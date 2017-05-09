import os
import json
import zmq

context = zmq.Context()

bands = context.socket(zmq.SUB)
bands.connect('ipc:///var/socks/bands')
bands.setsockopt(zmq.SUBSCRIBE, b'')

while True:
    data = bands.recv()
    with open('/tmp/data2.json', 'w') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.rename('/tmp/data2.json', '/tmp/data.json')

