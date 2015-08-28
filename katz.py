import gevent
import numpy as np
import zmq
from math import log10

context = zmq.Context()

fractal = context.socket(zmq.PUB)
fractal.bind('ipc:///var/socks/fractal')

raw = context.socket(zmq.SUB)
raw.connect('ipc:///var/socks/raw')
raw.setsockopt(zmq.SUBSCRIBE, b'')

CHANNELS = ["AF3", "AF4", "F7", "F8", "F3", "F4", "FC5", "FC6", "T7", "T8", "P7", "P8", "O1", "O2"]
FREQ = 128.0

SAMPLES = 256

chandata = np.empty([SAMPLES, len(CHANNELS)], 'int16')

index = 0
filled = False

def katz(data):
    n = len(data)-1
    L = np.hypot(np.diff(data), 1).sum() # Sum of distances
    d = np.hypot(data - data[0], np.arange(len(data))).max() # furthest distance from first point
    return log10(n) / (log10(d/L) + log10(n))

def katz2(data):
    dists = np.hypot(np.diff(data), 1)
    L = dists.sum()
    a = dists.mean()
    d = np.hypot(data - data[0], np.arange(len(data))).max() # furthest distance from first point
    return log10(L/a) / log10(d/a)


def process():
    indata = np.asanyarray(np.roll(chandata.transpose(), -index, 1), 'float64')
    #indata = [np.random.rand(100)]
    outdata = [katz(sensordata) for sensordata in indata]
    fractal.send_json(outdata)
    #print np.round(outdata, 2)

UPDATES_PER_SECOND = 8.0
SECONDS_PER_WINDOW = SAMPLES/FREQ
PIPELINE = FREQ / UPDATES_PER_SECOND

print "PIPELINE", PIPELINE

while True:
    try:
        data = raw.recv_json()
        chandata[index] = [data[chan] for chan in CHANNELS]
        index += 1
        if index == SAMPLES:
            filled = True
            index = 0
        if filled and index % PIPELINE == 0:
            process()

    except (KeyboardInterrupt, zmq.ContextTerminated):
        break

