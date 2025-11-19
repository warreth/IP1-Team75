import machine
import uasyncio
import vochtigheid
import lampen
import planten_licht
import pomp
import planten_water
import lcd
 # Init de LED's en pomp

'''
led_ch4 = machine.PWM(machine.Pin(15))
led_ch3 = machine.PWM(machine.Pin(14))
led_ch2 = machine.PWM(machine.Pin(13))
pomp_ch1 = machine.PWM(machine.Pin(12))
'''

#! source for async func: https://forums.raspberrypi.com/viewtopic.php?t=342824

async def start():
    #! IMPORTANT: Both run_planten_water and licht_cyclus MUST be defined as 'async def'
    # and use 'await uasyncio.sleep()' instead of 'time.sleep()'.
    # If run_planten_water is a normal function with a loop, it will block here forever.
    
    # Schedule tasks to run concurrently
    uasyncio.create_task(planten_water.run_planten_water())
    uasyncio.create_task(planten_licht.licht_cyclus())
    
    # Keep the main loop alive so background tasks can run
    while True:
        await uasyncio.sleep(10)

if __name__ == '__main__':
    try:
        uasyncio.run(start())
    except KeyboardInterrupt:
        print("Program stopped by user.")
    # lcd.start_lcd_display(60, "test")

