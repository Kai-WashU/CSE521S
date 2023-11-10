import bluetooth
import asyncio
from machine import Pin

LED = Pin("LED", Pin.OUT)
INTERVAL = 0.1
NAME = "test_tag"

LOOPBACK = 1000

TAG_UUID = bluetooth.UUID("6c7d1f50-7f51-11ee-b962-0242ac120002")
TAG_READ = [bluetooth.UUID("6c7d1f51-7f51-11ee-b962-0242ac120002"), bluetooth.FLAG_READ]
TAG_CHARACTERISTICS = [TAG_READ]
TAG_SERVICE = [TAG_UUID, TAG_CHARACTERISTICS]

class BLETag:
    def __init__(self):
        self.ping_id = 0
        self.blink = False
        
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self.handle_ble)
        
        

    
    def handle_ble(self, event, data):
        pass

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



