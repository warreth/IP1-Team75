import time
import uasyncio
import pomp
import vochtigheid
import rp3_coms

async def run_planten_water():
    """
    Automatic watering cycle that respects manual override.
    """
    while True:
        # Skip automatic pump control if manual override is active
        if pomp.is_manual_override():
            rp3_coms.send_log("DEBUG: Manual override active, skipping automatic pump control.", is_debug=True)
            await uasyncio.sleep(10)
            continue
            
        vochtigheid_waarde = vochtigheid.read_vochtigheid()
        rp3_coms.send_log(f"DEBUG: Huidige vochtigheid: {vochtigheid_waarde}%", is_debug=True)

        if vochtigheid_waarde < 40:
            rp3_coms.send_log("Vochtigheid laag, pomp aanzetten.")
            pomp.set_pomp_speed(30000)

            await uasyncio.sleep(10)
            pomp.set_pomp_speed(0)
            rp3_coms.send_log("Pomp uitgezet.")
        else:
            rp3_coms.send_log("DEBUG: Vochtigheid is voldoende, geen actie nodig.", is_debug=True)

        # Wacht 10min
        #await uasyncio.sleep(600)
        await uasyncio.sleep(10)