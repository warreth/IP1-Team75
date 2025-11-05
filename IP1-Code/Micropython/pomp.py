import machine


pomp_ch1 = machine.PWM(machine.Pin(12))

def set_pomp_speed(speed):
    pomp_ch1.freq(1000)
    pomp_ch1.duty_u16(speed)