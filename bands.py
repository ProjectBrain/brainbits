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
    'delta': (0.0, 3.0),
    'theta': (3.5, 7.5),
    'alpha': (7.5, 13.0),
    'smr': (12.0, 15.0),
    'beta': (16.0, 32.0),
    'global': (0.0, 32.0)
}

while True:
    try:
        data = freqs.recv_json()
        freq = np.array(data['freq'], 'float32')
        psd = np.array(data['psd'], 'float32')
        results = {}
        for name, rng in RANGES.items():
            indices = np.where((freq >= rng[0]) & (freq <= rng[1]))
            results[name] = np.trapz(psd.take(indices, axis=1), indices)
        results['total'] = np.trapz(psd)

        #print results
        bands.send_json({k: v.tolist() for k, v in results.items()})

    except (KeyboardInterrupt, zmq.ContextTerminated):
        break

