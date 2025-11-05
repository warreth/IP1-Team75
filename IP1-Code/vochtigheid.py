from machine import ADC, Pin

def read_vochtigheid():
    sensor = ADC(Pin(28))  # Assuming the sensor is connected to GPIO 26 (ADC0)
    vochtigheid_waarde = sensor.read_u16()
    print("DEBUG: Vochtigheid waarde:", vochtigheid_waarde)