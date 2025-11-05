import machine

def set_led_brightness(led, brightness):
    led.freq(1000)
    led.duty_u16(brightness)