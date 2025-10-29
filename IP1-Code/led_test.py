import machine
import time

led_ch1 = machine.PWM(machine.Pin(2))
led_ch2 = machine.PWM(machine.Pin(3))
led_ch3 = machine.PWM(machine.Pin(12))



def set_led_brightness(led, brightness):
    led.duty_u16(brightness)



set_led_brightness(led_ch1, 60000)
