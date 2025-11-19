"""
This Raspberry Pi Pico MicroPython code was developed by newbiely.com
This Raspberry Pi Pico code is made available for public use without any restriction
For comprehensive instructions and wiring diagrams, please visit:
https://newbiely.com/tutorials/raspberry-pico/raspberry-pi-pico-lcd-i2c
"""

from machine import I2C, Pin
from time import sleep
import time
import utime
sleep(1)
from DIYables_MicroPython_LCD_I2C import LCD_I2C
import math




# The I2C address of your LCD (Update if different)
I2C_ADDR = 0x27  # Use the address found using the I2C scanner

# Define the number of rows and columns on your LCD
LCD_ROWS = 2
LCD_COLS = 16

# Initialize I2C
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)

# getting I2C address
I2C_ADDR = i2c.scan()[0]
print(hex(I2C_ADDR))

# Initialize LCD
lcd = LCD_I2C(i2c, I2C_ADDR, LCD_ROWS, LCD_COLS)

# Setup function
lcd.backlight_on()
lcd.clear()
teller = time.time()
duratie_current_cycle = 14*60
naam_current_cycle = "HOOFDLICHT"
# Main loop function
while True:
    lcd.clear()
    lcd.set_cursor(5, 0) # Move the cursor to column 3, row 0 (first row)
    lcd.print("UGent")
    lcd.set_cursor(0, 1) # Move the cursor to column 0, row 1 (second row)
    lcd.print("elektronica-ICT")
    utime.sleep(2)

    lcd.clear()
    water_vochtigheid = 74
    lcd.set_cursor(0, 0) # Move to the beginning of the first row
    lcd.print("Watervochtigheid")
    lcd.set_cursor(0, 1)  # Move to the beginning of the second row
    lcd.print(f"{water_vochtigheid}%")
    utime.sleep(2)

    lcd.clear()
    duratie = duratie_current_cycle - (time.time() - teller)/60
    minuten = math.ceil(duratie) - 1
    uren = minuten // 60
    minuten = minuten % 60
    lcd.set_cursor(0, 0) # Move to the beginning of the first row
    lcd.print(f'{naam_current_cycle}')
    lcd.set_cursor(0, 1) # Move to the beginning of the first row
    lcd.print(f"{uren} : {minuten} over")
    utime.sleep(2)
lcd.print()
