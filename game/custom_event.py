# -*- coding: utf-8 -*-

import pygame
import sys
from audio_input import AudioInput
from threading import Thread

def pygame_threadf():
    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 480
    
    white = (255, 255, 255)
    black = (0, 0, 0)
    
    pygame.init()
    
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
            sys.exit()
        
        screen.fill(black)
        pygame.draw.circle(screen, white, (pos_x, pos_y), 20)
        pygame.display.update()

pygame_thread = Thread(target=pygame_threadf)
pygame_thread.start()
audio_input = AudioInput()
audio_input.start_stream(onset_thres=0.035, verbose=True)
