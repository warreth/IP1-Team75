import machine
import utime
import vochtigheid
import lampen

 # Init de LED's en pomp
led_ch4 = machine.PWM(machine.Pin(15))
led_ch3 = machine.PWM(machine.Pin(14))
led_ch2 = machine.PWM(machine.Pin(13))
pomp_ch1 = machine.PWM(machine.Pin(12))

# Main code
lampen.set_led_brightness(led_ch4, 60000)
lampen.set_led_brightness(led_ch3, 60000)
lampen.set_led_brightness(led_ch2, 60000)
print("LED's op maximale helderheid gezet.")

vochtigheid_percentage = vochtigheid.read_vochtigheid()
print(f"Vochtigheidspercentage: {vochtigheid_percentage}%")