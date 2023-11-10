import sys
sys.path.insert(0, "../..")

import dataclasses
import threading
import flask
import src

@dataclasses.dataclass
class BackendData:
    state: src.ModelState
    entry_num: int

data: BackendData = None
data_lock = threading.Lock()
server = flask.Flask(__name__, template_folder="template")

# TODO: Add a class which modifies the global variables for the internal model
class BackendWriter:
    pass

@server.route("/")
def home():
    return flask.render_template("home.html")

@server.route("/data/<entry>")
def get_data(entry: str):
    global data, data_lock
    entry_num = int(entry)
    if data_lock.acquire(timeout=0.1):
        if data is not None and data[1] >= entry_num:
            data_dict = dataclasses.asdict(data)
            data_lock.release()
            return flask.jsonify(data_dict)
        data_lock.release()
    else:
        print("Server: Could not acquire lock in time")
    return flask.jsonify({})

server.run()