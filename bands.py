import gevent
import numpy as np
#from zmq import green as zmq
import zmq
#import mne
from scipy import signal

context = zmq.Context()

bands = context.socket(zmq.PUB)
bands.bind('ipc:///var/socks/bands')

freqs = context.socket(zmq.SUB)
freqs.connect('ipc:///var/socks/freqs')
freqs.setsockopt(zmq.SUBSCRIBE, b'')

RANGES = {
    'delta': (0.0,3.0)
    'lowtheta': (3.5,7.5)
    'hightheta': (7.5,13.0)
    'smr': (12.0,15.0)
    'beta': (16.0)
}

while True:
    try:
        data = freqs.recv_json()
        out = []
        for chan in data.psd:
            
        chandata[index] = [data[chan] for chan in CHANNELS]
        index += 1
        if index == SAMPLES:
            filled = True
            index = 0
        if filled and index % 16 == 0:
            process2()

    except (KeyboardInterrupt, zmq.ContextTerminated):
        break

