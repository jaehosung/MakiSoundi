import pyaudio
import time
import numpy as np
from threading import Thread
from queue import Queue
from scipy import signal
import pygame

class AudioInput():
    DTYPE = np.float32
    CHANNELS = 1
    FS = 48000 # Hz
    CHUNK_SIZE = 128
    LOCALIZE_SIZE = 4096
    NUM_HOLD = LOCALIZE_SIZE//CHUNK_SIZE
    freq = np.fft.fftfreq(LOCALIZE_SIZE, 1/FS)[0:LOCALIZE_SIZE//2]
    hpcoef_b, hpcoef_a = signal.butter(3, [500/(FS/2), 1800/(FS/2)], btype='band')
    window = np.kaiser(LOCALIZE_SIZE, 13)
    AudioInputEvent = pygame.event.Event(pygame.USEREVENT+1, message="Bad cat!")
    
    def __init__(self):
        self.onset_thres = 1; # just for initialization
        self.stream_duration = 0 # just for initialization
        self.verbose = False # just for ini
        self.analyze_queue = Queue();
        self.zi = signal.lfilter_zi(AudioInput.hpcoef_b, AudioInput.hpcoef_a) # filter initial value
        self.onset_cnt = 0
        self.hold_count = 0
        
    def start_stream(self, onset_thres=0.035, stream_duration=99999, verbose = False):        
        self.onset_thres = onset_thres; # onset threashold
        self.stream_duration = stream_duration # streaming duration
        self.verbose = verbose
        stream_thread = Thread(target=self._stream_threadf)
        analyze_thread = Thread(target=self._analyze_threadf, daemon = True)
        stream_thread.start()
        analyze_thread.start()
        stream_thread.join()
        
    def _stream_threadf(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32,
                        channels=AudioInput.CHANNELS,
                        rate=AudioInput.FS,
                        output=False,
                        input=True,
                        stream_callback=self._detect_onset,
                        frames_per_buffer=AudioInput.CHUNK_SIZE)
        stream.start_stream()
        while stream.is_active():
            time.sleep(self.stream_duration)
            stream.stop_stream()
            # print("Stream is stopped")    
        stream.close()
        p.terminate()

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
                if self.verbose:
                    AudioInput._print_star(pitch) # print out pitch
                segments_buffer.clear()
                h_cnt = AudioInput.NUM_HOLD - 1
    
    def _estimate_pitch(self, sample):
        """
        Estimate pitch from sampCle.
        """
        windowed_sample = np.multiply(AudioInput.window, sample)
        sample_fft = np.fft.fft(windowed_sample, AudioInput.LOCALIZE_SIZE//2)
        
        return self.freq[np.argmax(np.absolute(sample_fft))]
    
    def _print_star(pitch):
        num_star = int((pitch-500)/25)
        if num_star < 0:
            num_star = 0
        else:
            print("{0:04d}hz\t".format(int(pitch)),end = "")
            for i in range(num_star):
                print('#', end='')
            print("")

if __name__ == "__main__":
    pygame.init()
    audio_handler = AudioInput()
    audio_handler.start_stream(onset_thres=0.035, stream_duration=10, verbose=True)
    pygame.quit()
