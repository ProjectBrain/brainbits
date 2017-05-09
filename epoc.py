from emokit.emotiv import Emotiv
import zmq
import time

headset = Emotiv()

context = zmq.Context()
raw = context.socket(zmq.PUB)
quality = context.socket(zmq.PUB)

def setup():
    raw.bind('ipc:///var/socks/raw')
    quality.bind('ipc:///var/socks/quality')

def mainloop():
    while True:
        packet = headset.dequeue()
        if packet is not None:
            BAD_SENSORS = set(['X', 'Y', 'Z', 'Unknown'])
            values = {name: packet.sensors[name]['value'] for name in packet.sensors if name not in BAD_SENSORS}
            qualities = {name: packet.sensors[name]['quality']/8192 for name in packet.sensors if name not in BAD_SENSORS}
            #print(values)
            raw.send_json(values)
            quality.send_json(qualities)
    time.sleep(0.001)

def cleanup():
    raw.close(linger=0)
    quality.close(linger=0)
    context.term()
    headset.stop()

if __name__ == "__main__":
    setup()
    try:
        mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
