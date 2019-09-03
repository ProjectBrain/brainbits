import numpy as np
import math
import zmq
from scipy import signal

context = zmq.Context()

filtered = context.socket(zmq.PUB)
filtered.bind('ipc:///var/socks/filtered')

raw = context.socket(zmq.SUB)
raw.connect('ipc:///var/socks/raw')
raw.setsockopt(zmq.SUBSCRIBE, b'')

CHANNELS = ["AF3", "AF4", "F7", "F8", "F3", "F4", "FC5", "FC6", "T7", "T8", "P7", "P8", "O1", "O2"]

while True:
    try:
        data = raw.recv_json()
        dataa = np.array([data[chan] for chan in CHANNELS], dtype='int')
        average = int(np.mean(dataa))
        result = {CHANNELS[i]: int(val) for i, val in enumerate(dataa - average)}
        filtered.send_json(result)

    except (KeyboardInterrupt, zmq.ContextTerminated):
        break
