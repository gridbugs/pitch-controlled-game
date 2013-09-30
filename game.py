import os, sys
import pygame
from pygame.locals import *
import random

from config import *
import mic

nyan = False

# some geom helpers
def below(a, b):
  return a[1] > b[1]

def above(a, b):
  return a[1] < b[1]

def left_of(a, b):
  return a[0] < b[0]

def right_of(a, b):
  return a[0] > b[0]

def rects_overlap(a_tl, a_br, b_tl, b_br):
  return below(a_br, b_tl) and right_of(a_br, b_tl) and above(a_tl, b_br) and left_of(a_tl, b_br)

class Star:
  def __init__(self, images):
    self.tick_delay = 5
    self.tick_wait = self.tick_delay
    self.state_range = 5
    self.state = int(random.random() * self.state_range)
    self.images = images
    self.move()

  def move(self):
    x = int(random.random() * WIDTH)
    y = int(random.random() * HEIGHT)

    self.pos = (x, y)
    
  def tick(self):
    if self.tick_wait == 0:
      self.pos = (self.pos[0] - 5, self.pos[1])
      self.state += 1
      if self.state == self.state_range:
        self.state = 0
        self.move()
      self.tick_wait = self.tick_delay
    else:
      self.tick_wait -= 1
      

  def draw(self, surface):
    surface.blit(self.images[self.state], self.pos)
    

class World:
  def __init__(self, top, bottom):
    self.top = top
    self.bottom = bottom
    self.speed = 7

    full = pygame.image.load("skyline.png")
    self.fg = pygame.transform.scale(full, (WIDTH, HEIGHT))
    self.offset = 600

    self.load_images(["b1.png", "b2.png", "b3.png", "b4.png", "b5.png"])

    self.stars = map(lambda x: Star(self.images), range(0, 20))

    self.nyan = False

  def load_images(self, images):
    self.images = map(pygame.image.load, images)

    self.images = []
    for i in images:
      tmp = pygame.image.load(i)
      self.images.append(pygame.transform.scale(tmp, (int(tmp.get_width() * 1), int(tmp.get_height() * 1))))

  def draw_fg(self, surface):
    if self.nyan:
      map(lambda x: x.draw(surface), self.stars)
    remaining = self.fg.get_width() - self.offset
    if remaining > WIDTH:
      surface.blit(self.fg, (0, 0), (self.offset, 0, WIDTH, self.fg.get_height()))
    else:
      surface.blit(self.fg, (0, 0), (self.offset, 0, remaining, self.fg.get_height()))
      surface.blit(self.fg, (remaining, 0), (0, 0, WIDTH - remaining, self.fg.get_height()))
  def tick(self):
    self.offset = (self.offset - 4) % self.fg.get_width()

    map(lambda x: x.tick(), self.stars)

class Enemy:
  def __init__(self, world, height_percent, start_x, sprite):
    self.world = world
    self.sprite = pygame.image.load(sprite)
    self.pos = (start_x, world.top + (height_percent * (world.bottom - world.top - self.sprite.get_height())))
  def draw(self, screen):
    screen.blit(self.sprite, (self.pos[0], self.pos[1], self.sprite.get_width(), self.sprite.get_height()))

  def progress(self):
    self.pos = (self.pos[0] + world.speed, self.pos[1])

  def top_left(self):
    return self.pos

  def bottom_right(self):
    return (self.pos[0] + self.sprite.get_width(), self.pos[1] + self.sprite.get_height())

  def check_collision(self, ch):
    return rects_overlap(self.top_left(), self.bottom_right(), ch.top_left(), ch.bottom_right())

class Character:
  def __init__(self, world, pos, step):
    self.world = world
    self.pos = pos
    self.step = step
    self.vvel = 0
    self.max_vvel = 3
    self.vvel_step = 2

    self.load_images(["s1.png", "s2.png", "s3.png", "s4.png"])
    self.load_nyan(["n1.png", "n2.png", "n3.png", "n4.png",
                    "n5.png", "n6.png", "n7.png", "n8.png",
                    "n9.png", "n10.png", "n11.png", "n12.png"])
    self.load_image("s1.png", 1)

    self.frame = 0
    self.frame_duration = 4
    self.frame_wait = self.frame_duration

  def become_nyan(self):
    self.images = self.nyans

  def load_images(self, images):
    self.images = map(pygame.image.load, images)

    self.images = []
    for i in images:
      tmp = pygame.image.load(i)
      self.images.append(pygame.transform.scale(tmp, (int(tmp.get_width() * CHAR_SCALE), int(tmp.get_height() * CHAR_SCALE))))
  def load_nyan(self, images):
    self.nyan = map(pygame.image.load, images)

    self.nyans = []
    for i in images:
      tmp = pygame.image.load(i)
      self.nyans.append(pygame.transform.scale(tmp, (int(tmp.get_width() * CHAR_SCALE), int(tmp.get_height() * CHAR_SCALE))))


  def move_up(self):
    self.vvel = max(self.vvel - self.vvel_step, -self.max_vvel)

  def move_down(self):
    self.vvel = min(self.vvel + self.vvel_step, self.max_vvel)

  def acc(self):
    self.pos = (self.pos[0], min(max(self.pos[1] + self.vvel, self.world.top), self.world.bottom))
    self.vvel = int(self.vvel*0.9)

  def load_image(self, file_name, scale):
    orig = pygame.image.load(file_name)
    self.image = pygame.transform.scale(orig, (int(orig.get_width() * CHAR_SCALE), int(orig.get_height() * CHAR_SCALE)))

  def draw(self, screen):
    screen.blit(self.images[self.frame], (self.pos[0], self.pos[1], self.image.get_width()*2, self.image.get_height()*2))

  def top_left(self):
    return self.pos

  def bottom_right(self):
    return (self.pos[0] + self.image.get_width(), self.pos[1] + self.image.get_height())

  def tick(self):
    if self.frame_wait == 0:
      self.frame = (self.frame + 1) % len(self.images)
      self.frame_wait = self.frame_duration
    else:
      self.frame_wait -= 1

class Control:
  def __init__(self):
    self.up = False
    self.flat = True

  def set_up(self):
    self.flat = False
    self.up = True

  def set_down(self):
    self.flat = False
    self.up = False

class Game:
  def __init__(self, world, character, control):
    self.world = world
    self.character = character
    self.control = control

  def progress(self):
    if control.flat:
      pass
    elif control.up:
      self.character.move_up()
    else:
      self.character.move_down()

    self.character.acc()

pygame.init()
mic = mic.Mic()
surface = pygame.display.set_mode((WIDTH,HEIGHT))
FPS = 33
clock = pygame.time.Clock()

world = World(10, HEIGHT - 60)
control = Control()

def change_to_nyan(world, character):
  character.become_nyan()
  world.nyan = True
  nyan = True

while True:

  character = Character(world, (WIDTH, int(HEIGHT-100)), 5)
  game = Game(world, character, control)

  if nyan:
    character.become_nyan()

  enemies = [Enemy(world, 1.2, -500, "e1.png"),
             Enemy(world, 0, -1300, "e1.png"),
             Enemy(world, 0.0, -1800, "e2.png"),
             Enemy(world, 0.0, -2000, "e2.png"),
             Enemy(world, 0.0, -2200, "e2.png"),
             Enemy(world, 1.2, -2600, "e3.png"),
             Enemy(world, 1.2, -2800, "e3.png"),
             Enemy(world, 1.2, -3000, "e3.png"),
             Enemy(world, 0.0, -4000, "e6.png"),
             Enemy(world, 0.0, -4100, "e6.png"),
             Enemy(world, 0.0, -4200, "e6.png"),
             Enemy(world, 0.0, -4300, "e6.png"),
             Enemy(world, 1.2, -4000, "e5.png"),
             Enemy(world, 1.2, -4100, "e5.png"),
             Enemy(world, 1.2, -4200, "e5.png"),
             Enemy(world, 1.2, -4300, "e5.png"),
             Enemy(world, 0.6, -5000, "e7.png"),
             Enemy(world, 1.2, -5400, "e7.png"),
             Enemy(world, 0.0, -5400, "e7.png"),
            ]

  win = False


  while True:
    time_passed = clock.tick(FPS)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

    pressed = pygame.key.get_pressed()
    if pressed[K_1]:
      break

    surface.fill(BG)
    world.draw_fg(surface)

    pygame.display.update()

  i = 0
  while True:
    time_passed = clock.tick(FPS)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

    character.pos = (character.pos[0] - 2, character.pos[1])

    surface.fill(BG)
    world.draw_fg(surface)
    character.draw(surface)

    pygame.display.update()

    world.tick()
    character.tick()
    i += 1
    if i > 200:
      break







  while True:
    time_passed = clock.tick(FPS)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

    mic.process()

    if mic.loud:
      control.set_up()
    else:
      control.set_down()

    pressed = pygame.key.get_pressed()
    if pressed[K_UP]:
      control.set_up()
    elif pressed[K_DOWN]:
      control.set_down()
    elif pressed[K_2]:
      break

    game.progress()

    surface.fill(BG)
    world.draw_fg(surface)
    character.draw(surface)

    pygame.display.update()

    world.tick()
    character.tick()


  i = 0
  while True:
    time_passed = clock.tick(FPS)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

    mic.process()

    if mic.loud:
      control.set_up()
    else:
      control.set_down()

    pressed = pygame.key.get_pressed()
    if pressed[K_UP]:
      control.set_up()
    elif pressed[K_DOWN]:
      control.set_down()
    elif pressed[K_5]:
      change_to_nyan(world, character)


    game.progress()
    map(lambda a: a.progress(), enemies)

    collisions = False
    for e in enemies:
      if e.check_collision(character):
        collisions = True
        break
    if collisions:
      break

    surface.fill(BG)
    world.draw_fg(surface)
    character.draw(surface)
    for e in enemies:
      e.draw(surface)

    pygame.display.update()

    world.tick()
    character.tick()

    i += 1
    if i > 950:
      win = True
      break

  if win:
    i = 0
    while True:
      time_passed = clock.tick(FPS)

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()

      character.pos = (character.pos[0] - 10, character.pos[1])

      surface.fill(BG)
      world.draw_fg(surface)
      character.draw(surface)

      pygame.display.update()

      world.tick()
      character.tick()
      i += 1
      if i > 100:
        break

  if win:
    message = "Congratulations!"
  else:
    message = "Game Over"

  while True:
    time_passed = clock.tick(FPS)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

    pressed = pygame.key.get_pressed()
    if pressed[K_3]:
      break
    elif pressed[K_4]:
      sys.exit(0)


    surface.fill(BG)
    world.draw_fg(surface)

    font = pygame.font.SysFont("Arial", 64)
    label = font.render(message, 1, BLACK)
    surface.blit(label, (300, 24))


    pygame.display.update()

    world.tick()
