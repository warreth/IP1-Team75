# Project objectives: 
#   Print a "Hello world!" text on the LCD screen to test its functionality
#   Learn how to use I2C communication between the LCD and Raspberry Pi Pico
#   Get familiarized with the pico_i2c_lcd and lcd_api modules
#
# Hardware and connections used:
#   LCD GND Pin to Raspberry Pi Pico GND
#   LCD VCC Pin to Raspberry Pi Pico VBUS 
#   (Note: VBUS is only to be used as power for the screen. 
#   It can't be used as power for the entire circuit if there are other components interfaced.)
#   LCD SDA Pin to Raspberry Pi Pico GPIO Pin 0
#   LCD SCL Pin to Raspberry Pi Pico GPIO Pin 1
#
# Programmer: Adrian Josele G. Quional

# modules
from machine import I2C, Pin    # since I2C communication would be used, I2C class is imported
from time import sleep
import time

# very important
# this module needs to be saved in the Raspberry Pi Pico in order for the LCD I2C to be used 
from pico_i2c_lcd import I2cLcd

# creating an I2C object, specifying the data (SDA) and clock (SCL) pins used in the Raspberry Pi Pico
# any SDA and SCL pins in the Raspberry Pi Pico can be used (check documentation for SDA and SCL pins)
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# getting I2C address
I2C_ADDR = i2c.scan()[0]

# creating an LCD object using the I2C address and specifying number of rows and columns in the LCD
# LCD number of rows = 2, number of columns = 16
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

# continuously print and clear "Hello world!" text in the LCD screen while the board has power
while True:
    lcd.clear()
    lcd.putstr("UGent \n")
    lcd.putstr("elektronica-ICT")
    time.sleep(2)
    
    lcd.clear()
    water_vochtigheid = 51
    duratie = 375
    minuten = round(duratie)
    uren = minuten // 60
    minuten = minuten % 60
    lcd.putstr(f"H20 {water_vochtigheid:.1d} % \n")  # Print integer
    lcd.putstr(f"{uren}u en {minuten}min")
    time.sleep(2)