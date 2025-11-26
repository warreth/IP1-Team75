from machine import ADC, Pin

DRY_RAW = 52000 
WET_RAW = 25000 

ADC_PIN = 28 # Pin van de vochtigheidssensor

def _raw_to_percent(raw: int) -> int:
    # Convert raw ADC value to percentage; assumes the dry value is higher than wet.
    if DRY_RAW == WET_RAW:
        return 0
    percent = (DRY_RAW - raw) * 100.0 / (DRY_RAW - WET_RAW)
    if percent < 0:
        percent = 0
    elif percent > 100:
        percent = 100
    return int(round(percent))

def read_vochtigheid() -> int:
    import rp3_coms
    # Read ADC, convert to percentage, print concise message, return percentage.
    try:
        sensor = ADC(Pin(ADC_PIN))
        raw_value = sensor.read_u16()
    except Exception as e:
        rp3_coms.send_log(f"ERROR: Failed to read ADC on GP{ADC_PIN}: {e}")
        return 0

    percentage = _raw_to_percent(raw_value)
    rp3_coms.send_log(f"De aarde is {percentage}% nat", is_debug=True)
    return percentage