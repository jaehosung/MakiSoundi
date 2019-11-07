import matplotlib.pyplot as plt
import pyaudio
import time
import numpy as np
from threading import Thread
from queue import Queue

p = pyaudio.PyAudio()

# absolute threshold for onset detection
ONSET_THRES = 0.08

CHANNELS = 1
FS = 48000
# CHUNK_SIZE = 512
CHUNK_SIZE = 256
LOCALIZE_SIZE = 1024
NUM_HOLD = LOCALIZE_SIZE//CHUNK_SIZE
HOLD_COUNT = 0


print("maximum resolution: {0:.3f}".format(LOCALIZE_SIZE/FS))

analyze_queue = Queue()

def analyze_threadf():
    """
    Frequency analyzing thread function
    """
    hold_count = NUM_HOLD - 1
    maxval = 0
    segments_buffer = []
    while(True):
        # queue.get blocks thread till new data arrives
        segment = analyze_queue.get()
        if (hold_count > 0):
            hold_count -= 1
            segments_buffer.append(segment)
        else:
            localized_sample = np.concatenate(segments_buffer)
            maxval = localized_sample.max()
            segments_buffer.clear()
            hold_count = NUM_HOLD - 1
            print(maxval)
        
def detect_onset(in_data, frame_count, time_info, flag):
    """
    Onset detector. Runs on separate thread implicitly.
    """
    # Raw streaming data with size CHUNK_SIZE
    audio_data = np.frombuffer(in_data, dtype=np.float32)
    global HOLD_COUNT
    if (HOLD_COUNT > 0):
        # hold and sample
        analyze_queue.put(audio_data)
        HOLD_COUNT -= 1
    else:
        if (any(audio_data>ONSET_THRES)):
            # Onset detected here
            print("onset") 
            HOLD_COUNT = NUM_HOLD
    return in_data, pyaudio.paContinue

def stream_threadf():
    """
    Audio streaming thread function
    """
    stream = p.open(format=pyaudio.paFloat32,
                channels=CHANNELS,
                rate=FS,
                output=False,
                input=True,
                stream_callback=detect_onset,
                frames_per_buffer=CHUNK_SIZE)
    stream.start_stream()
    while stream.is_active():
        time.sleep(10)
        stream.stop_stream()
        print("Stream is stopped")    
    stream.close()
    p.terminate()

stream_thread = Thread(target=stream_threadf)
analyze_thread = Thread(target=analyze_threadf, daemon = True)
stream_thread.start()
analyze_thread.start()

stream_thread.join()

