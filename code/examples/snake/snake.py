import random
import pygame
pygame.init()

class Button():
    def __init__(self):
        self.textBoxes = {}
    
    #----Clicked In----
    def clickedIn(self,x,y,width,height):
        global mouse_state, mouse_x, mouse_y
        if mouse_state == 1 and mouse_x >= x and mouse_x <= (x + width) and mouse_y >= y and mouse_y <= (y + height):
            return True

    #----Clicked Out----
    def clickedOut(self,x,y,width,height):
        global mouse_state, mouse_x, mouse_y
        if mouse_state == 1 and mouse_x < x or mouse_state == 1 and mouse_x > (x + width) or mouse_state == 1 and mouse_y < y or mouse_state == 1 and mouse_y > (y + height):
            return True

    #----Hovering----
    def hovering(self,x,y,width,height):
        global mouse_state, mouse_x, mouse_y
        if mouse_state == 0 and mouse_x >= x and mouse_x <= (x + width) and mouse_y >= y and mouse_y <= (y + height):
            return True
    
    #----Click Button----
    def clickButton(self,x,y,width,height,normalColor,hoverColor,textFont,text,textColor,stateHolding = False,stateVariable = 0,state = 1):
        if not self.clickedIn(x,y,width,height) and not self.hovering(x,y,width,height):
            pygame.draw.rect(screen,normalColor,(x,y,width,height))
        elif self.hovering(x,y,width,height):
            pygame.draw.rect(screen,hoverColor,(x,y,width,height))
        if stateHolding == True and stateVariable == state:
            pygame.draw.rect(screen,hoverColor,(x,y,width,height))
        buttonText = textFont.render(text,True,textColor)
        buttonText_x = buttonText.get_rect().width
        buttonText_y = buttonText.get_rect().height
        screen.blit(buttonText,(((x + (width / 2)) - (buttonText_x / 2)),((y + (height / 2)) - (buttonText_y / 2))))
        if self.clickedIn(x,y,width,height):
            return True

WHITE = (255,255,255)
GREY = (127,127,127)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
DGREEN = (0,127,0)

font = pygame.font.SysFont('Comic Sans MS',20)

size = (600,700)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Snake")

done = False

clock = pygame.time.Clock()

scale = 30

class Snake():
    def __init__(self):
        self.alive = True
        self.length = 1
        self.tail = []
        self.x = 0
        self.y = 0
        self.xV = 0
        self.yV = 1
        self.tick = 0
    
    def draw(self):
        for section in self.tail:
            pygame.draw.rect(screen,WHITE,(((section[0]) * scale),((section[1]) * scale) + 100,scale,scale))
    
    def update(self):
        if self.alive == True:
            if self.tick == 10:
                self.x += self.xV
                self.y += self.yV
                for segment in self.tail:
                    if segment[0] == self.x and segment[1] == self.y:
                        self.alive = False
                self.tick = 0
                self.tail.append((self.x,self.y))
            else:
                self.tick += 1
            while len(self.tail) > self.length:
                self.tail.pop(0)
        if self.x == -1:
            self.alive = False
            self.x = 0
        if self.x == (size[0] / scale):
            self.alive = False
            self.x = (size[0] / scale) - 1
        if self.y == -1:
            self.alive = False
            self.y = 0
        if self.y == (size[1] - 100) / scale:
            self.alive = False
            self.y = ((size[1] - 100) / scale) - 1
    
    def reset(self):
        self.alive = True
        self.length = 1
        self.tail.clear()
        self.x = 0
        self.y = 0
        self.xV = 0
        self.yV = 1
        self.tick = 0

class Food():
    def __init__(self):
        self.x = random.randrange((size[0] / scale) - 1)
        self.y = random.randrange(((size[1] - 100) / scale) - 1)
    
    def draw(self):
        pygame.draw.rect(screen,RED,((self.x * scale),(self.y * scale) + 100,scale,scale))
    
    def update(self):
        if snake.x == self.x and snake.y == self.y:
            self.reset()
            snake.length += 1
    
    def reset(self):
        self.x = random.randrange((size[0] / scale) - 1)
        self.y = random.randrange(((size[1] - 100) / scale) - 1)

class Utility():
    def __init__(self):
        return
    
    def draw(self):
        text = font.render("Length: " + str(snake.length),True,BLACK)
        text_y = text.get_rect().height
        screen.blit(text,(90,(50 - (text_y / 2))))
        text = font.render("Alive: " + str(snake.alive),True,BLACK)
        text_y = text.get_rect().height
        screen.blit(text,(size[0] - 210,(50 - (text_y / 2))))
        pygame.draw.line(screen,BLACK,(0,100),(size[0],100),7)
        if snake.alive == False:
            if button.clickButton((size[0] / 2) - 75,25,150,50,GREEN,DGREEN,font,"Play Again",WHITE):
                snake.reset()
                food.reset()
        
        for i in range(int(size[0] / scale) - 1):
            pygame.draw.line(screen,BLACK,(0,(100 + (i * scale) + scale)),(size[0],(100 + (i * scale) + scale)),3)
            pygame.draw.line(screen,BLACK,(((i * scale) + scale),100),(((i * scale) + scale),size[1]),3)
    
    def update(self):
        return

button = Button()
snake = Snake()
food = Food()
utility = Utility()

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_state = 1
            pygame.mouse.set_pos(mouse_x,mouse_y + 1)
        else:
            mouse_state = 0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                snake.yV = 0
                snake.xV = -1
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                snake.yV = 0
                snake.xV = 1
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                snake.xV = 0
                snake.yV = -1
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                snake.xV = 0
                snake.yV = 1
    
    mouse_x = pygame.mouse.get_pos()[0]
    mouse_y = pygame.mouse.get_pos()[1]
    
    pygame.display.set_caption("Snake, FPS: " + str(clock.get_fps()))
    
    screen.fill(GREY)
    
    snake.update()
    food.update()
    utility.update()
    food.draw()
    snake.draw()
    utility.draw()
    
    pygame.display.flip()
    
    clock.tick(50)

pygame.quit()