import pygame
from audio_input import AudioInput
from random import randint
import sys

VERBOSE = True

#Define Colors - RGB
black = (0,0,0)
white = (255,255,255)
green = (0,255,0)
red = (255,0,0)

pygame.init()

audio_input = AudioInput()
audio_input.launch(onset_thres=0.035, verbose=VERBOSE, accept_band=[80, 1200])

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

FRAME_MULTIPLIER = 1 # must be integer

HOLD_FRAME = 8
DEFAULT_YSPEED = 2 * FRAME_MULTIPLIER
UP_YSPEED = -5 * FRAME_MULTIPLIER
DOWN_YSPEED = 4 * FRAME_MULTIPLIER
HOLD_UP_YSPEED = -5 * FRAME_MULTIPLIER
HOLD_DOWN_YSPEED = 3 * FRAME_MULTIPLIER
OBSPEED = 1 * FRAME_MULTIPLIER
INPUT_TOGGLE = False

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
obspeed = OBSPEED
score = 0
hold_count = 0

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            audio_input.terminate()
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                y_speed = -10
                INPUT_TOGGLE = ~INPUT_TOGGLE
                if VERBOSE:
                    print("input toggle")
#
#        if event.type == pygame.KEYUP:
#            if event.key == pygame.K_UP:
#                y_speed = 5
        if event.type == AudioInput.AudioInputEventType:
            if INPUT_TOGGLE:
                # audio input down-key mode
                y_speed = DOWN_YSPEED
                hold_count = int(round(HOLD_FRAME/3*2))
            else:
                # audio input up-key mode
                y_speed = UP_YSPEED
                hold_count = HOLD_FRAME
            
            
            
    key_event = pygame.key.get_pressed()
    if key_event[pygame.K_ESCAPE]:
        audio_input.terminate()
        if VERBOSE:
            print("Terminated by ESC key")
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
        done = True

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
        if INPUT_TOGGLE:
            y_speed = HOLD_DOWN_YSPEED
            hold_count -= 1
        else:
            y_speed = HOLD_UP_YSPEED
            hold_count -= 1
    else:
        y_speed = DEFAULT_YSPEED

    pygame.display.flip()
    clock.tick(30)

pygame.quit()