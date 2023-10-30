background_image_filename = 'data/image/backgroung.jpg'
sprite_image_filename = 'data/image/bottle.jpeg'

import pygame
from pygame.locals import *
from sys import exit
from Source.Majiang.Vector import Vec2d
from math import *

pygame.init()
screen = pygame.display.set_mode((640, 480), 0, 32)

background = pygame.image.load(background_image_filename).convert()
sprite = pygame.image.load(sprite_image_filename).convert_alpha()

clock = pygame.time.Clock()

# 让pygame完全控制鼠标
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

sprite_pos = Vec2d(200, 150)
sprite_speed = 300.
sprite_rotation = 0.
sprite_rotation_speed = 360.

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        # 按Esc则退出游戏
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                exit()

    pressed_keys = pygame.key.get_pressed()
    # 这里获取鼠标的按键情况
    pressed_mouse = pygame.mouse.get_pressed()

    rotation_direction = 0.
    movement_direction = 0.

    # 通过移动偏移量计算转动
    rotation_direction = pygame.mouse.get_rel()[0] / 5.0
    print(rotation_direction)

    if pressed_keys[K_LEFT]:
        rotation_direction = +1.
    if pressed_keys[K_RIGHT]:
        rotation_direction = -1.
    # 多了一个鼠标左键按下的判断
    if pressed_keys[K_UP] or pressed_mouse[0]:
        movement_direction = +1.
    # 多了一个鼠标右键按下的判断
    if pressed_keys[K_DOWN] or pressed_mouse[2]:
        movement_direction = -1.

    screen.blit(background, (0, 0))

    rotated_sprite = pygame.transform.rotate(sprite, sprite_rotation)
    w, h = rotated_sprite.get_size()
    sprite_draw_pos = Vec2d(sprite_pos.x - w / 2, sprite_pos.y - h / 2)
    screen.blit(rotated_sprite, sprite_draw_pos)

    time_passed = clock.tick()
    time_passed_seconds = time_passed / 1000.0

    sprite_rotation += rotation_direction * sprite_rotation_speed * time_passed_seconds

    heading_x = sin(sprite_rotation * pi / 180.)
    heading_y = cos(sprite_rotation * pi / 180.)
    heading = Vec2d(heading_x, heading_y)
    heading *= movement_direction

    sprite_pos += heading * sprite_speed * time_passed_seconds

    pygame.display.update()