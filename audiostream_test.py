import matplotlib.pyplot as plt
import pyaudio
import time
import numpy as np
from threading import Thread
from queue import Queue
from scipy import signal

from numba import jit

# absolute threshold for onset detection
ONSET_THRES = 0.027
# automatically terminate after duration
STREAM_DURATION = 25 # second

DTYPE = np.float32
CHANNELS = 1
FS = 48000 # Hz
# CHUNK_SIZE = 512
CHUNK_SIZE = 128
LOCALIZE_SIZE = 2048
NUM_HOLD = LOCALIZE_SIZE//CHUNK_SIZE
HOLD_COUNT = 0

print("maximum resolution: {0:.3f} s".format(LOCALIZE_SIZE/FS))
print("warning: first onset is useless; to be fixed")

# Axiliary glabal variables: to be refactored
analyze_queue = Queue()
window = np.kaiser(LOCALIZE_SIZE, 13)
freq = np.fft.fftfreq(LOCALIZE_SIZE, 1/FS)[0:LOCALIZE_SIZE//2]
hpcoef_b, hpcoef_a = signal.butter(3, [300/(FS/2), 1500/(FS/2)], btype='band')
zi = signal.lfilter_zi(hpcoef_b, hpcoef_a)
onset_cnt = 0

@jit(nopython=True)
def mult_wind(sample):
    return np.multiply(window, sample)

def estimate_pitch(sample):
    """
    Estimate pitch from sample.
    """
    windowed_sample = mult_wind(sample)
    sample_fft = np.fft.fft(windowed_sample, LOCALIZE_SIZE//2)
    return freq[np.argmax(np.absolute(sample_fft))]

def analyze_threadf():
    """
    Frequency analyzing thread function.
    """
    onset_cnt = 0
    hold_count = NUM_HOLD - 1
    segments_buffer = []
    while(True):
        # queue.get blocks thread till new data arrives
        segment = analyze_queue.get()
        onset_temp = onset_cnt
        if (hold_count > 0):    
            segments_buffer.append(segment)
            hold_count -= 1
        else:
            segments_buffer.append(segment)
            localized_sample = np.concatenate(segments_buffer)
            # localized sample processed here
            pitch = estimate_pitch(localized_sample)
            print("num {0:02d} : {1:.3f} Hz".format(onset_temp, pitch), end='\n\n')
            segments_buffer.clear()
            hold_count = NUM_HOLD - 1
            onset_cnt += 1

def detect_onset(in_data, frame_count, time_info, flag):
    """
    Onset detector. Runs on separate thread implicitly.
    """
    # Raw streaming data with size CHUNK_SIZE
    audio_data = np.frombuffer(in_data, dtype=DTYPE)
    global zi
    global HOLD_COUNT
    global onset_cnt
    audio_filtered, zi = signal.lfilter(hpcoef_b, hpcoef_a, audio_data, zi=zi)
    if (HOLD_COUNT > 0):
        # hold and sample
        analyze_queue.put(audio_filtered)
        HOLD_COUNT -= 1
    else:
        if (any(audio_filtered>ONSET_THRES)):
            # Onset detected here
            print("onset".format(onset_cnt)) 
            onset_cnt += 1
            HOLD_COUNT = NUM_HOLD
    return in_data, pyaudio.paContinue

def stream_threadf():
    """
    Audio streaming thread function.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                channels=CHANNELS,
                rate=FS,
                output=False,
                input=True,
                stream_callback=detect_onset,
                frames_per_buffer=CHUNK_SIZE)
    stream.start_stream()
    while stream.is_active():
        time.sleep(STREAM_DURATION)
        stream.stop_stream()
        print("Stream is stopped")    
    stream.close()
    p.terminate()

stream_thread = Thread(target=stream_threadf)
analyze_thread = Thread(target=analyze_threadf, daemon = True)
stream_thread.start()
analyze_thread.start()

stream_thread.join()

