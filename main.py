import pygame
from pygame import*
import random
import time

pygame.init()
clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 736
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird by Deep")

#define font

font = pygame.font.SysFont('Calibri', 70, bold=True)
color = 'white'

#Globle game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1450 #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
bird_hit = False


#load image
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
restart_img = pygame.image.load('img/restart.png')
title = pygame.image.load('img/title.png')
resized_title = pygame.transform.rotozoom(title,0,0.5)

#load sound
game_sound = {}
game_sound['point'] = pygame.mixer.Sound('sound\point.mp3')
game_sound['hit'] = pygame.mixer.Sound('sound\hit.mp3')
game_sound['flap'] = pygame.mixer.Sound('sound/flap.mp3')
game_sound['die'] = pygame.mixer.Sound('sound\die.mp3')
game_sound['swoosh'] = pygame.mixer.Sound('sound\swoosh.mp3')


#Globle Functions:

def restart():
    global bird_hit
    global pipe_frequency
    global scroll_speed
    bird_hit = False
    pipe_group.empty()
    flappy.rect.x = 150
    flappy.rect.y = int(screen_height/2.3)
    score = 0
   #flappy.rect.center = (150,int(screen_height/2.3))
    flappy.vel = 0
    pipe_frequency = 1450 #milliseconds
    scroll_speed = 4


    return score
     

def text_draw(text, font, color, x, y):
    img = font.render(text,True,color,)
    screen.blit(img, (x,y))

class Bird(pygame.sprite.Sprite):
    def __init__(self, x ,y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range (1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x , y]
        self.vel = 0
    


    def update(self):
        if flying == True:
            #Gravity
            self.vel += 0.5
            if self.vel > 7:
                self.vel = 7
            if self.rect.bottom <= 568:
                self.rect.y += int(self.vel)

        if game_over == False:
            #bird animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            #jump animation
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

    def jump(self):         #jump function
        if game_over == False:
            self.vel = -6
            if scroll_speed >= 6 and self.vel<= -7:
                self.vel += -0.5
            game_sound['flap'].play()
            



class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load('img/pipe.png')
        self.rect=self.image.get_rect()
        #if position is 1 btm_pipe if -1 top_pipe
        if position == 1:
            self.rect.topleft = [x, y + int(pipe_gap/2)]
        if position == -1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft=[x,y - int(pipe_gap/2)]  
    
    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()



class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


    def draw(self):
        #Click on restart btn:
        restart = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                restart = True
                #global flying 
                #flying = False
        
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return restart



bird_group = pygame.sprite.Group()
flappy = Bird(150, int(screen_height/2.3))
bird_group.add(flappy)
pipe_group = pygame.sprite.Group()

button = Button((screen_width/2 - 50),(screen_height/2 - 50),restart_img)


run = True
while run:

    clock.tick(fps)
    screen.blit(bg, (0,-120))


    #bird
    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)    #pipe
    
    screen.blit(ground_img, (ground_scroll,568))


    #score count logic
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.left < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True
            game_sound['swoosh'].play()
        if pass_pipe == True and bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
            score += 1
            if score % 4 == 0 and scroll_speed <= 12:
                scroll_speed += .5
                if pipe_frequency >= 1200:
                    pipe_frequency -= 50
            game_sound['point'].play()
            pass_pipe = False
    text_draw(str(score),font,color,int(screen_width/2 - 20),40)


    #bird & pipe collision
    if pygame.sprite.groupcollide(bird_group,pipe_group, False, False) or flappy.rect.top < 0:
        if not game_over:
            game_over = True
            if not bird_hit:
                game_sound['hit'].play()
                bird_hit = True
            game_sound['die'].play()



    #ground hit part
    if flappy.rect.bottom >= 568:
        if not game_over:
            game_over= True
            flying= False
            if not bird_hit:
                game_sound['hit'].play()

    if game_over == False:

        #Pipe Generate logic
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency and flying == True:
            pipe_height = random.randint(-170,100)
            btm_pipe = Pipe(screen_width, int(screen_height/2) + pipe_height, 1)
            top_pipe = Pipe(screen_width, int(screen_height/2) + pipe_height, -1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        ground_scroll -= scroll_speed     #Ground_scroll animation 
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pipe_group.update()


    #Restart btn :
    if game_over==True:
        if button.draw() == True:
            game_over = False
            flying = False
            score = restart()

    #Title part
    if game_over == True or flying == False:
        screen.blit(resized_title, ((screen_width/2 - 245),(screen_height/2 -250)))
    
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP) and flying == False:
            flying = True

        if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
           flappy.jump()

        

    pygame.display.update()
pygame.QUIT