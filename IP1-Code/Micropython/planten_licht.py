import machine
import time
import uasyncio
import lampen
import lcd
import timer_manager

lcdOn = False #! Control LCD usage (good for debugging without LCD)

# Maximale helderheid (65535 is 100% duty cycle)
MAX_BRIGHTNESS = 65535
OFF = 0

# Duur van de lichtcyclus
HOOFDLICHT_AAN_UUR = 14
INFRAROOD_AAN_UUR = 1
TOTAAL_UUR_PER_DAG = 24
UUR_IN_SECONDE = 3600 # Voor testen kan dit verkort worden, bv. naar 1

def get_huidige_tijd_string():
    """Helper functie om een geformatteerde tijd string te krijgen."""
    return f"Tijd: {time.ticks_ms() // 1000}s"

async def licht_cyclus():
    """
    Regelt de dagelijkse lichtcyclus voor de planten.
    - Hoofdlicht (daglicht + blooming) staat 14 uur aan.
    - Daarna gaat het hoofdlicht uit en het infraroodlicht 1 uur aan.
    - De resterende 9 uur zijn alle lichten uit.
    """
    print(f"[{get_huidige_tijd_string()}] Lichtcyclus gestart.")
    while True:
        # --- HOOFDLICHT FASE ---
        print(f"[{get_huidige_tijd_string()}] Hoofdlicht AAN voor {HOOFDLICHT_AAN_UUR} uur.")
        if lcdOn: lcd.stop_lcd_display()
        if lcdOn: lcd.start_lcd_display(HOOFDLICHT_AAN_UUR*60, "HOOFDLICHT")
        lampen.set_daglicht_brightness(MAX_BRIGHTNESS)
        lampen.set_blooming_brightness(MAX_BRIGHTNESS)
        lampen.set_infrared_brightness(OFF) # Zorg dat infrarood uit is
        
        timer_manager.start_timer(HOOFDLICHT_AAN_UUR*UUR_IN_SECONDE, "HOOFDLICHT")
        await uasyncio.sleep(HOOFDLICHT_AAN_UUR * UUR_IN_SECONDE)
        
        # --- INFRAROOD FASE ---
        print(f"[{get_huidige_tijd_string()}] Hoofdlicht UIT.")
        if lcdOn: lcd.stop_lcd_display()
        if lcdOn: lcd.start_lcd_display(INFRAROOD_AAN_UUR*60, "INFRAROOD")
        lampen.set_daglicht_brightness(OFF)
        lampen.set_blooming_brightness(OFF)
        print(f"[{get_huidige_tijd_string()}] Infraroodlicht AAN voor {INFRAROOD_AAN_UUR} uur.")
        lampen.set_infrared_brightness(MAX_BRIGHTNESS)

        timer_manager.start_timer(INFRAROOD_AAN_UUR*UUR_IN_SECONDE, "INFRAROOD")
        await uasyncio.sleep(INFRAROOD_AAN_UUR * UUR_IN_SECONDE)


        # --- DONKERE FASE ---
        uren_uit = TOTAAL_UUR_PER_DAG - HOOFDLICHT_AAN_UUR - INFRAROOD_AAN_UUR
        if lcdOn: lcd.stop_lcd_display()
        if lcdOn: lcd.start_lcd_display(uren_uit*60, "DONKER")
        print(f"[{get_huidige_tijd_string()}] Alle lichten UIT voor {uren_uit} uur.")
        lampen.set_infrared_brightness(OFF)

        timer_manager.start_timer(uren_uit*UUR_IN_SECONDE, "DONKER")
        await uasyncio.sleep(uren_uit * UUR_IN_SECONDE)
        print(f"[{get_huidige_tijd_string()}] Einde donkere fase. Nieuwe cyclus start.")

# Start cyclus als test
# if __name__ == '__main__':
#     licht_cyclus()

