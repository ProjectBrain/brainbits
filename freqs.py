import gevent
import numpy as np
#from zmq import green as zmq
import zmq
#import mne
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
#info = mne.create_info(CHANNELS, FREQ, types) 

SAMPLES = 512 #64 #128 #512

chandata = np.empty([SAMPLES, len(CHANNELS)], 'int16')

index = 0
filled = False

#def process():
#    print "chandata", (chandata.transpose()[0]).tolist()
#    rawary = mne.io.RawArray(chandata.transpose(), info)
#    psd, freq = mne.time_frequency.compute_raw_psd(rawary, n_fft=256, n_overlap=32)
#    processed.send_json({'psd': psd.tolist(), 'freq': freq.tolist()})
#    print "psd", len(psd)
#    print "psd0", len(psd[0]), sum(psd[0])
#    print "freq", len(freq)

HIGH_FREQ = 2.0 #0.16
hipassb, hipassa = signal.butter(5, HIGH_FREQ / (FREQ/2.), btype='high')

def process2():
    indata = np.asanyarray(np.roll(chandata.transpose(), -index, 1), 'float64')
    psd = []
    for sensordata in indata:
        filtered = signal.lfilter(hipassb, hipassa, sensordata)
        freq, spectrum = signal.welch(filtered, fs=FREQ, nperseg=1024, noverlap=32)
        psd.append(spectrum.tolist())
    freqs.send_json({'psd': psd, 'freq': freq.tolist()})
    print "%d/%d" % (index, SAMPLES)
    print "psd", len(psd)
    #print "psd0", len(psd[0]), sum(psd[0])
    print "freq", len(freq)

while True:
    try:
        data = raw.recv_json()
        chandata[index] = [data[chan] for chan in CHANNELS]
        index += 1
        if index == SAMPLES:
            filled = True
            index = 0
        if filled and index % 16 == 0:
            process2()

    except (KeyboardInterrupt, zmq.ContextTerminated):
        break

