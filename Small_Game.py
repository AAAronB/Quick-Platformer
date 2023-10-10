import pygame
from pygame.locals import *
import json

class Sprite:

   def __init__(self, picture_path, size):
       self.size = size
       sprite_img = pygame.image.load(picture_path)
       sprite_width=sprite_img.get_width()
       num_sprites = sprite_width // size
       self.sprite_list = []
       for i in range (num_sprites):
           sprite = pygame.Surface((size,size), pygame.SRCALPHA, 32)
           sprite.convert_alpha()
           sprite.blit(sprite_img.subsurface(pygame.Rect(i*size, 0, size, size)), (0, 0))
           self.sprite_list.append(sprite)

   def draw(self, surface, x, y, frame, flip=False):
       spr = self.sprite_list[frame%len(self.sprite_list)]
       if flip:
           spr = pygame.transform.flip(spr, True, False)
       surface.blit(spr,(x-self.size/2, y-self.size/2))

class Bounding_Box:
    def __init__(self, box_width, box_height, box_position):
        self.width = box_width
        self.height = box_height
        self.position = box_position
        self.left = box_position[0] - box_width / 2
        self.right = box_position[0] + box_width / 2
        self.top = box_position[1] + box_height / 2
        self.bottom = box_position[1] - box_height / 2

    def hit(self, box2):
        #print([self.left, self.right, self.top, self.bottom], [box2.left, box2.right, box2.top, box2.bottom])

        if self.right < box2.left or self.left > box2.right or self.top < box2.bottom or self.bottom > box2.top:
            return False
        else:
            return True

    def response(self, box2):
        #if self.hit(box2):
        Xdiff_left = box2.left - self.right
        Ydiff_up = box2.top - self.bottom
        Xdiff_right = box2.right - self.left
        Ydiff_down = box2.bottom - self.top

        #print('offs: ',[Xdiff_left,Xdiff_right,Ydiff_up,Ydiff_down])

        d = min([abs(Xdiff_left), abs(Ydiff_up), abs(Xdiff_right), abs(Ydiff_down)])

        #print(d, [abs(Xdiff_left), abs(Ydiff_up), abs(Xdiff_right), abs(Ydiff_down)])

        if d == abs(Xdiff_left):
            return [Xdiff_left, 0]
        if d == abs(Ydiff_up):
            return [0, Ydiff_up]
        if d == abs(Xdiff_right):
            return [Xdiff_right, 0]
        if d == abs(Ydiff_down):
            return [0, Ydiff_down]
        return [0, 0]

    def Draw(self):
        pygame.draw.rect(screen, (255, 0, 0))

class Items:
    def __init__(self,item_type,position,size):
        self.coin_sprite = Sprite("sprites/(1).png", 32)
        self.points = 0
        self.collided = False
        self.item_type = item_type
        self.position = position
        self.size = size
        self.frame = 0

    def bounding_box(self):
        return Bounding_Box(self.size[0],self.size[1],self.position)

    def draw_item(self,camera):
        self.frame += 1
        bbox=self.bounding_box()

        left, top = camera.transformation([self.position[0] - self.size[0] / 2, self.position[1] - self.size[1] / 2])
        right, bottom = camera.transformation([self.position[0] + self.size[0] / 2, self.position[1] + self.size[1] / 2])
        width = right - left
        height = top - bottom
        #pygame.draw.rect(camera.screen, (255, 255, 255), (left, top, width, height))
        self.coin_sprite.draw(camera.screen,left+width/2,top+height/2,self.frame//3)

        #screen.blit(self.coin_sprite, (left,top))

        #x_coord, y_coord = camera.transformation(self.position)
        #radius = self.size[0] * camera.camera_scale

        #pygame.draw.circle(camera.screen, (255, 255, 255), (x_coord, y_coord), width/2)

        #camera.screen.set_at((int(left+width/2), int(top+height/2)), (0, 0, 0))

class Character:
    friction = 2.5
    walk = 10
    jump = 350
    gravity = 9.8

    def __init__(self, position, character_width, character_height):
        self.run_sprite = Sprite("sprites/GraveRobber_run.png",48)
        self.jump_sprite = Sprite("sprites/GraveRobber_jump.png",48)
        self.idle_sprite = Sprite("sprites/GraveRobber_idle.png",48)
        self.position = position
        self.height = character_height
        self.width = character_width
        self.acceleration = [0, 0]
        self.velocity = [0, 0]
        self.grounded = True
        self.dash = 0 # timer for dash
        self.points = 0
        self.jump_counter = 0
        self.jump_wait = 0
        self.frame = 0

    def key_pressed(self):
        state = pygame.key.get_pressed()
        mods = pygame.key.get_mods()

        self.acceleration = [0, 0]
        if self.grounded == True:
            self.acceleration[0] -= Character.friction * self.velocity[0]
            if state[K_a] == True: # move left
                self.acceleration[0] -= Character.walk
            elif state[K_d] == True: # move right
                if self.dash<=0 and mods&KMOD_SHIFT > 0:
                    #print('DASH!!!')
                    self.velocity[0] += Character.walk*0.05 # dash using velocity not acceleration
                self.acceleration[0] += Character.walk
            elif state[K_RETURN] == True:  # jump
                #print('jump')
                self.acceleration[1] += Character.jump*0.5
                self.jump_counter = 1
                self.jump_wait = 10
                self.grounded = False
        else:
            self.acceleration[1] -= Character.gravity
            self.jump_wait -= 1

            if state[K_RETURN] == True and self.grounded == False:  # double jump
                if self.jump_counter == 1 and self.jump_wait <= 0:
                    self.jump_counter = 0
                    # self.jump_wait = 55
                    print('double jump!')
                    #self.velocity[1] = 0
                    self.acceleration[1] += Character.jump*1.25


    def update(self, timestep):
        self.position[0] = self.position[0] + self.velocity[0] * timestep
        self.position[1] = self.position[1] + self.velocity[1] * timestep
        self.velocity[0] = self.velocity[0] + self.acceleration[0] * timestep
        self.velocity[1] = self.velocity[1] + self.acceleration[1] * timestep
        self.grounded = False
        self.frame += 1


    def hit(self, bounding_box):
        char_box = Bounding_Box(self.width,self.height,self.position)
        if char_box.hit(bounding_box):
            return True
        else:
            return False

    def collide(self, bounding_box):
        character_box = Bounding_Box(self.width, self.height, self.position)
        #print('player', character_box.top, character_box.bottom, character_box.left, character_box.right)
        #print('platform', bounding_box.top, bounding_box.bottom, bounding_box.left, bounding_box.right)
        if character_box.hit(bounding_box):
            #print('hit')
            offset = character_box.response(bounding_box)
            #print(offset)
            self.position[0] += offset[0]
            self.position[1] += offset[1]
            if offset[1] > 0:
                self.grounded = True

            character_box = Bounding_Box(self.width, self.height, self.position)
            #print('player after hit', character_box.top, character_box.bottom, character_box.left, character_box.right)

    def draw(self, camera):
        #print('world player', self.position[0] - self.width / 2, self.position[1] - self.height / 2,
              #self.position[0] + self.width / 2, self.position[1] + self.height / 2)
        x, y = camera.transformation([self.position[0], self.position[1]])
        left, top = camera.transformation([self.position[0] - self.width / 2, self.position[1] + self.height / 2])
        right, bottom = camera.transformation([self.position[0] + self.width / 2, self.position[1] - self.height / 2])
        width = right - left
        height = bottom - top
        #print('screen player', left, top, right, bottom)
        #pygame.draw.rect(camera.screen, (255, 0, 0), (left, top, width, height))
        if self.grounded == True:
            if abs(self.velocity[0])<0.01:
                self.idle_sprite.draw(camera.screen, x, y, self.frame // 3, self.velocity[0] < 0)
            else:
                self.run_sprite.draw(camera.screen, x, y, self.frame//3, self.velocity[0]<0)
        else:
            self.jump_sprite.draw(camera.screen, x, y, self.frame//3, self.velocity[0]<0)


    def clamp(self, camera):
        screenWidth = camera.screen.get_width()
        screenHeight = camera.screen.get_height()
        if self.position[0] + (self.width // 2) >= screenWidth:
            self.position[0] = screenWidth - (self.width // 2)
        if self.position[0] - (self.width // 2) <= 0:
            self.position[0] = (self.width // 2)
        if self.position[1] - (self.height // 2) <= 0:
            self.position[1] = (self.height // 2)
        if self.position[1] + (self.height // 2) >= screenHeight:
            self.position[1] = screenHeight - (self.height // 2)


class Platform:
    def __init__(self, platform_position, platform_width, platform_height):
        self.platform_image = pygame.image.load("Platform.png")
        pwidth, pheight = self.platform_image.get_width(), self.platform_image.get_height()
        platform_scale = 64 / pheight
        self.platform_image = pygame.transform.scale(self.platform_image, (int(pwidth * platform_scale), int(pheight * platform_scale)))
        self.position = platform_position
        self.width = platform_width
        self.height = platform_height
        self.bounding_box = Bounding_Box(self.width, self.height, self.position)

    def draw(self, camera):
        #print('world platform', self.position[0] - self.width / 2, self.position[1] - self.height / 2, self.position[0] + self.width / 2, self.position[1] + self.height / 2)
        #left, top = camera.transformation([self.position[0] - self.width / 2, self.position[1] - self.height / 2])
        #right, bottom = camera.transformation([self.position[0] + self.width / 2, self.position[1] + self.height / 2])
        #platform_width = right - left
        #platform_height = top - bottom
        left, top = camera.transformation([self.position[0] - self.width / 2, self.position[1] + self.height / 2])
        right, bottom = camera.transformation([self.position[0] + self.width / 2, self.position[1] - self.height / 2])
        width = right - left
        height = bottom - top
        #platform_rect = pygame.rect(self.position[0],self.position[1],self.width,self.height)

        screen.blit(self.platform_image, (left-7, top - 15))
        for i in range(int(left-7), int(right-self.platform_image.get_width()), 25):
            screen.blit(self.platform_image, (i, top-15))
        screen.blit(self.platform_image, (right - self.platform_image.get_width(), top - 15))

        #pygame.draw.rect(camera.screen, (0,0,255), (left, top, width, height), 2, 3)
        #print('screen platform', left, top, right, bottom)
        #pygame.draw.rect(camera.screen, (0, 0, 128), (left, top, platform_width, platform_height))


class Camera:
    def __init__(self, camera_center, camera_scale, screen):
        self.camera_center = camera_center
        self.camera_scale = camera_scale
        self.screen = screen

    def transformation(self, coords):
        offsetX = coords[0] - self.camera_center[0]
        offsetY = coords[1] - self.camera_center[1]
        pixel_offsetX = offsetX * self.camera_scale
        pixel_offsetY = offsetY * self.camera_scale
        centerX = screen.get_width() / 2
        centerY = screen.get_height() / 2
        return centerX + pixel_offsetX, centerY - pixel_offsetY
        # return centerX + pixel_offsetX, centerY + pixel_offsetY !problem

    def points(self):
        if player.hit(item) == True:
            self.points += 100
            #print(self.points)
        if item[3] > 1:
            self.points += 500

class Enemy:
    def __init__(self, x, y, width, height, end):
        self.enemy_sprite = Sprite("sprites/SteamMan_walk.png", 48)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.path = [x, end]  # This will define where our enemy starts and finishes their path.
        self.walkCount = 0
        self.vel = 3
        self.frame = 0

    def draw(self, camera):
        self.frame += 1
        #self.move()
        #if self.walkCount + 1 >= 33:
        #    self.walkCount = 0

        x, y = camera.transformation([self.x, self.y])

        #if self.vel > 0:
        self.enemy_sprite.draw(camera.screen, 10, 10, self.frame // 3)
        #else:
            #self.enemy_sprite.draw(camera.screen, x, y, self.frame // 3)

    def move(self):
        if self.vel > 0:  # If we are moving right
            if self.x < self.path[1] + self.vel:  # If we have not reached the furthest right point on our path.
                self.x += self.vel
            else:  # Change direction and move back the other way
                self.vel = self.vel * -1
                self.x += self.vel
                self.walkCount = 0
        else:  # If we are moving left
            if self.x > self.path[0] - self.vel:  # If we have not reached the furthest left point on our path
                self.x += self.vel
            else:  # Change direction
                self.vel = self.vel * -1
                self.x += self.vel
                self.walkCount = 0

class Button:

    def __init__(self, x, y, text, foreground, background):
        self.x = x
        self.y = y
        self.text = text
        self.foreground = foreground
        self.background = background
        self.unselected = font.render(self.text, True, self.foreground, self.background)
        self.selected = font.render(self.text, True, self.background, self.foreground)
        self.rect = self.unselected.get_rect()
        self.rect.center = (x, y)

    def draw_button(self):
        if self.check_mouse():
            screen.blit(self.selected, self.rect)
        else:
            screen.blit(self.unselected, self.rect)

    def check_mouse(self):
        mouse = pygame.mouse.get_pos()
        if point_in_rect(mouse[0], mouse[1], self.rect.left, self.rect.top, self.rect.right - self.rect.left,
                         self.rect.bottom - self.rect.top) == True:
            return True
        else:
            return False

def point_in_rect(x, y, rx, ry, rw, rh):
    if x >= rx and x <= rx + rw and y >= ry and y <= ry + rh:
        return True
    else:
        return False



def draw_menu():
  global draw_func


  black = (0,0,0)
  white = (255,255,255)
  color_light = (170,170,170)
  green = (0,128,0)
  blue = 	(0,0,255)
  screen.fill((255,0,0))
  screen.blit(background_image,(0,0))
  text = font.render('Big AB Adventure', True, black, white)
  textRect = text.get_rect()
  textRect.center = (400, 50)
  screen.blit(text,textRect)
  #quit = font.render('quit' , True , white, color_light)
  #start = font.render('Start!', True, black, green)
  #textRect3 = text.get_rect()
  #textRect3.center = (425, 150)
  #screen.blit(start, textRect3)
  #textRect2 = text.get_rect()
  #textRect2.center = (425, 350)
  #screen.blit(quit,textRect2)
  #controls = font.render('controls',True, white, blue)
  #textRect4 = text.get_rect()
  #textRect4.center = (400, 250)
  #screen.blit(controls, textRect4)

  quit.draw_button()
  start.draw_button()
  controls.draw_button()

  #print(pygame.mouse.get_pressed()[0], start.check_mouse())
  if pygame.mouse.get_pressed()[0] and start.check_mouse() == True:
    draw_func = draw_game
  if pygame.mouse.get_pressed()[0] and controls.check_mouse() == True:
     draw_func = draw_controls

def draw_game():
    global platforms, items, points
    timestep = clock.tick(60) / 1000
    # game update code
    player.key_pressed()
    player.update(timestep)
    #print('--->')
    i=0
    for platform in platforms:
        #print(i)
        i+=1
        player.collide(platform.bounding_box)

    tmp=[]
    for item in items:
        if player.hit(item.bounding_box()) == True:
            # add points...
            points += 100
        else:
            tmp.append(item)
    items=tmp

    # drawing code

    # (width, height) = (400, 400)
    # screen = pygame.display.set_mode((width, height))

    screen.fill((0,0,0))
    background = pygame.image.load('Forest.png')
    background = pygame.transform.scale(background, (1000, 563))
    screen.blit(background,(0,0))
    text1 = font.render('Points:' + str(points), True, (255, 255, 255), (255, 0, 255))
    text1.set_alpha(100)
    Rect = text1.get_rect()
    Rect.center = (100, 25)
    screen.blit(text1, Rect)
    camera.camera_center = player.position



    player.draw(camera)
    for platform in platforms:
        platform.draw(camera)

    for item in items:
        item.draw_item(camera)

def draw_controls():
    global draw_func
    screen.fill((255,255,255))
    keyboard = pygame.image.load("Keyboard.png")
    keyboard = pygame.transform.scale(keyboard, (1000, 563))
    screen.blit(keyboard,(0,0))
    clock = pygame.time.Clock()
    control_text = font.render("Controls",True,(0,128,0),(255,255,255))
    textRect = control_text.get_rect()
    textRect.center = (600, 50)
    screen.blit(control_text, textRect)
    writing = font.render("W A S D to Move",True,(0,128,0),(255,255,255))
    textRect1 = writing.get_rect()
    textRect1.center = (700, 200)
    screen.blit(writing, textRect1)
    writing2 = font.render("Enter to Jump", True, (0, 128, 0),(255,255,255))
    textRect2 = writing2.get_rect()
    textRect2.center = (700, 230)
    screen.blit(writing2, textRect2)



pygame.init()
pygame.display.set_caption('Platforming Game')
screen = pygame.display.set_mode((1000, 563))
clock = pygame.time.Clock()

'''
run_img = pygame.image.load("sprites/GraveRobber_run.png")
run_sprite = []

for i in range(6):
    spr = pygame.Surface((48, 48), pygame.SRCALPHA, 32)
    spr = spr.convert_alpha()
    spr.blit(run_img.subsurface(pygame.Rect(i*48, 0, 48, 48)), (0, 0))
    run_sprite.append(spr)
'''
#run_sprite = Sprite("sprites/GraveRobber_run.png")
#jump_sprite = Sprite("sprites/GraveRobber_jump.png")
platform = pygame.image.load("Platform.png")
platform_width, platform_height = platform.get_width(), platform.get_height()
scale = 48/platform_height
platform = pygame.transform.scale(platform, (int(platform_width*scale), int(platform_height*scale)))
goblin = Enemy(1, 1, 1, 1, 6)

camera = Camera([-2, -1], 40, screen)

character_position = [0, 0]
character_width = 1
character_height = 1
player = Character(character_position, character_width, character_height)
points = 0

background_image = pygame.image.load('Pixelated_Wasteland.jpg')
background_image = pygame.transform.scale(background_image, (1000, 650))
font = pygame.font.Font('freesansbold.ttf', 32)

start = Button(425, 150, 'Start!', (0,0,0), (0,128,0))
quit = Button(425, 350, 'quit', (255,255,255), (170,170,170))
controls = Button(400, 250, 'controls', (255,255,255), (0,0,255))

draw_func=draw_menu
items = []
platforms = []
with open('level1.json') as level1:
    data = json.load(level1)
    for platform in data["platforms"]:
        #print(platform["x"], platform["y"])
        p=Platform([platform["x"], platform["y"]], platform["width"], platform["height"])
        platforms.append(p)
        print(p.bounding_box.top, p.bounding_box.bottom, p.bounding_box.left, p.bounding_box.right)
        #print(platforms[-1].position)
    for item in data["items"]:
        items.append(Items(item["type"],[item["x"],item["y"]],[item["width"],item["height"]]))
    goblin.draw(camera)
#move.clamp(camera)

i = 0
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                up = True
            elif event.key == pygame.K_s:
                down = True
            elif event.key == pygame.K_a:
                left = True
            elif event.key == pygame.K_d:
                right = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                up = False
            elif event.key == pygame.K_s:
                down = False
            elif event.key == pygame.K_a:
                left = False
            elif event.key == pygame.K_d:
                right = False
    draw_func()

    #print(i//100)
    #screen.blit(run_sprite[(i//100)%len(run_sprite)], (0, 0))
    #run_sprite.draw(screen, 0, 0, i//100, True)
    #jump_sprite.draw(screen, 48, 0, i // 100, True)
    i += 1


    pygame.display.update()
