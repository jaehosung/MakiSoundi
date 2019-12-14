import pygame
from audio_input import AudioInput
from threading import Thread
from random import randint
import sys

VERBOSE = True
# audio input thread
def audio_threadf(audio_input):
    global VERBOSE
    audio_input.start_stream(onset_thres=0.035, verbose=VERBOSE, accept_band=[80, 1200])

#Define Colors - RGB
black = (0,0,0)
white = (255,255,255)
green = (0,255,0)
red = (255,0,0)

pygame.init()

audio_input = AudioInput()
audio_thread = Thread(target=audio_threadf, daemon=True, args=(audio_input,))
audio_thread.start()

#Screen Size
size = 700,500
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Flappy Bird in Python by @KartikKannapur")

done = False
clock = pygame.time.Clock()

def ball(x,y):
    #Radius of 20 px
    pygame.draw.circle(screen,black,[x,y],20)

def gameover():
    font = pygame.font.SysFont(None,55)
    text = font.render("Game Over! Try Again",True,red)
    screen.blit(text, [150,250])

def obstacle(xloc,yloc,xsize,ysize):
    pygame.draw.rect(screen,green,[xloc,yloc,xsize,ysize])
    pygame.draw.rect(screen,green,[xloc,int(yloc+ysize+space),xsize,ysize+500])

#If the ball is between 2 points on the screen, increment score
def Score(score):
    font = pygame.font.SysFont(None,55)
    text = font.render("Score: "+str(score),True,black)
    screen.blit(text, [0,0])

def terminate():
    audio_input._terminate_stream()
    audio_thread.join()

HOLD_FRAME = 15
DEFAULT_YSPEED = 2

x = 350
y = 250
x_speed = 0
y_speed = DEFAULT_YSPEED
ground = 477
xloc = 700
yloc = 0
xsize = 70
ysize = randint(0,350)
#Size of space between 2 blocks
space = 150
obspeed = 1
score = 0
hold_count = 0

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
            done = True
#        if event.type == pygame.KEYDOWN:
#            if event.key == pygame.K_UP:
#                y_speed = -10
#
#        if event.type == pygame.KEYUP:
#            if event.key == pygame.K_UP:
#                y_speed = 5
        if event.type == AudioInput.AudioInputEventType:
            print("hold")
            y_speed = -5
            hold_count = HOLD_FRAME
            
            
    key_event = pygame.key.get_pressed()
    if key_event[pygame.K_ESCAPE]:
        if VERBOSE:
            print("Terminated by ESC key")
        terminate()
        done = True
        sys.exit()
    
    screen.fill(white)
    obstacle(xloc,yloc,xsize,ysize)
    ball(x,y)
    Score(score)

    y += y_speed
    xloc -= obspeed

    if y > ground:
        gameover()
        y_speed = 0
        obspeed = 0

    if x+20 > xloc and y-20 < ysize and x-15 < xsize+xloc:
        gameover()
        y_speed = 0
        obspeed = 0

    if x+20 > xloc and y+20 < ysize and x-15 < xsize+xloc:
        gameover()
        y_speed = 0
        obspeed = 0

    if xloc < -80:
        xloc = 700
        ysize = randint(0,350)

    if x > xloc and x < xloc+3:
        score = score + 1
    
    if hold_count > 0:
        y_speed = -3
        hold_count -= 1
    else:
        y_speed = DEFAULT_YSPEED

    pygame.display.flip()
    clock.tick(60)

pygame.quit()