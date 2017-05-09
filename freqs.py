import numpy as np
import math
import zmq
from scipy import signal

context = zmq.Context()

freqs = context.socket(zmq.PUB)
freqs.bind('ipc:///var/socks/freqs')

raw = context.socket(zmq.SUB)
raw.connect('ipc:///var/socks/raw')
raw.setsockopt(zmq.SUBSCRIBE, b'')

CHANNELS = ["AF3", "AF4", "F7", "F8", "F3", "F4", "FC5", "FC6", "T7", "T8", "P7", "P8", "O1", "O2"]
FREQ = 128.0
types = ["eeg" for c in CHANNELS]

SAMPLES = 4096
SEGSIZE = 512

chandata = np.empty([SAMPLES, len(CHANNELS)], 'int16')

index = 0
filled = False

HIGHPASS_FREQ = 1.0
hipassb, hipassa = signal.butter(5, HIGHPASS_FREQ / (FREQ/2.), btype='high')

MAX_FREQ = 64.0
BINS = SEGSIZE/2
FREQ_PER_BIN = FREQ/BINS
BINS_PER_FREQ = BINS/FREQ
ARRAY_LEN = MAX_FREQ * BINS_PER_FREQ
print("bins", BINS)
print("array len", int(math.ceil(ARRAY_LEN)))

def process():
    indata = np.asanyarray(np.roll(chandata.transpose(), -index, 1), 'float64')
    psd = []
    for sensordata in indata:
        filtered = signal.lfilter(hipassb, hipassa, sensordata)
        #freq, spectrum = signal.welch(filtered, fs=FREQ, nperseg=SAMPLES, noverlap=SAMPLES*3/4)
        #freq, spectrum = signal.welch(filtered, fs=FREQ, nperseg=SAMPLES, noverlap=SAMPLES/2)
        #freq, spectrum = signal.welch(filtered, fs=FREQ, nperseg=SAMPLES, window='blackmanharris', noverlap=SAMPLES*2/3)
        #freq, spectrum = signal.welch(filtered, fs=FREQ, nperseg=SEGSIZE, window='hamming', noverlap=SEGSIZE/2)
        freq, spectrum = signal.welch(filtered, fs=FREQ, nperseg=SEGSIZE, window='blackmanharris', noverlap=SEGSIZE*3/4)
        psd.append(spectrum[:ARRAY_LEN].tolist())
    freqs.send_json({'psd': psd, 'freq': freq[:ARRAY_LEN].tolist()})

UPDATES_PER_SECOND = 4.0
SECONDS_PER_WINDOW = SEGSIZE/FREQ
PIPELINE = FREQ / UPDATES_PER_SECOND

print "PIPELINE", PIPELINE

while True:
    try:
        data = raw.recv_json()
        chandata[index] = [data[chan] for chan in CHANNELS]
        index += 1
        if index == SAMPLES:
            filled = True
            index = 0
        if filled and index % PIPELINE == 0:
            process()

    except (KeyboardInterrupt, zmq.ContextTerminated):
        break

