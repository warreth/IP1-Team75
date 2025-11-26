#!/usr/bin/env bash

# Set locale to UTF-8 to avoid Qt/locale warnings
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"

# Error checking: Ensure required commands are available
for cmd in dotnet sshpass scp ssh konsole; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: Required command '$cmd' not found. Please install it."
        exit 1
    fi
done

# Dynamically determine the project folder name from the current working directory (where the script is run)
project_dir="$(pwd)"
projectName="$(basename "$project_dir")"
project_path="."

# Error checking: Ensure projectName is not empty
if [[ -z "$projectName" ]]; then
    echo "Error: Could not determine project folder name."
    exit 1
fi

# Set remote deployment variables before use, always using the variable for the directory name
remote_user="w"
remote_host="ip75-pi3.netbird.cloud"
remote_path="~/$projectName"

# Parse optional -u argument for remote_host
while getopts "u:" opt; do
    case $opt in
        u)
            remote_host="$OPTARG"
            ;;
    esac
done

# Error checking: Ensure remote variables are not empty
if [[ -z "$remote_user" || -z "$remote_host" || -z "$remote_path" ]]; then
    echo "Error: One or more remote deployment variables are empty."
    exit 1
fi

# Step 0: Ping the remote host to check if it is up before proceeding
# Use 1 ping attempt, wait max 2 seconds, and suppress output
if ping -c 1 -W 2 "$remote_host" >/dev/null 2>&1; then
    echo "Device is up: $remote_host is reachable."
else
    echo "Device is down: $remote_host is unreachable."
    exit 1
fi

# Step 1: Publish the .NET project for Raspberry Pi 4 (linux-arm64) as a single file
# Use --runtime linux-arm64 and -p:PublishSingleFile=true for ARM64 single-file output
publish_output=$(dotnet publish "$project_path" --configuration Release --runtime linux-arm64 -o "$project_path/bin/Release/publish" 2>&1) #-p:PublishSingleFile=true
publish_status=$?

# Check if publish succeeded by exit status only
if [[ $publish_status -eq 0 ]]; then
    echo "dotnet publish succeeded."
else
    echo "$publish_output"
    echo "Error: dotnet publish failed."
    exit 1
fi

# Define the publish directory
publish_dir="$project_path/bin/Release/publish"

# Error checking: Ensure publish_dir exists and is not empty
if [[ ! -d "$publish_dir" || -z $(ls -A "$publish_dir") ]]; then
    echo "Error: publish_dir $publish_dir does not exist or is empty."
    exit 1
fi

# Prompt for SSH password once and store it securely in a variable
# This must come before any SSH or SCP operation
read -rsp "Enter SSH password: " ssh_password
echo

# Step 2: Remove the entire remote directory and its contents using sudo (do not recreate it)
# Keep token.json and log.md by moving them out before deletion and restoring them after
keep_files=("token.json" "apiKey.json" "log.md")

ssh_keep_cmd="sshpass -p \"$ssh_password\" ssh $remote_user@$remote_host 'mkdir -p /tmp/smartpackagebox_keep;"
for file in "${keep_files[@]}"; do
  ssh_keep_cmd+=" if [ -f $remote_path/$file ]; then mv $remote_path/$file /tmp/smartpackagebox_keep/; fi;"
done
ssh_keep_cmd+="'"

ssh_keep_output=$(eval "$ssh_keep_cmd" 2>&1)
ssh_keep_status=$?
if [[ $ssh_keep_status -ne 0 ]]; then
  echo "Error: Failed to move files to temporary location. Output was:"
  echo "$ssh_keep_output"
  exit 1
fi

ssh_remove_cmd="sshpass -p \"$ssh_password\" ssh $remote_user@$remote_host 'echo $ssh_password | sudo -S rm -rf $remote_path'"
ssh_remove_output=$(eval "$ssh_remove_cmd" 2>&1)
ssh_remove_status=$?
if [[ $ssh_remove_status -ne 0 ]]; then
  echo "Error: Failed to remove remote directory. Output was:"
  echo "$ssh_remove_output"
  exit 1
fi

echo "Remote directory removed."


# Step 2b: Recreate the remote directory before copying files
# Use bash -c to ensure ~ is expanded to the user's home directory on the remote side
ssh_create_cmd="sshpass -p \"$ssh_password\" ssh $remote_user@$remote_host 'bash -c \"mkdir -p $remote_path\"'"
ssh_create_output=$(eval "$ssh_create_cmd" 2>&1)
ssh_create_status=$?
if [[ $ssh_create_status -ne 0 ]]; then
    echo "Error: Failed to create remote directory. Output was:"
    echo "$ssh_create_output"
    exit 1
fi

echo "Remote directory created."


# Step 3: Copy published files to Raspberry Pi using tar + pv + ssh for a simple progress bar
# This will show a minimal progress bar (e.g., ----->) like yay/apt
# Error checking: Ensure pv is installed
if ! command -v pv >/dev/null 2>&1; then
    echo "Error: Required command 'pv' not found. Please install it."
    exit 1
fi

# Calculate total size for progress bar
publish_size=$(du -sb "$publish_dir" | awk '{print $1}')
if [[ -z "$publish_size" || "$publish_size" -eq 0 ]]; then
    echo "Error: Could not determine publish directory size."
    exit 1
fi

# Use tar + pv + ssh to transfer and extract with a simple progress bar
# The bar will look like: [=====>   ] 50%
sshpass -p "$ssh_password" tar -C "$publish_dir" -cf - . \
    | pv -s "$publish_size" -pterb \
    | sshpass -p "$ssh_password" ssh $remote_user@$remote_host "bash -c 'tar -C \"$HOME/$projectName\" -xf -'"

# Error checking: Check exit status of the last command in the pipeline
if [[ ${PIPESTATUS[2]} -ne 0 || ${PIPESTATUS[0]} -ne 0 ]]; then
    echo "Error: File transfer or extraction failed."
    exit 1
fi

echo "Files successfully copied to Raspberry Pi."
# Step 4: Prompt user to start SSH session in current terminal (y/n)
while true; do
    read -rp $"Do you want to start an SSH session to $remote_user@$remote_host? (y/n): " yn
    case "$yn" in
        [Yy]*)
            break
            ;;
        [Nn]*)
            echo "Skipping SSH session."
            exit 0
            ;;
        *)
            echo "Please answer y or n."
            ;;
    esac
done

# Open SSH session directly in current terminal with a normal shell experience
# -t forces pseudo-terminal allocation for interactivity
sshpass -p "$ssh_password" ssh -t "$remote_user@$remote_host" "cd $remote_path; exec \$SHELL"

# Print completion message after SSH session ends
if [[ $? -eq 0 ]]; then
    echo "SSH session ended. Deployment and testing complete."
else
    echo "Error: SSH session failed."
fi
