import bluetooth
import asyncio
from machine import Pin

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)

LED = Pin("LED", Pin.OUT)
INTERVAL = 0.1
NAME = "test_tag"

LOOPBACK = 1000

TAG_UUID = bluetooth.UUID("6c7d1f50-7f51-11ee-b962-0242ac120002")
TAG_READ = [bluetooth.UUID("6c7d1f51-7f51-11ee-b962-0242ac120002"), bluetooth.FLAG_READ]
TAG_CHARACTERISTICS = [TAG_READ]
TAG_SERVICE = [TAG_UUID, TAG_CHARACTERISTICS]

BEACON_UUID = bluetooth.UUID("80d0aa40-7f52-11ee-b962-0242ac120002")
BEACON_WRITE = [bluetooth.UUID("80d0aa41-7f52-11ee-b962-0242ac120002"), bluetooth.FLAG_WRITE]
BEACON_CHARACTERISTICS = [BEACON_WRITE]
BEACON_SERVICE = [BEACON_UUID, BEACON_CHARACTERISTICS]

SERVICES = [TAG_SERVICE, BEACON_SERVICE]

ADVERTISE_INTERVAL = 1

class BLEBeacon:
    def __init__(self):
        self.ping_id = 0
        self.blink = False
        
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self.handle_ble)

        self.connections = set()

        ((self.tag_read,), (self.beacon_write,)) = self.ble.gatts_register_services(SERVICES)
        self.ble.gap_advertise(ADVERTISE_INTERVAL * 1000000, SERVICES)

    def handle_ble(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            print("Connected")
        elif event == _IRQ_CENTRAL_DISCONNECT:
            print("Disconnect")
        print(data)
    
    async def indicator(self):
        while True:
            if self.blink:
                LED.off()
            else:
                LED.on()
            self.blink = not self.blink
            await asyncio.sleep(1)

async def main():
    beacon = BLEBeacon()
    await asyncio.gather(beacon.indicator())

asyncio.run(main())



