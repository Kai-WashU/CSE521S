import serial
import threading
import enum

# USB Addresses of Beacons
TABLE_0_ADDRESS = "/dev/cu.usbmodem1101"
TABLE_1_ADDRESS = "/dev/cu.usbmodem1201"
BOX_ADDRESS = "/dev/cu.usbmodem1301"

GROUPING = 1            # Currently, we aren't running into issues, but it is believable that we might
MAX_ENTRIES = 16        # Pings get completed relatively fast.
EVICTION_RATIO = 0.75   # What proportion of accumulated pings should be evicted when we hit the limit

class Beacon(enum.Enum):
    TABLE_0 = 0
    TABLE_1 = 1
    BOX = 2

class ThreeBeaconIoT:
    def __init__(self):
        # Dictionary containing RSSI data
        # <tag name> --> <ping id> --> [<table_0 rssi>, <table_1 rssi>, <box rssi>, <timeout>]
        self.record: dict[str, dict[int, list[int]]] = {}
        # Keep track of key info for entries in order so that we can evict entries if there are too many
        self.eviction_list: list[(str, int)] = []
        self.lock = threading.Lock()

        self.table_0 = serial.Serial(port=TABLE_0_ADDRESS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE)
        self.table_0.flush()

        self.table_1 = serial.Serial(port=TABLE_1_ADDRESS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE)
        self.table_1.flush()

        self.box = serial.Serial(port=BOX_ADDRESS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE)
        self.box.flush()
    
    # Takes in reports in the form:
    # <tag name>, <RSSI>, <ping id>
    def parse_report(self, report: str) -> (str, int, int):
        data = report.split(",")

        tag_name = data[0].strip()
        rssi = int(data[1].strip())
        ping_id = int(data[2].strip())

        return (tag_name, rssi, ping_id)

    def listen(self, beacon: Beacon):
        serial_stream = None
        entry_index = -1

        if beacon == Beacon.TABLE_0:
            serial_stream = self.table_0
            entry_index = 0
        elif beacon == Beacon.TABLE_1:
            serial_stream = self.table_1
            entry_index = 1
        else:
            serial_stream = self.box
            entry_index = 2

        while True:
            # Read in new data
            data = serial_stream.read_until()
            (tag_name, rssi, ping_id) = self.parse_report(data.decode())

            # Group pings 
            ping_id -= ping_id % GROUPING

            with self.lock:
                if tag_name not in self.record:
                    self.record[tag_name] = {}
                if ping_id not in self.record[tag_name]:
                    self.record[tag_name][ping_id] = [None, None, None]
                    self.eviction_list.append((tag_name, ping_id))
                
                # Since we are grouping pings, it is possible we will overlap
                # Only update when it if data is needed
                if self.record[tag_name][ping_id][entry_index] is None:
                    self.record[tag_name][ping_id][entry_index] = rssi
                    
                    table_0_rssi = self.record[tag_name][ping_id][0]
                    table_1_rssi = self.record[tag_name][ping_id][1]
                    box_rssi = self.record[tag_name][ping_id][2]

                    # If the entry is complete, make a determination
                    if table_0_rssi is not None and table_1_rssi is not None and box_rssi is not None:
                        print(f"Completed entry: {tag_name} | {ping_id} | {table_0_rssi}, {table_1_rssi}, {box_rssi}")
                        del self.record[tag_name][ping_id]
                        self.eviction_list.remove((tag_name, ping_id))

                        table_average = (table_0_rssi + table_1_rssi) / 2
                        confidence_delta = table_average - box_rssi
                        print(f"Confidence Delta: {confidence_delta}")

                        # TODO: Send confidence delta to internal model
                
                # If necessary, evict items. We need to evict in waves, otherwise new pings can't be tracked
                if len(self.eviction_list) > MAX_ENTRIES:
                    for i in range(int(MAX_ENTRIES * EVICTION_RATIO)):
                        (tag_name, ping_id) = self.eviction_list.pop()
                        del self.record[tag_name][ping_id]
    
    # A blocking call which runs the IoT listeners
    def run(self):
        table_0_thread = threading.Thread(target=self.listen, args=[Beacon.TABLE_0])
        table_1_thread = threading.Thread(target=self.listen, args=[Beacon.TABLE_1])
        table_0_thread.start()
        table_1_thread.start()
        self.listen(Beacon.BOX)
                

if __name__ == "__main__":
    model = ThreeBeaconIoT()
    model.run()
    while True:
        pass