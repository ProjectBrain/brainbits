import zmq
import sys

filename = sys.argv[1] or 'dump'
time = int(sys.argv[2] or 30)
samples = time * 128

context = zmq.Context()
receiver = context.socket(zmq.SUB)
receiver.connect('ipc:///var/socks/raw')
receiver.setsockopt(zmq.SUBSCRIBE, b'')

print("sampling for {} seconds".format(time))

i = 0
with open(filename, 'w') as f:
    while i < samples:
        try:
            f.write(str(receiver.recv()))
            f.write('\n')
            i = i + 1
            #print("{}/{}".format(i, samples))

        except (KeyboardInterrupt, zmq.ContextTerminated):
            break
