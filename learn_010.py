import pygame
from pygame.locals import *
from sys import exit
from Vector import Vec2d
from random import *

pygame.init()

screen = pygame.display.set_mode((640, 480), 0, 32)

clock = pygame.time.Clock()

position = Vec2d(100.0, 100.0)
heading = Vec2d(0, 0)
r = 100
wid = 5
rc = (randint(0, 255), randint(0, 255), randint(0, 255))


def from_points(p1, p2):
    return Vec2d(p2[0] - p1[0], p2[1] - p1[1])


while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

    time_passed = clock.tick()
    time_passed_seconds = time_passed / 1000.0

    screen.fill((0, 0, 0))
    pygame.draw.circle(screen, rc, position, r, width=wid)

    # 参数前面加*意味着把列表或元组展开
    destination = Vec2d(*pygame.mouse.get_pos()) - Vec2d(2 * r, 2 * r) / 2
    # 计算鱼儿当前位置到鼠标位置的向量
    vector_to_mouse = from_points(position, destination)
    # 向量规格化
    vector_to_mouse.normalized()

    # 这个heading可以看做是鱼的速度，但是由于这样的运算，鱼的速度就不断改变了
    # 在没有到达鼠标时，加速运动，超过以后则减速。因而鱼会在鼠标附近晃动。
    heading = heading + (vector_to_mouse * 0.001)

    position += heading * time_passed_seconds
    pygame.display.update()
