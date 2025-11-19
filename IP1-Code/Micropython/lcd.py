from machine import I2C, Pin
from time import sleep
import utime
import time
sleep(1)
from DIYables_MicroPython_LCD_I2C import LCD_I2C
import vochtigheid
import planten_licht

def init_lcd():
    I2C_ADDR = 0x27  # Adress van de I2C
    # Aantal rijen en kolommen van de lcd
    LCD_ROWS = 2
    LCD_COLS = 16
    # Initialize I2C
    i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000) #de data staat op pin 4 en de klok op pin 5
    # start LCD
    lcd = LCD_I2C(i2c, I2C_ADDR, LCD_ROWS, LCD_COLS)
    lcd.backlight_on()
    lcd.clear()
    return lcd
    

def start_lcd_display(duratie_current_cycle, naam_current_cycle):
    lcd = init_lcd()
    global keep_going
    keep_going = True
    teller = time.time()

    while (keep_going==True):
        lcd.clear()
        lcd.set_cursor(5, 0) # Move the cursor to column 3, row 0 (first row)
        lcd.print("UGent")
        lcd.set_cursor(0, 1) # Move the cursor to column 0, row 1 (second row)
        lcd.print("elektronica-ICT")
        utime.sleep(2)
        
        lcd.clear()
        water_vochtigheid = vochtigheid.read_vochtigheid()
        lcd.set_cursor(0, 0) # Move to the beginning of the first row
        lcd.print("Watervochtigheid")
        lcd.set_cursor(0, 1)  # Move to the beginning of the second row
        lcd.print(f"{water_vochtigheid}%")
        utime.sleep(2)

        lcd.clear()
        duratie = duratie_current_cycle - (time.time() - teller)/60
        minuten = round(duratie)
        uren = minuten // 60
        minuten = minuten % 60
        lcd.set_cursor(0, 0) # Move to the beginning of the first row
        lcd.print({naam_current_cycle})
        lcd.set_cursor(0, 1) # Move to the beginning of the first row
        lcd.print(f"{uren} : {minuten} over")
        utime.sleep(2)
    lcd.print()

def stop_lcd_display():
    lcd = init_lcd()
    global keep_going
    keep_going = False

    lcd.clear()
    lcd.backlight_off()