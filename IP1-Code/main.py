import machine
import utime

led_ch4 = machine.PWM(machine.Pin(15))
led_ch3 = machine.PWM(machine.Pin(14))
led_ch2 = machine.PWM(machine.Pin(13))
pomp_ch1 = machine.PWM(machine.Pin(12))


def set_led_brightness(led, brightness):
    led.freq(1000)
    led.duty_u16(brightness)

a=0
while True:
    set_led_brightness(led_ch2, 0000) 
    set_led_brightness(led_ch3, 0000)
    set_led_brightness(led_ch4, 60000)
    utime.sleep(1000)
    