from machine import Pin, ADC
import uasyncio

lich_pin = Pin(32, Pin.IN)
adc = ADC(lich_pin)
adc.atten(ADC.ATTN_11DB)

async def lich():
    while True:
        adc_value = adc.read()
        print(f"Lich value: {adc_value}")
        await uasyncio.sleep(1)
