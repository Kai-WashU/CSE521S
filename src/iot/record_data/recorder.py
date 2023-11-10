import serial
import time
import enum
import statistics

# USB Addresses of Beacons
PORT = "/dev/cu.usbmodem1101"
DURATION = 60

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
        while time.time() < start + DURATION:
            # Read in new data
            data = self.serial_stream.read_until()
            (tag_name, rssi, ping_id) = self.parse_report(data.decode())
            self.message += f"{rssi}, "
            self.data.append(rssi)

            if len(self.data) % 5 == 0:
                for i in range(loading - 1):
                    print(".", end="")
                print(".", end="\r")
                loading += 1

        print(self.message[:-2])
        self.data.sort()
        min = self.data[0]
        max = self.data[len(self.data) - 1]
        stdev = statistics.pstdev(self.data)

        avg = 0
        for rssi in self.data:
            avg += rssi
        avg /= len(self.data)

        print(f"Duration: {DURATION}s | Pings Detected: {len(self.data)} | Min: {min} | Max: {max} | Average: {avg} | Standard Deviation: {stdev}")


model = Recorder()
model.record()