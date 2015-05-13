import zmq
import sys

filename = sys.argv[1] or 'dump'

context = zmq.Context()
receiver = context.socket(zmq.SUB)
receiver.connect('ipc:///var/socks/raw')
receiver.setsockopt(zmq.SUBSCRIBE, b'')

with open(filename, 'w') as f:
  while True:
      try:
          f.write(receiver.recv())
          f.write('\n')
      except (KeyboardInterrupt, zmq.ContextTerminated):
          break

