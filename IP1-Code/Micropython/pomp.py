import machine


pomp_ch1 = machine.PWM(machine.Pin(12))
pomp_speed = 0

# Manual override flag - when True, automatic cycle will not change pump values
manual_override = False

def get_pomp_speed():
    global pomp_speed
    return pomp_speed

def set_pomp_speed(speed: int):
    import rp3_coms
    global pomp_speed
    pomp_speed = speed
    
    pomp_ch1.freq(1000)
    pomp_ch1.duty_u16(pomp_speed)
    rp3_coms.send_log(f"DEBUG: Pomp snelheid ingesteld op: {pomp_speed}", is_debug=True)

def set_manual_override(enabled):
    global manual_override
    manual_override = enabled

def is_manual_override():
    return manual_override
