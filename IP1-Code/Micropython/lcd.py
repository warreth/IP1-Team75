from machine import I2C, Pin
from time import sleep
import utime
import time
import uasyncio
from DIYables_MicroPython_LCD_I2C import LCD_I2C
import vochtigheid
import timer_manager
import math

_lcd_active = False # Control LCD display state
_lcd_instance = None # LCD instance (to make sure only one instance exists)

def init_lcd():
    I2C_ADDR = 0x27  # Adress van de I2C
    # Aantal rijen en kolommen van de lcd
    LCD_ROWS = 2
    LCD_COLS = 16
    # Initialize I2C
    i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100000) #de data staat op pin 4 en de klok op pin 5
    # start LCD
    lcd = LCD_I2C(i2c, I2C_ADDR, LCD_ROWS, LCD_COLS)
    lcd.backlight_on()
    lcd.clear()
    return lcd

async def run_lcd_loop():
    global _lcd_active, _lcd_instance
    
    try:
        _lcd_instance = init_lcd()
    except Exception as e:
        print(f"LCD Init Error: {e}")
        
    while True:
        if _lcd_active:
            if _lcd_instance is None:
                try:
                    #print("Attempting to re-initialize LCD...")
                    _lcd_instance = init_lcd()
                except Exception as e:
                    #print(f"LCD Re-init Error: {e}")
                    await uasyncio.sleep(5)
                    continue

            try:
                _lcd_instance.clear()
                _lcd_instance.set_cursor(5, 0) # Move the cursor to column 3, row 0 (first row)
                _lcd_instance.print("UGent")
                _lcd_instance.set_cursor(0, 1) # Move the cursor to column 0, row 1 (second row)
                _lcd_instance.print("elektronica-ICT")
                await uasyncio.sleep(2)
                
                if not _lcd_active: continue

                _lcd_instance.clear()
                water_vochtigheid = vochtigheid.read_vochtigheid()
                _lcd_instance.set_cursor(0, 0) # Move to the beginning of the first row
                _lcd_instance.print(f"Watervochtigheid")
                _lcd_instance.set_cursor(0, 1)  # Move to the beginning of the second row
                _lcd_instance.print(f"{water_vochtigheid}%")
                await uasyncio.sleep(2)

                if not _lcd_active: continue

                _lcd_instance.clear()
                uren, minuten = timer_manager.get_remaining_time()
                naam_current_cycle = timer_manager.get_current_cycle()
                _lcd_instance.set_cursor(0, 0) # Move to the beginning of the first row
                _lcd_instance.print(f"{naam_current_cycle}")
                _lcd_instance.set_cursor(0, 1) # Move to the beginning of the first row
                _lcd_instance.print(f"{uren} : {minuten} over")
                await uasyncio.sleep(2)
            except Exception as e:
                print(f"LCD Loop Error: {e}")
                # Force re-initialization on error
                _lcd_instance = None
                await uasyncio.sleep(1)
        else:
            await uasyncio.sleep(1)

def start_lcd_display(duratie_cycle, naam_current_cycle):
    global _lcd_active
    _lcd_active = True


def stop_lcd_display():
    global _lcd_active, _lcd_instance
    _lcd_active = False

    try:
        if _lcd_instance:
            _lcd_instance.clear()
            _lcd_instance.backlight_off()
        else:
            lcd = init_lcd()
            lcd.clear()
            lcd.backlight_off()
    except:
        pass