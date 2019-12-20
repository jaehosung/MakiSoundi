# -*- coding: utf-8 -*-
import pyaudio
import time
import numpy as np
from threading import Thread
from queue import Queue
from scipy import signal

from numba import jit


class PitchEstimator:
    # absolute threshold for onset detection
    ONSET_THRES = 0.027
    # automatically terminate after duration
    STREAM_DURATION = 2500 # second
    
    DTYPE = np.float32
    CHANNELS = 1
    FS = 48000 # Hz
    # CHUNK_SIZE = 512
    CHUNK_SIZE = 128
    LOCALIZE_SIZE = 2048
    NUM_HOLD = LOCALIZE_SIZE//CHUNK_SIZE
    HOLD_COUNT = 0
    pyaudio_obj = pyaudio.PyAudio()

    def __init__(self):
        stream = self.pyaudio_obj.open(format=pyaudio.paFloat32,
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
            # print("Stream is stopped")    
        stream.close()
        p.terminate()
    
    def get_pitch(self):
        return self.NUM_HOLD
    
    
a = PitchEstimator()
b = a.getPitch()
print(b)