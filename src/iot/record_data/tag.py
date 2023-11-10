import bluetooth
import asyncio
from machine import Pin

LED = Pin("LED", Pin.OUT)
INTERVAL = 0.1
NAME = "test_tag"

LOOPBACK = 1000

class BLETag:
    def __init__(self):
        self.ping_id = 0
        self.blink = False
        
        self.ble = bluetooth.BLE()

    async def ping(self):
        while True:
            # Send 1 ping
            self.ble.active(True)
            self.ble.gap_advertise(100 * 1000000, ("[TAG] %s | %d" % (NAME, self.ping_id)).encode("utf8"))
            # Make sure the ping gets sent
            await asyncio.sleep(0.1)
            # Make sure no more pings get sent
            self.ble.gap_advertise(None)
            self.ble.active(False)

            # Increment ping ID or loop around
            if self.ping_id == LOOPBACK:
                self.ping_id = 0
            else:
                self.ping_id += 1

            # Wait the rest of the time
            await asyncio.sleep(INTERVAL - 0.1)
    
    async def indicator(self):
        while True:
            if self.blink:
                LED.off()
            else:
                LED.on()
            self.blink = not self.blink
            await asyncio.sleep(1)

async def main():
    tag = BLETag()
    await asyncio.gather(tag.indicator(), tag.ping())

asyncio.run(main())



