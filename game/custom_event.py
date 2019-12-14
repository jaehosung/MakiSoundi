# -*- coding: utf-8 -*-

import pygame
import sys
from audio_input import AudioInput
from threading import Thread

VERBOSE = True # verbose mode

def audio_threadf():
    global VERBOSE
    audio_input = AudioInput()
    audio_input.start_stream(onset_thres=0.021, verbose=VERBOSE)

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

white = (255, 255, 255)
black = (0, 0, 0)

pygame.init()
if VERBOSE:
    print("Pygame initialized...")
print("Press ESC to exit")
audio_thread = Thread(target=audio_threadf, daemon = True)
audio_thread.start()

pygame.display.set_caption("Simple PyGame Example")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pos_x = 200
pos_y = 200

clock = pygame.time.Clock()
while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        
        if event.type == AudioInput.AudioInputEventType:
            pos_x += 10

    key_event = pygame.key.get_pressed()
    if key_event[pygame.K_LEFT]:
        pos_x -= 1

    if key_event[pygame.K_RIGHT]:
        pos_x += 1

    if key_event[pygame.K_UP]:
        pos_y -= 1

    if key_event[pygame.K_DOWN]:
        pos_y += 1
        
    if key_event[pygame.K_ESCAPE]:
        if VERBOSE:
            print("Terminated by ESC key")
        sys.exit()
    
    screen.fill(black)
    pygame.draw.circle(screen, white, (pos_x, pos_y), 20)
    pygame.display.update()

