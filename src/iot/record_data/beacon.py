import bluetooth
import asyncio
from machine import Pin
from micropython import const

_IRQ_SCAN_RESULT = const(5)
LED = Pin("LED", Pin.OUT)
DURATION = 1
ID = 0

class BLEBeacon:
    def __init__(self):
        self.blink = False
        
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self.handle_detected)
        # Constantly be scanning
        self.ble.gap_scan(0, (int)(DURATION * 1000000), (int)(DURATION * 1000000))

    def handle_detected(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            (addr_type,addr,adv_type,rssi,adv_data) = data
            try:
                # Data comes in the form:
                # [TAG] <tag name> | <ping id>
                data = bytes(adv_data).decode()
                if data[:5] == "[TAG]":
                    print(rssi)
            except:
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
    beacon = BLEBeacon()
    await asyncio.gather(beacon.indicator())

asyncio.run(main())

