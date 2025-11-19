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
uart = machine.UART(0, baudrate=115200, tx=machine.Pin(0), rx=machine.Pin(1))


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
        uart.write(f"{json_str}\n")
        
        # Yield control to allow other async tasks to run
        await uasyncio.sleep(0)
        
    except Exception as e:
        print(f"Error sending data: {e}")

def send_log(message):
    """
    Sends a log message to the RPi4 via UART.
    """
    try:
        # Send the log message prefixed with LOG:
        uart.write(f"LOG:{message}\n")
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
                
                try:
                    # Parse JSON string into a dictionary
                    # Expected format: {"command": "NAME", "value": 123}
                    return ujson.loads(command_str)
                except ValueError:
                    send_log(f"Received non-JSON data: {command_str}")
                    return None
                
    except Exception as e:
        send_log(f"Error receiving data: {e}")
        
    return None

async def run_coms():
    """
    Async loop to handle communication with RPi4.
    """
    while True:
        # Check for incoming commands (returns a dict or None)
        cmd_data = await receive_command()
        
        if cmd_data:
            send_log(f"Received command data: {cmd_data}")
            
            # Extract command details safely
            cmd_name = cmd_data.get("command")
            cmd_value = cmd_data.get("value")
            
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
            if cmd_name == "SET_LAMP_DL_BRIGHTNESS": #daglicht
                if cmd_value is not None:
                    try:
                        lampen.set_daglicht_brightness(int(cmd_value))
                        send_log(f"Daglicht helderheid ingesteld op {cmd_value}.")
                    except Exception as e:
                        send_log(f"Error setting daglicht brightness: {e}")
                else:
                    send_log("Error: Value missing for SET_LAMP_DL_BRIGHTNESS")
            if cmd_name == "SET_LAMP_BLOOM_BRIGHTNESS": #bloom
                if cmd_value is not None:
                    try:
                        lampen.set_blooming_brightness(int(cmd_value))
                        send_log(f"Blooming helderheid ingesteld op {cmd_value}.")
                    except Exception as e:
                        send_log(f"Error setting blooming brightness: {e}")
                else:
                    send_log("Error: Value missing for SET_LAMP_BLOOM_BRIGHTNESS")
            if cmd_name == "SET_LAMP_IR_BRIGHTNESS": #infared
                if cmd_value is not None:
                    try:
                        lampen.set_infared_brightness(int(cmd_value))
                        send_log(f"Infared helderheid ingesteld op {cmd_value}.")
                    except Exception as e:
                        send_log(f"Error setting infared brightness: {e}")
                else:
                    send_log("Error: Value missing for SET_LAMP_IR_BRIGHTNESS")
            else:
                send_log(f"Unknown command: {cmd_name}")
        
        # Send status update with sensor values
        vochtigheid_waarde = vochtigheid.read_vochtigheid()
        pomp_snelheid = pomp.get_pomp_speed()
        DaglichtBR, bloomingBR, infaredBR = lampen.return_led_brightness()
        current_uren, current_minuten = timer_manager.get_remaining_time()
        current_cycle = timer_manager.get_current_cycle()

        await send_status(vochtigheid_waarde, DaglichtBR, bloomingBR, infaredBR, pomp_snelheid, current_uren, current_minuten, current_cycle)
        
        # Wait 1 second before next update
        await uasyncio.sleep(1)


