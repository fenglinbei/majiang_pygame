#!/usr/bin/env python
import pygame
from pygame.locals import *
from sys import exit

pygame.init()

screen = pygame.display.set_mode((3440, 1440), FULLSCREEN, 32)


def create_scales(height):
    red_scale_surface = pygame.surface.Surface((3440, height))
    green_scale_surface = pygame.surface.Surface((3440, height))
    blue_scale_surface = pygame.surface.Surface((3440, height))
    for x in range(3440):
        c = int((x / 3440) * 255.)
        red = (c, 0, 0)
        green = (0, c, 0)
        blue = (0, 0, c)
        line_rect = Rect(x, 0, 1, height)
        pygame.draw.rect(red_scale_surface, red, line_rect)
        pygame.draw.rect(green_scale_surface, green, line_rect)
        pygame.draw.rect(blue_scale_surface, blue, line_rect)
    return red_scale_surface, green_scale_surface, blue_scale_surface


red_scale, green_scale, blue_scale = create_scales(100)

color = [127, 127, 127]

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

    screen.fill((0, 0, 0))

    screen.blit(red_scale, (0, 0))
    screen.blit(green_scale, (0, 100))
    screen.blit(blue_scale, (0, 200))

    x, y = pygame.mouse.get_pos()

    if pygame.mouse.get_pressed()[0]:
        for component in range(3):
            if component * 100 < y < (component + 1) * 100:
                color[component] = int((x / 3440) * 255.)
        pygame.display.set_caption("PyGame Color Test - " + str(tuple(color)))

    for component in range(3):
        pos = (int((color[component] / 255.) * 3440), component * 100 + 50)
        pygame.draw.circle(screen, (255, 255, 255), pos, 25)

    pygame.draw.rect(screen, tuple(color), (0, 300, 3440, 1440))

    pygame.display.update()