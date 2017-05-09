import numpy as np
import zmq
from scipy import signal

context = zmq.Context()

visdata = context.socket(zmq.PUB)
visdata.bind('ipc:///var/socks/visdata')

bandsock = context.socket(zmq.SUB)
bandsock.connect('ipc:///var/socks/bands')
bandsock.setsockopt(zmq.SUBSCRIBE, b'')

bpmsock = context.socket(zmq.SUB)
bpmsock.connect('ipc:///var/socks/bpmbands')
bpmsock.setsockopt(zmq.SUBSCRIBE, b'')

scales = [{'highest': 0, 'lowest': 0} for _ in range(0, 14)]
DECAY = 0.01

highest = 0
lowest = 0

while True:
    try:
        bands = bandsock.recv_json()
        bpms = bpmsock.recv_json()

        result = []

        avgscale = (highest + lowest) / 2.
        highest = highest * (1-DECAY) + avgscale * DECAY
        lowest = lowest * (1-DECAY) + avgscale * DECAY

        for alpha, beta, theta, total, bpm, bpmenv, scale in zip(bands['alpha'], bands['beta'], bands['theta'], bands['total'], bpms['bpm'], bpms['bpmenv'], scales):
#        for band, bpm, scale in zip(banddata, bpmdata, scales):
            # avgscale = (scale['highest'] + scale['lowest']) / 2.
            # scale['highest'] = scale['highest'] * (1-DECAY) + avgscale * DECAY
            # scale['lowest'] = scale['lowest'] * (1-DECAY) + avgscale * DECAY

            # if scale['highest'] < total: scale['highest'] = total
            # if scale['lowest'] > total: scale['lowest'] = total

            # scaledtotal = (total - scale['lowest']) / (scale['highest'] - scale['lowest'])

            if highest < total: highest = total
            if lowest > total: lowest = total

            scaledtotal = (total - lowest) / (highest - lowest)

            # proportionaltotal = total / 32.
            r = min(1, (beta / total) / (16 / 32.))
            g = min(1, (theta / total) / (4 / 32.))
            b = min(1, (alpha / total) / (5.5 / 32.))

            result.append({
                'color': [int(r*255), int(g*255), int(b*255)],
                'intensity': scaledtotal,
                'frequency': bpms['freq'],
                'amplitude': max(0, bpm * 2 / bpmenv - 1),
                'phase': 0.0
            })

        visdata.send_json(result)

    except (KeyboardInterrupt, zmq.ContextTerminated):
        break

