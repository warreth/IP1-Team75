import machine
import uasyncio
import vochtigheid
import lampen
import planten_licht
import pomp
import planten_water
import lcd
import rp3_coms
import utime as time

# Monkey-patch rp3_coms to prevent infinite feedback loop
# The RPi3 echoes logs, causing the Pico to read them as invalid commands and log errors, creating a loop.
_original_send_log = rp3_coms.send_log
def _safe_send_log(msg, is_debug=False):
    # Filter out the error messages that cause the loop
    if isinstance(msg, str) and (msg.startswith("Received non-JSON data") or msg.startswith("Error receiving data")):
        return
    _original_send_log(msg, is_debug)
rp3_coms.send_log = _safe_send_log

# Enable/Disable debug logging
rp3_coms.debug_on = False

 # Init de LED's en pomp
'''
led_ch4 = machine.PWM(machine.Pin(15))
led_ch3 = machine.PWM(machine.Pin(14))
led_ch2 = machine.PWM(machine.Pin(13))
pomp_ch1 = machine.PWM(machine.Pin(12))
'''

#! source for async func: https://forums.raspberrypi.com/viewtopic.php?t=342824

async def main():
    #! IMPORTANT: Both run_planten_water and licht_cyclus MUST be defined as 'async def'
    # and use 'await uasyncio.sleep()' instead of 'time.sleep()'.
    # If run_planten_water is a normal function with a loop, it will block here forever.


    # Schedule tasks to run concurrently
    uasyncio.create_task(planten_water.run_planten_water())
    uasyncio.create_task(planten_licht.licht_cyclus())
    uasyncio.create_task(lcd.run_lcd_loop())
    uasyncio.create_task(rp3_coms.run_coms())
    
    # Keep the main loop alive so background tasks can run
    while True:
        await uasyncio.sleep(10)

if __name__ == '__main__':
    try:
        uasyncio.run(main())
    except KeyboardInterrupt:
        rp3_coms.send_log("Program stopped by user.")
    # lcd.start_lcd_display(60, "test")

