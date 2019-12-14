import pyaudio
import time
import numpy as np
from threading import Thread
from queue import Queue
from scipy import signal
from scipy.fftpack import fft, fftfreq
import pygame

class AudioInput():
    DTYPE = np.float32
    CHANNELS = 1
    FS = 48000 # Hz
    CHUNK_SIZE = 128
    LOCALIZE_SIZE = 2048
    NUM_HOLD = LOCALIZE_SIZE//CHUNK_SIZE
    freq = fftfreq(LOCALIZE_SIZE, 1/FS)[0:LOCALIZE_SIZE//2]
    hpcoef_b, hpcoef_a = signal.butter(3, [200/(FS/2), 1800/(FS/2)], btype='band')
    window = np.kaiser(LOCALIZE_SIZE, 15)
    AudioInputEventType = pygame.USEREVENT+1
    AudioInputEvent = pygame.event.Event(AudioInputEventType)
    
    def __init__(self):
        self.onset_thres = 1; # just for initialization
        self.verbose = False # just for ini
        self.accept_band = [0, AudioInput.FS//2]
        self.analyze_queue = Queue();
        self.zi = signal.lfilter_zi(AudioInput.hpcoef_b, AudioInput.hpcoef_a) # filter initial value
        self.onset_cnt = 0
        self.hold_count = 0
        self.stream_thred = None
        self.analyze_thread = None
        self.stream = None
        
    def start_stream(self, onset_thres=0.035, verbose = False, accept_band=[0, FS//2]):        
        self.onset_thres = onset_thres; # onset threashold
        self.verbose = verbose
        self.accept_band = accept_band
        if verbose:
            print("Audio input reader starting...")
            print("sampling rate : {0:d} Hz".format(AudioInput.FS))
            print("resolution : {0:.2f} ms".format(AudioInput.LOCALIZE_SIZE/AudioInput.FS*1000))
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32,
                        channels=AudioInput.CHANNELS,
                        rate=AudioInput.FS,
                        output=False,
                        input=True,
                        stream_callback=self._detect_onset,
                        frames_per_buffer=AudioInput.CHUNK_SIZE)
        self.stream.start_stream()
        analyze_thread = Thread(target=self._analyze_threadf, daemon = True)
        analyze_thread.start()
        print("startsete")
    
    def _terminate_stream(self):
        self.stream.close()
        self.p.terminate()
        
    def _detect_onset(self, in_data, frame_count, time_info, flag):
        """
        Onset detector. Runs on separate thread implicitly.
        """
        # Raw streaming data with size CHUNK_SIZE
        audio_data = np.frombuffer(in_data, dtype=AudioInput.DTYPE)
        audio_filtered, self.zi = signal.lfilter(AudioInput.hpcoef_b, AudioInput.hpcoef_a, audio_data, zi=self.zi)
        if (self.hold_count > 0):
            # hold and sample
            self.analyze_queue.put(audio_filtered)
            self.hold_count -= 1
        else:
            if (any(audio_filtered>self.onset_thres)):
                # Onset detected here
                # print("onset".format(onset_cnt))
                self.hold_count = AudioInput.NUM_HOLD
        return in_data, pyaudio.paContinue
    
    def _analyze_threadf(self):
        """
        Frequency analyzing thread function.
        """
        h_cnt = AudioInput.NUM_HOLD - 1
        segments_buffer = []
        while(True):
            # queue.get blocks thread till new data arrives
            segment = self.analyze_queue.get()
            if (h_cnt > 0):    
                segments_buffer.append(segment)
                h_cnt -= 1
            else:
                segments_buffer.append(segment)
                localized_sample = np.concatenate(segments_buffer)
                # localized sample processed here
                pitch = self._estimate_pitch(localized_sample)
                lb = self.accept_band[0]
                rb = self.accept_band[1]
                if (pitch > lb and pitch < rb):    
                    pygame.event.post(AudioInput.AudioInputEvent)
                    if self.verbose:
                        print("detect {0:.2f} Hz".format(pitch))
                else:
                    if self.verbose:
                        print("reject {0:.2f} Hz".format(pitch)) # print out pitch
                segments_buffer.clear()
                h_cnt = AudioInput.NUM_HOLD - 1
    
    def _estimate_pitch(self, sample):
        """
        Estimate pitch from sampCle.
        """
        windowed_sample = np.multiply(AudioInput.window, sample)
        sample_fft = fft(windowed_sample, AudioInput.LOCALIZE_SIZE//2)
        return self.freq[np.argmax(np.absolute(sample_fft))]
    
    
#    def _print_star(pitch):
#        num_star = int((pitch-500)/25)
#        if num_star < 0:
#            num_star = 0
#        else:
#            print("{0:04d}hz\t".format(int(pitch)),end = "")
#            for i in range(num_star):
#                print('#', end='')
#            print("")

if __name__ == "__main__":
    pygame.init()
    audio_input = AudioInput()
    audio_input.start_stream(onset_thres=0.035, verbose=True)
    time.sleep(5)
    audio_input._terminate_stream()
    pygame.quit()
