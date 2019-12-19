# -*- coding: utf-8 -*-


from audio_input import AudioInput
from pynput.keyboard import Key, Controller
import time


keyboard = Controller()
def press_right():
    keyboard.press(Key.right)
    keyboard.release(Key.right)

def press_left():
    keyboard.press(Key.left)
    keyboard.release(Key.left)

audio_input = AudioInput(onset_thres=0.035, verbose=True)
audio_input.add_onset_action(press_right, accept_band=[1000, 4000])
#audio_input.add_onset_action(press_left, accept_band=[50, 999])
audio_input.launch()
time.sleep(10000)

