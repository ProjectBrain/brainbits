import numpy as np
import math
import zmq
from scipy import signal

context = zmq.Context()

freqs = context.socket(zmq.PUB)
freqs.bind('ipc:///var/socks/freqs')

raw = context.socket(zmq.SUB)
raw.connect('ipc:///var/socks/filtered')
raw.setsockopt(zmq.SUBSCRIBE, b'')

CHANNELS = ["AF3", "AF4", "F7", "F8", "F3", "F4", "FC5", "FC6", "T7", "T8", "P7", "P8", "O1", "O2"]
FREQ = 128.0
types = ["eeg" for c in CHANNELS]

SAMPLES = 512
SEGSIZE = 256

chandata = np.zeros([SAMPLES, len(CHANNELS)], 'float64')

HIGHPASS_FREQ = 3.
hipassb, hipassa = signal.butter(5, HIGHPASS_FREQ / (FREQ/2.), btype='high')

MAX_FREQ = 64.0
BINS = SEGSIZE/2
FREQ_PER_BIN = FREQ/BINS
BINS_PER_FREQ = BINS/FREQ

ARRAY_LEN = int(math.ceil(MAX_FREQ * BINS_PER_FREQ))
print("bins", BINS)
print("array len", ARRAY_LEN)


def process(num):
    indata = np.roll(chandata.transpose()[:num], -index, 1)
    psd = []
    filtered = signal.filtfilt(hipassb, hipassa, indata)
    freq, psd = signal.welch(filtered, fs=FREQ, nperseg=SEGSIZE, window='blackmanharris', noverlap=SEGSIZE*3/4)

    freqs.send_json({'psd': psd[:ARRAY_LEN].tolist(), 'freq': freq[:ARRAY_LEN].tolist()})


UPDATES_PER_SECOND = 8.0
SECONDS_PER_WINDOW = SAMPLES/FREQ
SAMPLES_PER_WINDOW = SAMPLES
SAMPLES_PER_SECOND = FREQ
SAMPLES_PER_UPDATE = int(FREQ / UPDATES_PER_SECOND)


print('seconds per window', SECONDS_PER_WINDOW)
print('samples per update', SAMPLES_PER_UPDATE)

index = 0
fillcount = 0

while True:
    try:
        data = raw.recv_json()
        chandata[index] = [data[chan] for chan in CHANNELS]
        index = (index + 1) % SAMPLES
        if index % SAMPLES_PER_UPDATE == 0:
            fillcount = max(fillcount, index)
            process(fillcount)

    except (KeyboardInterrupt, zmq.ContextTerminated):
        break
