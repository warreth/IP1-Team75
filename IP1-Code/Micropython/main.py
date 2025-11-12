import machine
import utime
import vochtigheid
import lampen
import planten_licht
import pomp
import planten_water
import _thread
import lcd
 # Init de LED's en pomp

'''
led_ch4 = machine.PWM(machine.Pin(15))
led_ch3 = machine.PWM(machine.Pin(14))
led_ch2 = machine.PWM(machine.Pin(13))
pomp_ch1 = machine.PWM(machine.Pin(12))
'''
# Main code

if __name__ == '__main__':
    pomp.set_pomp_speed(0)  # Zet de pomp uit bij start

    planten_licht.licht_cyclus()
    _thread.start_new_thread(planten_water.run_planten_water(), ())
    
      
#lcd.start_lcd_display(60, "test")