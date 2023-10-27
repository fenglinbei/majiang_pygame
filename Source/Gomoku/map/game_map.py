import pygame

from typing import Tuple, List
from pygame import Surface

from config import config
from utils.constants import Player, Color

from utils.utils import reverse_player

MAP_POINT_POS = [(3, 3), (11, 3), (3, 11), (11, 11), (7, 7)]
player_color = {
                Player.BLACK: Color.PLAYER_BLACK,
                Player.WHITE: Color.PLAYER_WHITE
            }

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = [[0 for x in range(self.width)] for y in range(self.height)]
        self.steps = []

    def reset(self):
        for y in range(self.height):
            for x in range(self.width):
                self.map[y][x] = 0
        self.steps = []

    @staticmethod
    def getMapUnitRect(x: int, y: int) -> Tuple[int]:
        map_x = x * config.REC_SIZE
        map_y = y * config.REC_SIZE

        return (map_x, map_y, config.REC_SIZE, config.REC_SIZE)

    @staticmethod
    def MapPosToIndex(map_x: int, map_y: int) -> Tuple[int]:
        x = map_x // config.REC_SIZE
        y = map_y // config.REC_SIZE
        return (x, y)
    
    @staticmethod
    def isInMap(map_x: int, map_y: int) -> bool:
        if (map_x <= 0 or map_x >= config.MAP_WIDTH or
                map_y <= 0 or map_y >= config.MAP_HEIGHT):
            return False
        return True

    def isEmpty(self, x: int, y: int) -> bool:
        return self.map[y][x] == 0

    def click(self, x: int, y: int, player: Player):
        self.map[y][x] = player.value
        self.steps.append((x, y))

    def drawChess(self, screen: Surface):

        font = pygame.font.SysFont(None, config.REC_SIZE * 2 // 3)

        for i in range(len(self.steps)):
            x, y = self.steps[i]
            map_x, map_y, width, height = self.getMapUnitRect(x, y)
            pos, radius = (map_x + width // 2, map_y + height // 2), config.CHESS_RADIUS
            player = self.map[y][x]

            pygame.draw.circle(screen, player_color[player], pos, radius)

            msg_image = font.render(str(i), True, player_color[reverse_player(player)], player_color[player])
            msg_image_rect = msg_image.get_rect()
            msg_image_rect.center = pos
            screen.blit(msg_image, msg_image_rect)

        if len(self.steps) > 0:
            last_pos = self.steps[-1]
            map_x, map_y, width, height = self.getMapUnitRect(last_pos[0], last_pos[1])
            purple_color = (255, 0, 255)
            point_list = [(map_x, map_y), (map_x + width, map_y),
                          (map_x + width, map_y + height), (map_x, map_y + height)]
            pygame.draw.lines(screen, purple_color, True, point_list, 1)

    def drawBackground(self, screen: Surface):
        
        # 画横线
        for y in range(self.height):
            # draw a horizontal line
            start_pos, end_pos = (config.REC_SIZE // 2, config.REC_SIZE // 2 + config.REC_SIZE * y), (
                config.MAP_WIDTH - config.REC_SIZE // 2, config.REC_SIZE // 2 + config.REC_SIZE * y)

            if y == (self.height) // 2:
                width = 2
            else:
                width = 1
            pygame.draw.line(screen, Color.BLACK, start_pos, end_pos, width)

        # 画竖线
        for x in range(self.width):
            # draw a horizontal line
            start_pos, end_pos = (config.REC_SIZE // 2 + config.REC_SIZE * x, config.REC_SIZE // 2), (
                config.REC_SIZE // 2 + config.REC_SIZE * x, config.MAP_HEIGHT - config.REC_SIZE // 2)
            if x == (self.width) // 2:
                width = 2
            else:
                width = 1
            pygame.draw.line(screen, Color.BLACK, start_pos, end_pos, width)

        # 画棋盘上的点
        for (x, y) in MAP_POINT_POS:
            pygame.draw.rect(
                screen,
                Color.BLACK,
                (
                    x * config.REC_SIZE + config.REC_SIZE // 2 - config.MAP_POINT_SIZE // 2,
                    y * config.REC_SIZE + config.REC_SIZE // 2 - config.MAP_POINT_SIZE // 2,
                    config.MAP_POINT_SIZE,
                    config.MAP_POINT_SIZE
                    )
                )
