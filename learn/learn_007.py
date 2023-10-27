import pygame
from pygame.locals import *
from sys import exit
from random import randint

pygame.init()
screen = pygame.display.set_mode((3440, 1440), HWSURFACE | FULLSCREEN, 32)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

    rand_col = (randint(0, 255), randint(0, 255), randint(0, 255))
    screen.lock()
    for _ in range(10000):
        rand_pos = (randint(0, 3440), randint(0, 1440))
        screen.set_at(rand_pos, rand_col)
    screen.unlock()

    pygame.display.update()