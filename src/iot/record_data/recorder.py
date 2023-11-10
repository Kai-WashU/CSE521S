import serial
import time
import enum
import pyperclip

# USB Addresses of Beacons
PORT = "/dev/cu.usbmodem101"
N = 50

class Beacon(enum.Enum):
    TABLE = 0
    MIDDLE = 1
    BOX = 2

class Recorder:
    def __init__(self):
        # List of RSSI data
        self.data: list[int] = []
        self.message = ""

        self.serial_stream = serial.Serial(port=PORT, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE)
        self.serial_stream.flush()

    # Takes in reports in the form:
    # <tag name>, <RSSI>, <ping id>
    def parse_report(self, report: str) -> (str, int, int):
        data = report.split(",")

        tag_name = data[0].strip()
        rssi = int(data[1].strip())
        ping_id = int(data[2].strip())

        return (tag_name, rssi, ping_id)
    
    def record(self):
        start = time.time()
        loading = 1

        while len(self.data) < N:
            # Read in new data
            data = self.serial_stream.read_until()
            (tag_name, rssi, ping_id) = self.parse_report(data.decode())
            self.message += f"{rssi}\n"
            self.data.append(rssi)

            if len(self.data) % 5 == 0:
                for i in range(loading - 1):
                    print(".", end="")
                print(".", end="\r")
                loading += 1

        pyperclip.copy(f"{time.time() - start}\n{self.message[:-1]}")
        


model = Recorder()
model.record()