import machine


pomp_ch1 = machine.PWM(machine.Pin(12))
pomp_speed = 0 # Initialize global variable

def get_pomp_speed():
    global pomp_speed
    return pomp_speed

def set_pomp_speed(speed: int):
    global pomp_speed
    pomp_speed = speed
    
    pomp_ch1.freq(1000)
    pomp_ch1.duty_u16(pomp_speed)
    print("DEBUG: Pomp snelheid ingesteld op:", pomp_speed)
