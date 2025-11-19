import time
import uasyncio
import pomp
import vochtigheid

async def run_planten_water():
    while True:
        vochtigheid_waarde = vochtigheid.read_vochtigheid()
        print("DEBUG: Huidige vochtigheid: ", vochtigheid_waarde, "%")

        if vochtigheid_waarde < 40:
            print("Vochtigheid laag, pomp aanzetten.")
            pomp.set_pomp_speed(30000)

            await uasyncio.sleep(10)
            pomp.set_pomp_speed(0) # Zet de pomp uit
            print("Pomp uitgezet.")
        else:
            print("DEBUG: Vochtigheid is voldoende, geen actie nodig.")

        # Wacht 10min
        #await uasyncio.sleep(600)
        await uasyncio.sleep(10)  # Voor testen, verkort naar 10 seconden