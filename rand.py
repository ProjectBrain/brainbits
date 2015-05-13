import random
import gevent
from zmq import green as zmq

context = zmq.Context()
raw = context.socket(zmq.PUB)
quality = context.socket(zmq.PUB)

NAMES = ["AF3", "AF4", "F7", "F8", "F3", "F4", "FC5", "FC6", "T7", "T8", "P7", "P8", "O1", "O2"]

def setup():
    raw.bind('ipc:///var/socks/raw')
    quality.bind('ipc:///var/socks/quality')
    gevent.sleep(0)

def mainloop():
    while True:
        values = {name: random.random() for name in NAMES}
        qualities = {name: 15 for name in NAMES}
        raw.send_json(values)
        quality.send_json(qualities)
        gevent.sleep(1./128)

def cleanup():
    raw.close(linger=0)
    quality.close(linger=0)
    context.term()

if __name__ == "__main__":
    setup()
    try:
        mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
