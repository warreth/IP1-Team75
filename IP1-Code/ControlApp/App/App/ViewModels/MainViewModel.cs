using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using App.Services;

namespace App.ViewModels;

public partial class MainViewModel : ViewModelBase
{
    [ObservableProperty]
    private string imageServerUrl = "http://raspberrypi.local:8081/latest.png";

    [ObservableProperty]
    private string apiUrl = "https://raspberrypi.local:8080";


    // Add properties for editing and saving settings
    [ObservableProperty]
    private string? editableApiUrl;

    [ObservableProperty]
    private string? editableImageUrl;

    [ObservableProperty]
    private bool imageVisible = true;

    [ObservableProperty]
    private bool editableImageVisible;

    [ObservableProperty]
    private bool logVisible = true;

    [ObservableProperty]
    private bool editableLogVisible;

    [ObservableProperty]
    private string newestImageUrl = "";

    public ObservableCollection<string> LogMessages { get; } = new ObservableCollection<string>();

    private readonly ApiService _apiService = new ApiService();

    public void Log(string message) //TODO: Make the logs scroll down when new log is added
    {
        if (message == null)
        {
            message = "[null log message]";
        }
        string logEntry = $"[{DateTime.Now:HH:mm:ss}] {message}";
        LogMessages.Add(logEntry);
    }

    [RelayCommand]
    private async Task RefreshImageAsync() //TODO: Fix image not showing up on mobile (prob issue with the asyncImageLoader library)
    {
        string? result = await _apiService.ContactUrlAsync(ApiUrl, "newest-url");

        if (string.IsNullOrEmpty(result) || result.Contains("Error"))
        {
            Log($"Refreshimage request failed: {result}");
            OnPropertyChanged(nameof(LogMessages));
            NewestImageUrl = ImageServerUrl;
            return;
        }
        NewestImageUrl = ImageServerUrl + result;
        Log($"Refreshimage result: {NewestImageUrl}");
        OnPropertyChanged(nameof(LogMessages));

    }

    [RelayCommand]
    private async Task StopHatchAsync()
    {
        string? result = await _apiService.ContactUrlAsync(ApiUrl, "stop-hatch");

        // Check if result is "true" or "false" before converting
        bool isOpen;
        if (result == "true" || result == "false")
        {
            isOpen = Convert.ToBoolean(result);
        }
        else
        {
            Log($"StopHatch request failed: unexpected response '{result}'");
            OnPropertyChanged(nameof(LogMessages));
            return;
        }
        result = isOpen ? "Hatch is now stopped" : "Hatch could not be stopped (see RPi logs)";
        Log($"StopHatch result: {result}");

        OnPropertyChanged(nameof(LogMessages));
    }

    [RelayCommand]
    private async Task ToggleDetectionAsync()
    {
        string? result = await _apiService.ContactUrlAsync(ApiUrl, "toggle-detection");

        if (result == "enabled")
        {
            Log("Detection is now enabled");
        }
        else if (result == "disabled")
        {
            Log("Detection is now disabled");
        }
        else
        {
            Log($"ToggleDetection request failed: unexpected response '{result}'");
            OnPropertyChanged(nameof(LogMessages));
            return;
        }
        OnPropertyChanged(nameof(LogMessages));
    }

    [RelayCommand]
    private async Task MoveHatchAsync()
    {
        string? result = await _apiService.ContactUrlAsync(ApiUrl, "move-hatch");

        // Check if result is "true" or "false" before converting
        bool isOpen;
        if (result == "true" || result == "false")
        {
            isOpen = Convert.ToBoolean(result);
        }
        else
        {
            Log($"Openhatch request failed: unexpected response '{result}'");
            OnPropertyChanged(nameof(LogMessages));
            return;
        }
        result = isOpen ? "Hatch is now open" : "Hatch is now closed";
        Log($"Openhatch result: {result}");

        OnPropertyChanged(nameof(LogMessages));
    }

    [RelayCommand]
    private async Task TakePictureAsync()
    {
        string? result = await _apiService.ContactUrlAsync(ApiUrl, "take-picture");

        // Check if result is "true" or "false" before converting
        bool isOpen;
        if (result == "true" || result == "false")
        {
            isOpen = Convert.ToBoolean(result);
        }
        else
        {
            Log($"TakePicture request failed: unexpected response '{result}'");
            OnPropertyChanged(nameof(LogMessages));
            return;
        }
        result = isOpen ? "Picture taken" : "Picture couldnt be taken (see RPi logs)";
        Log($"TakePicture result: {result}");

        OnPropertyChanged(nameof(LogMessages));
    }

    [RelayCommand]
    private void LoadSettings()
    {
        EditableApiUrl = ApiUrl;
        EditableImageUrl = ImageServerUrl;
        EditableImageVisible = ImageVisible;
        EditableLogVisible = LogVisible;
        Log("Loaded settings into editable fields");
    }

    [RelayCommand]
    private void ClearLogs()
    {
        LogMessages.Clear();
        Log("Cleared logs");
    }

    [RelayCommand]
    private void SaveSettings()
    {
        if (string.IsNullOrWhiteSpace(EditableApiUrl) || string.IsNullOrWhiteSpace(EditableImageUrl))
        {
            Log("API or Image URL cannot be empty");
            return;
        }

        ApiUrl = EditableApiUrl;
        ImageServerUrl = EditableImageUrl;
        ImageVisible = EditableImageVisible;
        LogVisible = EditableLogVisible;
        /*Log(
            $"Settings saved:\n" +
            $"  API URL      = {ApiUrl}\n" +
            $"  Image URL    = {ImageServerUrl}\n" +
            $"  Image Visible= {ImageVisible}\n" +
            $"  Log Visible  = {LogVisible}"
        );*/
    }

    partial void OnApiUrlChanged(string value)
    {
        if (string.IsNullOrEmpty(EditableApiUrl))
            EditableApiUrl = value;
    }

    partial void OnImageServerUrlChanged(string value)
    {
        if (string.IsNullOrEmpty(EditableImageUrl))
            EditableImageUrl = value;
    }

    public MainViewModel()
    {
        EditableApiUrl = ApiUrl;
        EditableImageUrl = ImageServerUrl;
        EditableImageVisible = ImageVisible;
        EditableLogVisible = LogVisible;
    }
}
