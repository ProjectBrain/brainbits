import zmq
import sys
import time
import zmq

filename = sys.argv[1] or 'dump'

context = zmq.Context()
raw = context.socket(zmq.PUB)
raw.bind('ipc:///var/socks/raw')

with open(filename, 'r') as f:
    for line in f:
        raw.send_string(line)
        time.sleep(1./128)
