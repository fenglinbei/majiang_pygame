import pygame

from typing import List, Tuple

from config import asset_config, render_config
from utils.vector import Vec2d
from utils.constants import PlayerType
from processor.processor import Processor
from Source.Majiang.entity.entities import Table, Card
from logic.elements import Player, LogicCard

class LocationAndSize:
    
    def __init__(self) -> None:
        
        assets = Processor(
            card_face_image_path=asset_config.CARD_FACE_PATH,
            card_back_image_path=asset_config.CARD_BACK_PATH,
            font_image_path=asset_config.FONT_PATH
            ).get_assets()
        
        self.font_size = assets.font_size
        self.card_size = assets.card_size
        self.card_width = assets.card_width
        self.card_height = assets.card_height
        
        self.font_place = (3 * render_config.RADIUS + 9 * self.card_width,
                           4 * render_config.RADIUS + 0.5 * ((6 / 5) * render_config.RADIUS + 3 * self.card_height) - 64)
        self.peng_place = {2: (render_config.SCREEN_WIDTH - 12 - self.card_height, 12),
                           1: (render_config.SCREEN_WIDTH - 12 - self.card_width, render_config.SCREEN_HEIGHT - 12 - self.card_height),
                           3: (12, 12),
                           4: (12, render_config.SCREEN_WIDTH - 12 - self.card_width)}
        self.place = {1: [(3 * render_config.RADIUS - 4 * self.card_width,
                           4 * render_config.RADIUS + 0.5 * ((6 / 5) * render_config.RADIUS - 3 * self.card_height)),
                          (3 * render_config.RADIUS + 7 * self.card_width,
                           (26 / 5) * render_config.RADIUS)],
                      2: [(4 * render_config.RADIUS + 0.5 * ((6 / 5) * render_config.RADIUS - 3 * self.card_height),
                           3 * render_config.RADIUS + 3 * self.card_width),
                          ((26 / 5) * render_config.RADIUS,
                           3 * render_config.RADIUS - 3 * render_config.RADIUS + 5 * self.card_width)],
                      3: [(3 * render_config.RADIUS + 3 * self.card_width,
                           (4 / 5) * render_config.RADIUS + 0.5 * ((6 / 5) * render_config.RADIUS - 3 * self.card_height) + 2 * self.card_height),
                          (3 * render_config.RADIUS - 3 * render_config.RADIUS + 5 * self.card_width,
                           (4 / 5) * render_config.RADIUS - self.card_height)],
                      4: [((4 / 5) * render_config.RADIUS + 0.5 * ((6 / 5) * render_config.RADIUS - 3 * self.card_height) + 2 * self.card_height,
                           3 * render_config.RADIUS - 4 * self.card_width),
                          ((4 / 5) * render_config.RADIUS - self.card_height, 3 * render_config.RADIUS + 7 * self.card_width)]}

LOCATION_AND_SIZE = LocationAndSize()

class Render:

    def __init__(self, table: Table):
        self.table = table
        self.screen = pygame.display.set_mode((render_config.SCREEN_WIDTH, render_config.SCREEN_HEIGHT), 0, 32)
        self.font = pygame.font.SysFont("arial", render_config.FONT_SIZE)
        
        self.clock = pygame.time.Clock()
    
    
    def render(self):
        self.table.process(self.clock.tick(60))
        self.screen.blit(self.table.back_ground, (0, 0))
        
        for entity in self.table.entities.values():
            if entity.render:
                if entity.id < 200:
                    self.screen.blit(entity.back, entity.location) if entity.show else self.screen.blit(entity.back, entity.location)
                
        font_text_1 = self.font.render(self.table.text, True, (0, 0, 0))
        # font_text_2 = self.font.render(self.table.text_2, True, (0, 0, 0))
        # self.screen.blit(font_text_1, (render_config.SCREEN_WIDTH / 2 - 100, render_config.SCREEN_HEIGHT / 2 - 24))
        # self.screen.blit(font_text_2, (render_config.SCREEN_WIDTH / 2 - 100, render_config.SCREEN_HEIGHT / 2 + 10))
        

