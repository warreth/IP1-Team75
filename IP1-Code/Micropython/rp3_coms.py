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
# Added timeout to prevent blocking
uart = machine.UART(1, baudrate=9600, tx=machine.Pin(8), rx=machine.Pin(9), timeout=100)

debug_on = False

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
        
        # Send the string followed by a newline character
        # Explicitly encode to bytes for reliability
        uart.write(f"{json_str}\n".encode('utf-8'))
        
        # Yield control to allow other async tasks to run
        await uasyncio.sleep(0)
        
    except Exception as e:
        send_log(f"Error sending data: {e}")

async def send_status_update():
    print("Sending status update...")
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
        print(message) # Also print locally for debugging
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
    last_status_time = 0
    
    while True:
        current_time = utime.ticks_ms()
        
        # Send status update every 1000ms (1 second)
        if utime.ticks_diff(current_time, last_status_time) >= 1000:
            await send_status_update()
            last_status_time = current_time
        
        # Check for incoming commands (returns a dict or None)
        cmd_data = await receive_command()
        
        if cmd_data:
            # Extract command details safely
            cmd_name = cmd_data.get("command")
            cmd_value = cmd_data.get("value")
            
            # Only process if it is actually a command (has a 'command' key)
            # This filters out echoed status updates which are valid JSON but lack 'command'
            if cmd_name:
                send_log(f"Received command data: {cmd_data}")

                if cmd_name == "CHANGE_POMP_SPEED":
                    if cmd_value is not None:
                        try:
                            # Update pump speed
                            pomp.set_pomp_speed(int(cmd_value))
                            send_log(f"Pomp snelheid ingesteld op {cmd_value}.")
                        except Exception as e:
                            send_log(f"Error setting pump speed: {e}")
                    else:
                        send_log("Error: Value missing for CHANGE_POMP_SPEED")
                elif cmd_name == "SET_LAMP_DL_BRIGHTNESS": #daglicht
                    if cmd_value is not None:
                        try:
                            lampen.set_daglicht_brightness(int(cmd_value))
                            send_log(f"Daglicht helderheid ingesteld op {cmd_value}.")
                        except Exception as e:
                            send_log(f"Error setting daglicht brightness: {e}")
                    else:
                        send_log("Error: Value missing for SET_LAMP_DL_BRIGHTNESS")
                elif cmd_name == "SET_LAMP_BLOOM_BRIGHTNESS": #bloom
                    if cmd_value is not None:
                        try:
                            lampen.set_blooming_brightness(int(cmd_value))
                            send_log(f"Blooming helderheid ingesteld op {cmd_value}.")
                        except Exception as e:
                            send_log(f"Error setting blooming brightness: {e}")
                    else:
                        send_log("Error: Value missing for SET_LAMP_BLOOM_BRIGHTNESS")
                elif cmd_name == "SET_LAMP_IR_BRIGHTNESS": #infared
                    if cmd_value is not None:
                        try:
                            lampen.set_infared_brightness(int(cmd_value))
                            send_log(f"Infared helderheid ingesteld op {cmd_value}.")
                        except Exception as e:
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
                else:
                    send_log(f"Unknown command: {cmd_name}")
        
        # Short sleep to allow other tasks to run and prevent CPU hogging
        # This makes the loop run at ~10Hz, checking for commands frequently
        await uasyncio.sleep(0.1)


