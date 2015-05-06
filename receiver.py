import zmq

context = zmq.Context()
receiver = context.socket(zmq.SUB)
receiver.connect('ipc:///var/socks/bands')
receiver.setsockopt(zmq.SUBSCRIBE, b'')
while True:
    try:
        print receiver.recv_json()
    except (KeyboardInterrupt, zmq.ContextTerminated):
        break

