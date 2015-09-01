import numpy as np
import scipy as sp
import zmq
import pyeeg

context = zmq.Context()

entropy = context.socket(zmq.PUB)
entropy.bind('ipc:///var/socks/entropy')

raw = context.socket(zmq.SUB)
raw.connect('ipc:///var/socks/raw')
raw.setsockopt(zmq.SUBSCRIBE, b'')

CHANNELS = ["AF3", "AF4", "F7", "F8", "F3", "F4", "FC5", "FC6", "T7", "T8", "P7", "P8", "O1", "O2"]
FREQ = 128.0

SAMPLES = 128

chandata = np.empty([SAMPLES, len(CHANNELS)], 'int16')

index = 0
filled = False

#Broken
def sampen(data, dim=1, r=0.25):
    N = len(data)
    Phi = np.ones((1, N-dim+1))
    Phi1 = np.zeros((1, N-dim+2))
    for m in xrange(dim, dim+2):

        X = np.zeros((N-m+1, m))
        for i in xrange(1, m+1):
            ids = numpy.arange(i, N-m+1 + i);
            X[:,i] = ids

        data_X = data[X]

def sampen2(X, M, R):
    N = len(X)

    Em = pyeeg.embed_seq(X, 1, M)
    Emp = pyeeg.embed_seq(X, 1, M + 1)

    Cm, Cmp = np.zeros(N - M - 1) + 1e-100, np.zeros(N - M - 1) + 1e-100
    # in case there is 0 after counting. Log(0) is undefined.

    for i in xrange(0, N - M):
        for j in xrange(i + 1, N - M):  # no self-match
            # if max(abs(Em[i]-Em[j])) <= R:  # v 0.01_b_r1
            if pyeeg.in_range(Em[i], Em[j], R):
                Cm[i] += 1
#            if max(abs(Emp[i] - Emp[j])) <= R: # v 0.01_b_r1
                if abs(Emp[i][-1] - Emp[j][-1]) <= R:  # check last one
                    Cmp[i] += 1

    Samp_En = np.log(sum(Cm) / sum(Cmp))

    return Samp_En

def process():
    indata = np.asanyarray(np.roll(chandata.transpose(), -index, 1), 'float64')
    #indata = [np.random.rand(100)]
    outdata = [sampen2(sensordata, 1, 0.25) for sensordata in indata]
    entropy.send_json(outdata)
    print np.round(outdata, 2)

UPDATES_PER_SECOND = 1
SECONDS_PER_WINDOW = SAMPLES/FREQ
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

