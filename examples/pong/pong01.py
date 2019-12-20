import os
import random
import pygame
pygame.init()

P = [1,1,1,1, 1,0,0,1, 1,1,1,1, 1,0,0,0, 1,0,0,0]

O = [1,1,1,1, 1,0,0,1, 1,0,0,1, 1,0,0,1, 1,1,1,1]

N = [1,0,0,1, 1,0,0,1, 1,1,0,1, 1,0,1,1, 1,0,0,1]

G = [1,1,1,1, 1,0,0,0, 1,0,1,1, 1,0,0,1, 1,1,1,1]

zero = [1,1,1,1, 1,0,0,1, 1,0,0,1, 1,0,0,1, 1,1,1,1]

one = [0,0,1,0, 0,1,1,0, 0,0,1,0, 0,0,1,0, 1,1,1,1]

two = [0,1,1,0, 1,0,0,1, 0,0,1,0, 0,1,0,0, 1,1,1,1]

three = [1,1,1,0, 0,0,0,1, 1,1,1,0, 0,0,0,1, 1,1,1,0]

four = [1,0,1,0, 1,0,1,0, 1,1,1,1, 0,0,1,0, 0,0,1,0]

size = (900,700)
screen = pygame.display.set_mode(size)

done = False

clock = pygame.time.Clock()

WHITE = (255,255,255)
GREY = (128,128,128)
BLACK = (0,0,0)

program_state = 0

difficulty = 6  #6: Easy, 4: Medium, 2: Hard

font = pygame.font.Font("FFFFORWA.ttf",16)

def character(character,x,y,size):
    for a in range(5):
        for b in range(4):
            if character[((a * 4) + b)] == 1:
                pygame.draw.rect(screen,WHITE,((x + (b * size)),(y + (a * size)),size,size))

def clickedIn(x,y,width,height):
    if mouse_state == 1 and mouse_x >= x and mouse_x <= (x + width) and mouse_y >= y and mouse_y <= (y + height):
        return True

def clickedOut(x,y,width,height):
    if mouse_state == 1 and mouse_x < x or mouse_state == 1 and mouse_x > (x + width) or mouse_state == 1 and mouse_y < y or mouse_state == 1 and mouse_y > (y + height):
        return True

def hovering(x,y,width,height):
    if mouse_state == 0 and mouse_x >= x and mouse_x <= (x + width) and mouse_y >= y and mouse_y <= (y + height):
        return True

def clickButton(x,y,width,height,normalColor,hoverColor,textFont,text,textColor,stateHolding = False,stateVariable = 0,state = 1):
    if not clickedIn(x,y,width,height) and not hovering(x,y,width,height):
        pygame.draw.rect(screen,normalColor,(x,y,width,height))
    if hovering(x,y,width,height):
        pygame.draw.rect(screen,hoverColor,(x,y,width,height))
    if stateHolding == True:
        if stateVariable == state:
            pygame.draw.rect(screen,hoverColor,(x,y,width,height))
    buttonText = textFont.render(text,True,textColor)
    buttonText_x = buttonText.get_rect().width
    buttonText_y = buttonText.get_rect().height
    screen.blit(buttonText,(((x + (width / 2)) - (buttonText_x / 2)),((y + (height / 2)) - (buttonText_y / 2))))
    if clickedIn(x,y,width,height):
        return True

def net():
    for i in range(17):
        pygame.draw.rect(screen,WHITE,(440,((40 * i) + 20),20,20))

class Ball():
    
    def __init__(self):
        self.width = 20
        self.height = 20
        self.x = 440
        self.y = 340
        self.change_x = 20
        self.change_y = 20
        self.color = WHITE
        self.score = 0
    
    def draw(self):
        pygame.draw.rect(screen,self.color,(self.x,self.y,self.width,self.height))
    
    def move(self):
        self.x += self.change_x
        self.y += self.change_y
    
    def update(self):


        if self.y <= 0:
            self.change_y *= -1
        elif self.y >= 680:
            self.change_y *= -1
        
        if self.x <= 60 and self.x >= 40 and self.y >= hpaddle.y and self.y < (hpaddle.y + hpaddle.height):
            self.change_x *= -1
            self.score += 1
        elif self.x >= 820 and self.x <= 840 and self.y >= aipaddle.y and self.y < (aipaddle.y + aipaddle.height):
            self.change_x *= -1
        
        if self.x <= 0:
            aipaddle.score += 1
            self.x = 440
            self.y = 340
            self.change_x *= -1
        
        if self.x >= 880:
            hpaddle.score += 1
            self.x = 440
            self.y = 340
            self.change_x *= -1

class Paddle():
    
    def __init__(self):
        self.width = 20
        self.height = 150
        self.x = 0
        self.y = 200
        self.color = WHITE
        self.score = 0
    
    def draw(self):
        pygame.draw.rect(screen,self.color,(self.x,self.y,self.width,self.height))

ball = Ball()

hpaddle = Paddle()
hpaddle.x = 40

aipaddle = Paddle()
aipaddle.x = 840


# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_state = 1
        else:
            mouse_state = 0
	   
    mouse_x = pygame.mouse.get_pos()[0]
    mouse_y = pygame.mouse.get_pos()[1]
    
    screen.fill(BLACK)
    
    #Menu
    if program_state == 0:
        
        character(P,300,150,15)
        character(O,380,150,15)
        character(N,460,150,15)
        character(G,540,150,15)
        
        if clickButton(350,325,200,50,WHITE,GREY,font,"START",BLACK,stateHolding = False,stateVariable = 0,state = 1) == True:
            program_state = 1
            ball.x = 440
            ball.y = 340
            hpaddle.score = 0
            aipaddle.score = 0
        
        if clickButton(200,425,100,50,WHITE,GREY,font,"EASY",BLACK,True,difficulty,6) == True:
            difficulty = 6
            ball.change_x = 5
            ball.change_y = 5
        
        if clickButton(400,425,100,50,WHITE,GREY,font,"MEDIUM",BLACK,True,difficulty,4) == True:
            difficulty = 4
            ball.change_x = 10
            ball.change_y = 10
        
        if clickButton(600,425,100,50,WHITE,GREY,font,"HARD",BLACK,True,difficulty,2) == True:
            difficulty = 2
            ball.change_x = 15
            ball.change_y = 15
    
    #Game
    elif program_state == 1:
        
        if hpaddle.score == 0:
            character(zero,370,30,10)
        
        elif hpaddle.score == 1:
            character(one,370,30,10)
        
        elif hpaddle.score == 2:
            character(two,370,30,10)
        
        elif hpaddle.score == 3:
            character(three,370,30,10)
        
        elif hpaddle.score == 4:
            character(four,370,30,10)
        
        elif hpaddle.score == 5:
            program_state = 2
        
        if aipaddle.score == 0:
            character(zero,490,30,10)
        
        elif aipaddle.score == 1:
            character(one,490,30,10)
        
        elif aipaddle.score == 2:
            character(two,490,30,10)
        
        elif aipaddle.score == 3:
            character(three,490,30,10)
        
        elif aipaddle.score == 4:
            character(four,490,30,10)
        
        elif aipaddle.score == 5:
            program_state = 2
        
        net()
        
        ball.draw()
        ball.move()
        ball.update()
        
        hpaddle.draw()
        #hpaddle.y = (ball.y - 75)
        hpaddle.y = mouse_y - 75
        
        aipaddle.draw()
        aipaddle.y = (ball.y - 75)
    
    #End Screen
    elif program_state == 2:
        
        character(P,300,150,15)
        character(O,380,150,15)
        character(N,460,150,15)
        character(G,540,150,15)
        
        scoreText = font.render(str(hpaddle.score) + ":" + str(aipaddle.score),True,WHITE)
        scoreText_x = scoreText.get_rect().width
        scoreText_y = scoreText.get_rect().height
        screen.blit(scoreText,((450 - (scoreText_x / 2)),(425 - (scoreText_y / 2))))
        
        if hpaddle.score == 5:
            winText = font.render("You Won!",True,WHITE)
            winText_x = winText.get_rect().width
            winText_y = winText.get_rect().height
            screen.blit(winText,((450 - (winText_x / 2)),(375 - (winText_y / 2))))
        
        if aipaddle.score == 5:
            loseText = font.render("You Lose!",True,WHITE)
            loseText_x = loseText.get_rect().width
            loseText_y = loseText.get_rect().height
            screen.blit(loseText,((450 - (loseText_x / 2)),(375 - (loseText_y / 2))))
        
        if clickButton(350,525,200,50,WHITE,GREY,font,"REPLAY",BLACK,stateHolding = False,stateVariable = 0,state = 1) == True:
            program_state = 0
            ball.x = 440
            ball.y = 340
            hpaddle.score = 0
            aipaddle.score = 0
    
    pygame.display.flip()
    
    pygame.display.set_caption("Pong, FPS: " + str(clock.get_fps()))
    
    clock.tick(60)

pygame.quit()