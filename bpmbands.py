import numpy as np
import zmq
from scipy import signal

context = zmq.Context()

bands = context.socket(zmq.PUB)
bands.bind('ipc:///var/socks/bpmbands')

freqs = context.socket(zmq.SUB)
freqs.connect('ipc:///var/socks/freqs')
freqs.setsockopt(zmq.SUBSCRIBE, b'')

BPM = 150
FREQ = BPM / 60.0
SPREAD = 1
ENV_SPREAD = 2

RANGES = {
    'bpm/2': (FREQ/2.0-SPREAD, FREQ/2.0+SPREAD),
    'bpm/2env': (FREQ/2.0-ENV_SPREAD, FREQ/2.0+ENV_SPREAD),
    'bpm': (FREQ-SPREAD, FREQ+SPREAD),
    'bpmenv': (FREQ-ENV_SPREAD, FREQ+ENV_SPREAD),
    'bpm2': (FREQ*2-SPREAD, FREQ*2+SPREAD),
    'bpm2env': (FREQ*2-ENV_SPREAD, FREQ*2+ENV_SPREAD),
    'bpm4': (FREQ*4-SPREAD, FREQ*4+SPREAD),
    'bpm4env': (FREQ*4-ENV_SPREAD, FREQ*4+ENV_SPREAD),
}

while True:
    try:
        data = freqs.recv_json()
        freq = np.array(data['freq'], 'float32')
        psd = np.array(data['psd'], 'float32')
        results = {}
        for name, rng in RANGES.items():
            indices = np.where((freq >= rng[0]) & (freq <= rng[1]))
            results[name] = np.trapz(np.squeeze(psd.take(indices, axis=1)), indices)
        results['total'] = np.trapz(psd)

        #print results
        bpmdata = {k: v.tolist() for k, v in results.items()}
        bpmdata['freq'] = FREQ
        bands.send_json(bpmdata)

    except (KeyboardInterrupt, zmq.ContextTerminated):
        break

