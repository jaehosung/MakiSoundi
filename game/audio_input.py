import pyaudio
import time
import numpy as np
from threading import Thread
from queue import Queue
from scipy import signal
from scipy.fftpack import fft, fftfreq

class AudioInput():
    DTYPE = np.float32
    CHANNELS = 1
    FS = 48000 # Hz
    CHUNK_SIZE = 128
    LOCALIZE_SIZE = 2048
    NUM_HOLD = LOCALIZE_SIZE//CHUNK_SIZE
    freq = fftfreq(LOCALIZE_SIZE, 1/FS)[0:LOCALIZE_SIZE//2]
    #hpcoef_b, hpcoef_a = signal.butter(3, [150/(FS/2), 2500/(FS/2)], btype='band')
    hpcoef_b, hpcoef_a = signal.butter(3, 300/(FS/2), btype='high')
    window = np.kaiser(LOCALIZE_SIZE, 14)
    
    def __init__(self, onset_thres=0.035, verbose = False):
        self.onset_thres = onset_thres # just for initialization
        self.verbose = verbose # just for ini
        self.onset_actions = []
        self.onset_action_params = []
        self.accept_bands = []
        self.analyze_queue = Queue();
        self.zi = signal.lfilter_zi(AudioInput.hpcoef_b, AudioInput.hpcoef_a) # filter initial value
        self.onset_cnt = 0
        self.hold_count = 0
        self.main_thread = None
        self.analyze_thread = None
        self.stream = None
    
    def add_onset_action(self, onset_action, *onset_action_params, accept_band=[0, FS//2]):
        self.onset_actions.append(onset_action)
        self.onset_action_params.append((onset_action_params))
        self.accept_bands.append(accept_band)        
        
    def launch(self):
        self.main_thread = Thread(target=self.__launch_streamf, daemon=True, name="AudioInput_main_thread")
        self.main_thread.start()
        if self.verbose:
            print("Audiostream main thread launched")
        self.main_thread.join()
    
    def terminate(self):
        self.stream.close()
        self.p.terminate()
        if self.verbose:
            print("Audiostream main thread terminated")
    
    def __launch_streamf(self):
        if self.verbose:
            print("Audio input reader starting...")
            print("sampling rate : {0:d} Hz".format(AudioInput.FS))
            print("resolution : {0:.2f} ms".format(AudioInput.LOCALIZE_SIZE/AudioInput.FS*1000))
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32,
                        channels=AudioInput.CHANNELS,
                        rate=AudioInput.FS,
                        output=False,
                        input=True,
                        stream_callback=self.__detect_onset,
                        frames_per_buffer=AudioInput.CHUNK_SIZE)
        self.stream.start_stream()
        self.analyze_thread = Thread(target=self.__analyze_threadf, daemon = True, name="AudioInput_analyze_thread")
        self.analyze_thread.start()
        if self.verbose:
            print("Analyze thread launched")
        
    def __detect_onset(self, in_data, frame_count, time_info, flag):
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
                #print("onset")
                self.hold_count = AudioInput.NUM_HOLD
        return in_data, pyaudio.paContinue
    
    def __analyze_threadf(self):
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
                pitch = self.__estimate_pitch(localized_sample)
                if self.verbose:
                    print("detect {0:.2f} Hz".format(pitch))
                for i in range(len(self.onset_actions)):
                    if (pitch > self.accept_bands[i][0] and pitch < self.accept_bands[i][1]):    
                        self.onset_actions[i](*self.onset_action_params[i])
                        if self.verbose:
                            print("action {0:d} accepted".format(i))
                segments_buffer.clear()
                h_cnt = AudioInput.NUM_HOLD - 1
    
    def __estimate_pitch(self, sample):
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
    print("10 seconds test")
    audio_input = AudioInput(onset_thres=0.035, verbose=True)
    audio_input.launch()
    time.sleep(30)
    audio_input.terminate()
    
