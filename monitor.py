import zmq
import sys

sock = sys.argv[1]

context = zmq.Context()
receiver = context.socket(zmq.SUB)
receiver.connect('ipc:///var/socks/' + sock)
receiver.setsockopt(zmq.SUBSCRIBE, b'')

while True:
    try:
        print(receiver.recv())
    except (KeyboardInterrupt, zmq.ContextTerminated):
        break

