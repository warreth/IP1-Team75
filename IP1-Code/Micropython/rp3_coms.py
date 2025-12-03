# Here we must communicate with the RP3 over data pins
import machine
import utime
import ujson
import uasyncio
import pomp
import vochtigheid
import lampen
import timer_manager

# Initialize UART (Serial) communication
# TX pin (e.g., GP0) connects to RX on RPi4
# RX pin (e.g., GP1) connects to TX on RPi4
# Lowered to 9600 for stability
uart = machine.UART(1, baudrate=9600, tx=machine.Pin(8), rx=machine.Pin(9))

debug_on = False
debug_print_on = True  # Set to False to disable debug print statements

def debug_print(message):
    """Print debug message if debug printing is enabled."""
    if debug_print_on:
        print(message)

async def send_status(humidity, lamp1_val, lamp2_val, lamp3_val, pump_speed, uren, minuten, cycle):
    """
    Sends the current status values to the RPi4 via UART as a JSON string.
    """
    try:
        # Create a dictionary with the data
        data = {
            "humidity": humidity,
            "lamp1": lamp1_val,
            "lamp2": lamp2_val,
            "lamp3": lamp3_val,
            "pump_speed": pump_speed,
            "uren": uren,
            "minuten": minuten,
            "cycle": cycle
        }
        
        # Convert dictionary to JSON string
        json_str = ujson.dumps(data)

        #print(f"Sending status: {json_str}")  # For debugging
        
        # Send the string followed by a newline character
        # Explicitly encode to bytes for reliability
        uart.write(f"{json_str}\n")
        
        # Yield control to allow other async tasks to run
        
    except Exception as e:
        send_log(f"Error sending data: {e}")

async def send_status_update():
    #print("Sending status update...")
    # Send status update with sensor values
    vochtigheid_waarde = vochtigheid.read_vochtigheid()
    pomp_snelheid = pomp.get_pomp_speed()
    DaglichtBR, bloomingBR, infaredBR = lampen.return_led_brightness()
    current_uren, current_minuten = timer_manager.get_remaining_time()
    current_cycle = timer_manager.get_current_cycle()

    await send_status(vochtigheid_waarde, DaglichtBR, bloomingBR, infaredBR, pomp_snelheid, current_uren, current_minuten, current_cycle)


def send_log(message, is_debug=False):
    """
    Sends a log message to the RPi4 via UART.
    """
    if is_debug and not debug_on:
        return

    try:
        # Send the log message prefixed with LOG:
        uart.write(f"LOG:{message}\n".encode('utf-8'))
        #print(message) # Also print locally for debugging
    except Exception as e:
        print(f"Error sending log: {e}")


async def receive_command():
    """
    Checks for incoming commands from the RPi4.
    Returns the command dictionary if available and valid JSON, otherwise None.
    """
    try:
        if uart.any():
            # Read line from UART
            command_bytes = uart.readline()
            
            if command_bytes:
                # Decode bytes to string and strip whitespace
                command_str = command_bytes.decode("utf-8").strip()
                
                # Yield control
                await uasyncio.sleep(0)
                
                # Ignore empty lines
                if not command_str:
                    return None

                # Prevent feedback loop: Ignore echoed log messages
                if command_str.startswith("LOG:"):
                    return None
                
                try:
                    # Parse JSON string into a dictionary
                    # Expected format: {"command": "NAME", "value": 123}
                    return ujson.loads(command_str)
                except ValueError:
                    send_log(f"Received non-JSON data: {command_str}")
                    return None
            else:
                return None
    except Exception as e:
        send_log(f"Error receiving data: {e}")
        
    return None

async def run_coms():
    """
    Async loop to handle communication with RPi4.
    """
    while True:
        await send_status_update()
        
        # Check for incoming commands (returns a dict or None)
        cmd_data = await receive_command()
        
        if cmd_data:
            # Extract command details safely
            cmd_name = cmd_data.get("command")
            cmd_value = cmd_data.get("value")
            
            # Only process if it is actually a command (has a 'command' key)
            # This filters out echoed status updates which are valid JSON but lack 'command'
            if cmd_name:
                debug_print(f"Processing command: {cmd_name} with value: {cmd_value}")
                send_log(f"Received command data: {cmd_data}")

                if cmd_name == "CHANGE_POMP_SPEED":
                    if cmd_value is not None:
                        try:
                            speed_val = int(cmd_value)
                            if speed_val == 0:
                                # Setting to 0 disables manual override and resumes automatic cycle
                                pomp.set_manual_override(False)
                                pomp.set_pomp_speed(0)
                                debug_print("Pump set to 0, manual override disabled")
                                send_log("Pomp op 0 gezet, automatische cyclus hervat.")
                            else:
                                # Enable manual override so automatic cycle doesn't overwrite
                                pomp.set_manual_override(True)
                                pomp.set_pomp_speed(speed_val)
                                debug_print(f"Pump speed set to {cmd_value}")
                                send_log(f"Pomp snelheid ingesteld op {cmd_value} (manual override enabled).")
                        except Exception as e:
                            debug_print(f"Pump error: {e}")
                            send_log(f"Error setting pump speed: {e}")
                    else:
                        send_log("Error: Value missing for CHANGE_POMP_SPEED")
                elif cmd_name == "SET_LAMP_DL_BRIGHTNESS":
                    if cmd_value is not None:
                        try:
                            brightness_val = int(cmd_value)
                            if brightness_val == 0:
                                # Check if all lamps are being set to 0, then disable override
                                lampen.set_daglicht_brightness(0)
                                # Disable override if all lamps are at 0
                                dl, bloom, ir = lampen.return_led_brightness()
                                if dl == 0 and bloom == 0 and ir == 0:
                                    lampen.set_manual_override(False)
                                    send_log("Alle lampen op 0, automatische cyclus hervat.")
                                else:
                                    send_log("Daglicht op 0 gezet.")
                            else:
                                # Enable manual override so automatic cycle doesn't overwrite
                                lampen.set_manual_override(True)
                                debug_print(f"Calling lampen.set_daglicht_brightness({cmd_value})")
                                lampen.set_daglicht_brightness(brightness_val)
                                debug_print(f"Daglicht brightness set to {cmd_value}")
                                send_log(f"Daglicht helderheid ingesteld op {cmd_value} (manual override enabled).")
                        except Exception as e:
                            debug_print(f"Daglicht error: {e}")
                            send_log(f"Error setting daglicht brightness: {e}")
                    else:
                        send_log("Error: Value missing for SET_LAMP_DL_BRIGHTNESS")
                elif cmd_name == "SET_LAMP_BLOOM_BRIGHTNESS":
                    if cmd_value is not None:
                        try:
                            brightness_val = int(cmd_value)
                            if brightness_val == 0:
                                # Check if all lamps are being set to 0, then disable override
                                lampen.set_blooming_brightness(0)
                                # Disable override if all lamps are at 0
                                dl, bloom, ir = lampen.return_led_brightness()
                                if dl == 0 and bloom == 0 and ir == 0:
                                    lampen.set_manual_override(False)
                                    send_log("Alle lampen op 0, automatische cyclus hervat.")
                                else:
                                    send_log("Blooming op 0 gezet.")
                            else:
                                # Enable manual override so automatic cycle doesn't overwrite
                                lampen.set_manual_override(True)
                                debug_print(f"Calling lampen.set_blooming_brightness({cmd_value})")
                                lampen.set_blooming_brightness(brightness_val)
                                debug_print(f"Blooming brightness set to {cmd_value}")
                                send_log(f"Blooming helderheid ingesteld op {cmd_value} (manual override enabled).")
                        except Exception as e:
                            debug_print(f"Blooming error: {e}")
                            send_log(f"Error setting blooming brightness: {e}")
                    else:
                        send_log("Error: Value missing for SET_LAMP_BLOOM_BRIGHTNESS")
                elif cmd_name == "SET_LAMP_IR_BRIGHTNESS":
                    if cmd_value is not None:
                        try:
                            brightness_val = int(cmd_value)
                            if brightness_val == 0:
                                # Check if all lamps are being set to 0, then disable override
                                lampen.set_infrared_brightness(0)
                                # Disable override if all lamps are at 0
                                dl, bloom, ir = lampen.return_led_brightness()
                                if dl == 0 and bloom == 0 and ir == 0:
                                    lampen.set_manual_override(False)
                                    send_log("Alle lampen op 0, automatische cyclus hervat.")
                                else:
                                    send_log("Infrared op 0 gezet.")
                            else:
                                # Enable manual override so automatic cycle doesn't overwrite
                                lampen.set_manual_override(True)
                                debug_print(f"Calling lampen.set_infared_brightness({cmd_value})")
                                lampen.set_infrared_brightness(brightness_val)
                                debug_print(f"Infared brightness set to {cmd_value}")
                                send_log(f"Infared helderheid ingesteld op {cmd_value} (manual override enabled).")
                        except Exception as e:
                            debug_print(f"Infared error: {e}")
                            send_log(f"Error setting infared brightness: {e}")
                    else:
                        send_log("Error: Value missing for SET_LAMP_IR_BRIGHTNESS")
                elif cmd_name == "SET_DEBUG":
                    if cmd_value is not None:
                        global debug_on
                        debug_on = bool(cmd_value)
                        send_log(f"Debug mode set to {debug_on}")
                    else:
                        send_log("Error: Value missing for SET_DEBUG")
                elif cmd_name == "DISABLE_LAMP_OVERRIDE":
                    # Disable lamp manual override to resume automatic cycle
                    lampen.set_manual_override(False)
                    send_log("Lamp manual override disabled, automatic cycle resumed.")
                elif cmd_name == "DISABLE_PUMP_OVERRIDE":
                    # Disable pump manual override to resume automatic cycle
                    pomp.set_manual_override(False)
                    send_log("Pump manual override disabled, automatic cycle resumed.")
                elif cmd_name == "DISABLE_ALL_OVERRIDES":
                    # Disable all manual overrides to resume automatic cycles
                    lampen.set_manual_override(False)
                    pomp.set_manual_override(False)
                    send_log("All manual overrides disabled, automatic cycles resumed.")
                else:
                    send_log(f"Unknown command: {cmd_name}")
        
        # Wait 1 second before next update
        await uasyncio.sleep(1)


