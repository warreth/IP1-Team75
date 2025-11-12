from machine import I2C, Pin
from time import sleep
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
        lcd.print("UGent \n")
        lcd.print("elektronica-ICT")
        time.sleep(2)
        
        lcd.clear()
        water_vochtigheid = vochtigheid.read_vochtigheid()
        duratie = duratie_current_cycle - (time.time() - teller)/60
        minuten = round(duratie)
        uren = minuten // 60
        minuten = minuten % 60
        lcd.print(f"H20 {water_vochtigheid:.1d} % \n")  # Print integer
        lcd.print(f"{uren} uren en {minuten} min ")
        time.sleep(2)
    lcd.print()

def stop_lcd_display():
    lcd = init_lcd()
    global keep_going
    keep_going = False

    lcd.clear()
    lcd.backlight_off()