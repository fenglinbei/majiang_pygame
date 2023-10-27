background_image_filename = 'data/image/backgroung.jpg'
sprite_image_filename = 'data/image/bottle.jpeg'

import pygame
from pygame.locals import *
from sys import exit
from random import *
import math

pygame.init()
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
w, h, wid = 3440, 1440, 5

screen = pygame.display.set_mode((w, h), HWSURFACE | FULLSCREEN, 32)

background = pygame.image.load(background_image_filename).convert()
sprite = pygame.image.load(sprite_image_filename)

# Clock对象
clock = pygame.time.Clock()

theta = randint(0, 360)
r = 200
rc = (randint(0, 255), randint(0, 255), randint(0, 255))
x = r
y = r

# 速度（像素/秒）
speed = 1000.

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        elif event.type == KEYDOWN:
            exit()
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                theta = randint(0, 360)
            elif event.button == 3:
                rc = (randint(0, 255), randint(0, 255), randint(0, 255))
        elif event.type == MOUSEWHEEL:
            if event.y > 0:
                speed += 50
            else:
                speed -= 50
                if speed < 0:
                    speed = 0

    screen.fill((0, 0, 0))
    pygame.draw.circle(screen, rc, (x, y), r, width=wid)

    time_passed = clock.tick()
    time_passed_seconds = time_passed / 1000.0

    distance_moved = time_passed_seconds * speed
    x_move = distance_moved * math.sin(theta / 57.3)
    y_move = distance_moved * math.cos(theta / 57.3)

    x += x_move
    y -= y_move

    if x > w - 4*r - 80:
        x = w - 4*r - 80
        theta = 360 - theta
        rc = (randint(0, 255), randint(0, 255), randint(0, 255))
    elif x < r:
        x = r
        theta = 360 - theta
        rc = (randint(0, 255), randint(0, 255), randint(0, 255))

    if y > h - 2*r - 80:
        y = h - 2*r - 80
        if theta < 180:
            theta = 180 - theta
        else:
            theta = 540 - theta
        rc = (randint(0, 255), randint(0, 255), randint(0, 255))
    elif y < r:
        y = r
        if theta < 180:
            theta = 180 - theta
        else:
            theta = 540 - theta
        rc = (randint(0, 255), randint(0, 255), randint(0, 255))

    pygame.display.flip()
