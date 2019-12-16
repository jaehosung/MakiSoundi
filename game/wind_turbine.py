import pygame as pg
from audio_input import AudioInput
import sys 
import numpy as np

VERBOSE = True

AudioInputUpType = pg.USEREVENT+1
AudioInputUpEvent = pg.event.Event(AudioInputUpType)

AudioInputDownType = pg.USEREVENT+2
AudioInputDownEvent = pg.event.Event(AudioInputDownType)

audio_input = AudioInput(onset_thres=0.035, verbose=VERBOSE)
audio_input.add_onset_action(pg.event.post, AudioInputUpEvent, accept_band=[1000, 4000])
audio_input.add_onset_action(pg.event.post, AudioInputDownEvent, accept_band=[50, 999])
audio_input.launch()

screen = pg.display.set_mode((1440,1300))
screen_rect = screen.get_rect()
clock = pg.time.Clock()
done = False

SCREEN_X = 1440
SCREEN_Y = 1300
BAR_XW = 100
BAR_X = (SCREEN_X-BAR_XW)//2 
BAR_YW = 1000
BAR_Y = (SCREEN_Y)//2-70

SKY_COLOR = (2, 128, 189)

class Rotator:
    def __init__(self, screen_rect):
        self.screen_rect = screen_rect
        self.master_image = pg.image.load('Artboard 6.png')
        self.image = self.master_image.copy()
        self.rect = self.image.get_rect(center=self.screen_rect.center)
        self.delay = 10
        self.timer = 0.0
        self.angle = 0
        self.angular_vel = 0
    
    def accel_cw(self):
        self.angular_vel += 256
    
    def accel_ccw(self):
        self.angular_vel -= 256
    
    def new_angle(self):
        self.angle += int(np.floor(self.angular_vel/64))
        self.angle %= 360
        angular_accel = max(np.abs(self.angular_vel/64), 1)
        if self.angular_vel > angular_accel:
            self.angular_vel -= angular_accel
        elif self.angular_vel < -angular_accel:
            self.angular_vel += angular_accel
        else:
            self.angular_vel = 0
 
    def rotate(self):
        self.new_angle()
        self.image = pg.transform.rotate(self.master_image, self.angle)
        self.rect = self.image.get_rect(center=self.screen_rect.center)
 
    def update(self):
        if pg.time.get_ticks()- self.timer > self.delay:
            self.timer = pg.time.get_ticks()
            self.rotate()
 
    def draw(self, surf):
        surf.blit(self.image, self.rect)
 
rotator = Rotator(screen_rect)
clock = pg.time.Clock()

while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        if event.type == AudioInputUpType:
            # audio input counter-clockwise mode
            rotator.accel_ccw()
        if event.type == AudioInputDownType:
            # audio input clockwise mode
            rotator.accel_cw()
        
    key_event = pg.key.get_pressed()
    if key_event[pg.K_ESCAPE]:
        audio_input.terminate()
        if VERBOSE:
            print("Terminated by ESC key")
        done = True
        sys.exit()
    screen.fill(SKY_COLOR)
    pg.draw.rect(screen,(255, 255, 255),[BAR_X, BAR_Y, BAR_XW, BAR_YW])
    pg.draw.rect(screen,(0, 0, 0),[BAR_X, BAR_Y, BAR_XW, BAR_YW], 10)
    rotator.update()
    rotator.draw(screen)
    pg.display.update()
    clock.tick(30)