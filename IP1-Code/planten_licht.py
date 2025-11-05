import machine
import time
from lampen import set_led_brightness

# Pin definities voor de LEDs (pas aan naar de juiste GPIO pinnen)
DAGLICHT_PIN = 13
BLOOMING_PIN = 14
INFRARED_PIN = 15

# Initialiseer de PWM voor elke LED
led_daglicht = machine.PWM(machine.Pin(DAGLICHT_PIN))
led_blooming = machine.PWM(machine.Pin(BLOOMING_PIN))
led_infrared = machine.PWM(machine.Pin(INFRARED_PIN))

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

def licht_cyclus():
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
        set_led_brightness(led_daglicht, MAX_BRIGHTNESS)
        set_led_brightness(led_blooming, MAX_BRIGHTNESS)
        set_led_brightness(led_infrared, OFF) # Zorg dat infrarood uit is
        
        time.sleep(HOOFDLICHT_AAN_UUR * UUR_IN_SECONDE)
        
        # --- INFRAROOD FASE ---
        print(f"[{get_huidige_tijd_string()}] Hoofdlicht UIT.")
        set_led_brightness(led_daglicht, OFF)
        set_led_brightness(led_blooming, OFF)
        
        print(f"[{get_huidige_tijd_string()}] Infraroodlicht AAN voor {INFRAROOD_AAN_UUR} uur.")
        set_led_brightness(led_infrared, MAX_BRIGHTNESS)
        
        time.sleep(INFRAROOD_AAN_UUR * UUR_IN_SECONDE)

        # --- DONKERE FASE ---
        uren_uit = TOTAAL_UUR_PER_DAG - HOOFDLICHT_AAN_UUR - INFRAROOD_AAN_UUR
        print(f"[{get_huidige_tijd_string()}] Alle lichten UIT voor {uren_uit} uur.")
        set_led_brightness(led_infrared, OFF)
        
        time.sleep(uren_uit * UUR_IN_SECONDE)
        print(f"[{get_huidige_tijd_string()}] Einde donkere fase. Nieuwe cyclus start.")

# Om de cyclus te starten, roep je de functie aan in je main.py
# if __name__ == '__main__':
#     licht_cyclus()
