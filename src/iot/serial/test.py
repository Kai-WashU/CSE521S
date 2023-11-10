import serial

port = "/dev/cu.usbmodem101"

class SerialReader:
    def __init__(self):
        self.buffer = bytearray()
        self.connection = serial.Serial(port=port, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE)
        self.connection.flush()
    
    def listen(self):
        while True:
            # Read in new data
            data = self.connection.read_until()
            print("Recieved Message")
            print(data.decode())


if __name__ == "__main__":
    reader = SerialReader()
    reader.listen()