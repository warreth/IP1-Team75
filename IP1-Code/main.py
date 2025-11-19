import uasyncio
from lich import lich
from water import water

async def main():
    # Create tasks for lich and water to run concurrently
    uasyncio.create_task(lich())
    uasyncio.create_task(water())
    
    # Keep the main coroutine running forever
    while True:
        await uasyncio.sleep(10)

# Run the main asynchronous function
try:
    uasyncio.run(main())
except KeyboardInterrupt:
    print("Program stopped")
