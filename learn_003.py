background_image_filename = 'data/image/bottle.jpeg'

import pygame
from pygame.locals import *
from sys import exit

pygame.init()
screen = pygame.display.set_mode((640, 480), 0, 32)
background = pygame.image.load(background_image_filename).convert()
font = pygame.font.SysFont("arial", 36)

x, y = 0, 0
move_x, move_y = 0, 0

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        if event.type == 771:
            print(event.text)
            # 键盘有按下？
            if event.text == 'a':
                # 按下的是左方向键的话，把x坐标减一
                move_x = -2
            elif event.text == 'd':
                # 右方向键则加一
                move_x = 2
            elif event.text == 'w':
                # 类似了
                move_y = -2
            elif event.text == 's':
                move_y = 2
            #screen.blit(font.render("123", True, (0, 0, 0)), (100, 10))
        elif event.type == KEYUP:
            # 如果用户放开了键盘，图就不要动了
            move_x = 0
            move_y = 0

        # 计算出新的坐标
        x += move_x
        y += move_y

        screen.fill((255, 255, 255))
        screen.blit(background, (x, y))
        # 在新的位置上画图
        pygame.display.update()