import machine

# Pin definities voor de LEDs
DAGLICHT_PIN = 13
BLOOMING_PIN = 14
INFRARED_PIN = 15

# Initialiseer de PWM voor elke LED
daglicht_led = machine.PWM(machine.Pin(DAGLICHT_PIN))
blooming_led = machine.PWM(machine.Pin(BLOOMING_PIN))
infrared_led = machine.PWM(machine.Pin(INFRARED_PIN))


blooming_led_brightness = 0
infrared_led_brightness = 0
daglicht_led_brightness = 0

# Manual override flag - when True, automatic cycle will not change lamp values
manual_override = False

def __set_led_brightness(led, brightness): # !Private! function to set brightness
    led.freq(1000)
    led.duty_u16(brightness)

def set_infrared_brightness(brightness):
    import rp3_coms
    global infrared_led_brightness
    infrared_led_brightness = brightness
    __set_led_brightness(infrared_led, infrared_led_brightness)
    rp3_coms.send_log(f"DEBUG: Infrared LED brightness set to: {infrared_led_brightness}", is_debug=True)

def set_blooming_brightness(brightness):
    import rp3_coms
    global blooming_led_brightness
    blooming_led_brightness = brightness
    __set_led_brightness(blooming_led, blooming_led_brightness)
    rp3_coms.send_log(f"DEBUG: Blooming LED brightness set to: {blooming_led_brightness}", is_debug=True)

def set_daglicht_brightness(brightness):
    import rp3_coms
    global daglicht_led_brightness
    daglicht_led_brightness = brightness
    __set_led_brightness(daglicht_led, daglicht_led_brightness)
    rp3_coms.send_log(f"DEBUG: Daglicht LED brightness set to: {daglicht_led_brightness}", is_debug=True)

def return_led_brightness():
    return (daglicht_led_brightness, blooming_led_brightness, infrared_led_brightness)

def set_manual_override(enabled):
    global manual_override
    manual_override = enabled

def is_manual_override():
    return manual_override