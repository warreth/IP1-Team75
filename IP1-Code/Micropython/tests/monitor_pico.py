import serial
import json
import time
import threading

# --- CONFIGURATIE ---
# Pas aan als je niet de standaard poort gebruikt
SERIAL_PORT = '/dev/serial0' 
BAUD_RATE = 9600

def parse_pico_message(line):
    """Probeert de ontvangen tekst te begrijpen."""
    try:
        # 1. Kijk of het een LOG bericht is
        if line.startswith("LOG:"):
            print(f"📄 [LOG]: {line[4:].strip()}")
            return

        # 2. Probeer het als JSON status data te lezen
        data = json.loads(line)
        print(f"📊 [STATUS]: Vocht={data.get('humidity')}% | Pomp={data.get('pump_speed')} | Lamp1={data.get('lamp1')}")
        
    except json.JSONDecodeError:
        # Als het geen JSON is, print gewoon de ruwe tekst
        print(f"⚠️ [RAW]: {line}")
    except Exception as e:
        print(f"❌ Fout bij parsen: {e}")

def listen_to_uart(ser):
    """Luistert continu naar de Pico."""
    print("--- Luisteren gestart (Druk Ctrl+C om te stoppen) ---")
    while True:
        try:
            if ser.in_waiting > 0:
                # Lees een hele regel tot aan de \n
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    parse_pico_message(line)
        except OSError:
            print("Seriële poort fout (kabel los?).")
            break

def send_test_command(ser):
    """Stuurt een geldig JSON commando om te testen."""
    print("\n...Verstuur test commando: Pomp aan (snelheid 20000)...")
    command = {"command": "CHANGE_POMP_SPEED", "value": 20000}
    json_cmd = json.dumps(command) + "\n"
    ser.write(json_cmd.encode('utf-8'))

if __name__ == "__main__":
    try:
        # Open de verbinding
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        
        # Start luisteren in een achtergrond 'thread'
        t = threading.Thread(target=listen_to_uart, args=(ser,))
        t.daemon = True
        t.start()

        # Wacht even en stuur dan een test commando
        time.sleep(3) 
        send_test_command(ser)

        # Houd het script draaiende
        while True:
            time.sleep(1)

    except serial.SerialException:
        print(f"KAN POORT NIET OPENEN: {SERIAL_PORT}")
        print("Check: Staat Serial aan in raspi-config? Is de kabel goed?")
    except KeyboardInterrupt:
        print("\nGestopt.")