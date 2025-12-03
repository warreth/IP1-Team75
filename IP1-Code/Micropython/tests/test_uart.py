import machine
import time

def test_uart_send():
    # Initialize UART 1 with baudrate 9600, tx pin 4, rx pin 5 (adjust pins as needed for your board)
    # On standard RPi, UART is often on specific GPIOs, but for MicroPython on Pico/ESP, pins are configurable.
    # Assuming a generic setup here.
    try:
        uart = machine.UART(1, baudrate=9600, tx=machine.Pin(8), rx=machine.Pin(9))
        print("UART initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize UART: {e}")
        return

    count = 0
    while True:
        try:
            message = f"Test message {count}\n"
            
            # Send the message encoded as bytes
            uart.write(message.encode('utf-8'))
            
            print(f"Sent: {message.strip()}")
            
            count += 1
            time.sleep(1)
            
        except Exception as e:
            print(f"Error sending data: {e}")
            time.sleep(1)

if __name__ == "__main__":
    test_uart_send()