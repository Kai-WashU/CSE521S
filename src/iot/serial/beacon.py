import bluetooth
import network
import ubinascii
import time
from machine import Pin

LED = Pin("LED", Pin.OUT)

# Prints out MAC address
class BLEBeacon:
    def __init__(self):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        
        self.blink = False
        
        self.connections = set()
        self.name = "Pico ID: %s" % ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    
    def message(self):
        while True:
            if self.blink:
                LED.off()
            else:
                LED.on()
            self.blink = not self.blink
            print(self.name)
            time.sleep(1)

beacon = BLEBeacon()
beacon.message()
