import time
import math

_start_time = 0
_duration_minutes = 0
_current_cycle = "UNKNOWN"

def start_timer(duration_minutes, cycle_name="UNKNOWN"):
    global _start_time, _duration_minutes, _current_cycle
    _start_time = time.time()
    _duration_minutes = duration_minutes
    _current_cycle = cycle_name

def get_current_cycle():
    global _current_cycle
    return _current_cycle

def get_remaining_time():
    global _start_time, _duration_minutes
    if _start_time == 0:
        return 0, 0
    
    elapsed_minutes = (time.time() - _start_time) / 60
    remaining_minutes = _duration_minutes - elapsed_minutes
    
    # Logic from original lcd.py
    minuten_raw = math.ceil(remaining_minutes) - 1
    
    if minuten_raw < 0:
        minuten_raw = 0
        
    uren = minuten_raw // 60
    minuten = minuten_raw % 60
    return uren, minuten