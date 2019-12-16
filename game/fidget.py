# -*- coding: utf-8 -*-

"""Fidget, inspired by fidget spinners.

Exercises

1. Change the spinner pattern.
2. Respond to mouse clicks.
3. Change its acceleration.
4. Make it go forwards and backwards.

"""
import turtle
from audio_input import AudioInput
from pynput.keyboard import Key, Controller
import numpy as np

keyboard = Controller()
def press_space():
    keyboard.press(Key.space)
    keyboard.release(Key.space)

def press_a():
    keyboard.press('a')
    keyboard.release('a')

audio_input = AudioInput(onset_thres=0.035, verbose=True)
audio_input.add_onset_action(press_space, accept_band=[1000, 4000])
audio_input.add_onset_action(press_a, accept_band=[50, 999])
audio_input.launch()

state = {'turn': 0}
windmill_image = "Artboard 6.png"

def spinner():
    "Draw fidget spinner."
    turtle.clear()
    turtle.angle = state['turn'] / 10
    turtle.right(turtle.angle)
    turtle.forward(100)
    turtle.dot(120, 'red')
    turtle.back(100)
    turtle.right(120)
    turtle.forward(100)
    turtle.dot(120, 'green')
    turtle.back(100)
    turtle.right(120)
    turtle.forward(100)
    turtle.dot(120, 'blue')
    turtle.back(100)
    turtle.right(120)
    turtle.update()
    
def animate():
    "Animate fidget spinner."
    damp = max(np.abs(round(state['turn']*0.01)),1)
    if state['turn'] > 0:
        state['turn'] -= damp
    elif state['turn'] < 0:
        state['turn'] += damp
    else:
        state['turn'] = 0
    spinner()
    turtle.ontimer(animate, 20)

def flick():
    "Flick fidget spinner."
    state['turn'] += 20

def drag():
    "Drag fidget spinner."
    state['turn'] -= 20
    
def terminate():
    audio_input.terminate()
    turtle.bye()


turtle.setup(420, 420, 370, 0)
turtle.hideturtle()
turtle.tracer(False)
turtle.width(20)
turtle.onkey(flick, 'space')
turtle.onkey(drag, 'a')
turtle.onkey(terminate, 'Escape')
turtle.listen()
animate()
turtle.done()
 
