import sys
sys.path.append("..")

import dataclasses
import threading
import flask
import internal

@dataclasses.dataclass
class BackendData:
    state: internal.ModelState
    entry_num: int

data: BackendData = BackendData(internal.ModelState({}, {}, internal.REQUIRED_ITEMS), -1)
data_lock = threading.Lock()
server = flask.Flask(__name__, template_folder="template")

class BackendWriter:
    def __init__(self):
        global server
        server_thread = threading.Thread(target=server.run)
        server_thread.start()

    def write_data(self, state: internal.ModelState, entry_num: int):
        global data, data_lock
        if data_lock.acquire(timeout=0.05):
            data = BackendData(state, entry_num)
            data_lock.release()

@server.route("/")
def home():
    return flask.render_template("home.html")

@server.route("/data/<entry>")
def get_data(entry: str):
    global data, data_lock
    entry_num = int(entry)
    if data_lock.acquire(timeout=0.1):
        if data is not None and data.entry_num >= entry_num:
            data_dict = dataclasses.asdict(data)
            data_lock.release()
            data_dict["state"]["missing"] = list(data_dict["state"]["missing"])
            return flask.jsonify(data_dict)
        data_lock.release()
    else:
        print("Server: Could not acquire lock in time")
    return flask.jsonify({})