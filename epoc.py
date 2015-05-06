from emokit.emotiv import Emotiv
import gevent
from zmq import green as zmq

headset = Emotiv()

context = zmq.Context()
raw = context.socket(zmq.PUB)
quality = context.socket(zmq.PUB)

def setup():
    raw.bind('ipc:///var/socks/raw')
    quality.bind('ipc:///var/socks/quality')
    gevent.spawn(headset.setup)
    gevent.sleep(0)

def mainloop():
    while True:
        packet = headset.dequeue()
        BAD_SENSORS = set(['X', 'Y', 'Unknown'])
        values = {name: packet.sensors[name]['value'] for name in packet.sensors if name not in BAD_SENSORS}
        qualities = {name: packet.sensors[name]['quality'] for name in packet.sensors if name not in BAD_SENSORS}
        #print("socks", socks)
        raw.send_json(values)
        quality.send_json(qualities)
        gevent.sleep(0)

def cleanup():
    raw.close(linger=0)
    quality.close(linger=0)
    context.term()
    headset.close()

if __name__ == "__main__":
    setup()
    try:
        mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
