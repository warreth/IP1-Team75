from machine import Pin
import time

led_ch1 = Pin(10, Pin.OUT)
led_ch2 = Pin(11, Pin.OUT)
led_ch3 = Pin(12, Pin.OUT)

x = 0.5

led_ch1.value(0)
led_ch2.value(0)
led_ch3.value(0)

while True:
    # CH1 aan, rest uit
    led_ch1.value(1)
    led_ch2.value(0)
    led_ch3.value(0)
    time.sleep(x)
    
    # CH2 aan, rest uit
    led_ch1.value(0)
    led_ch2.value(1)
    led_ch3.value(0)
    time.sleep(x)
    
    # CH3 aan, rest uit
    led_ch1.value(0)
    led_ch2.value(0)
    led_ch3.value(1)
    time.sleep(x)