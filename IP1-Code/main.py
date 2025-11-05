import machine
import utime
import vochtigheid
import lampen
import planten_licht

 # Init de LED's en pomp
"""" 
    led_ch4 = machine.PWM(machine.Pin(15))
    led_ch3 = machine.PWM(machine.Pin(14))
    led_ch2 = machine.PWM(machine.Pin(13))
    pomp_ch1 = machine.PWM(machine.Pin(12))
"""
# Main code
if __name__ == '__main__':
    planten_licht.licht_cyclus()