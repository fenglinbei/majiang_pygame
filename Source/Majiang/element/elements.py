import copy
import pygame

from pygame import Surface
from typing import Dict, List, Optional

from config import config
from utils.vector import Vec2d
from utils.constants import PlayerType, Color


class Entity:
    def __init__(self) -> None:
        self.id: int = 0
        self.cls: int = 0
        self.location = Vec2d(0, 0)
        self.destination = Vec2d(0, 0)
        self.speed: int = 0


class Card(Entity):

    def __init__(self, face: Surface, back: Surface):
        super().__init__()

        self.face = face
        self.back = back
        self.size = [face.get_width(), face.get_height()]
        self.player = PlayerType.EMPTY # 手牌拥有者
        self.speed = config.CARD_MOVEMENT_SPEED
        self.show = False # 是否展示手牌
        self.can_followed = True # 是否跟随鼠标
        self.init_location = self.location

    def render(self, surface: Surface):
        surface.blit(self.back, self.location) if self.show else surface.blit(self.back, self.location)

    def process(self, time_passed_seconds: float):
        if self.speed > 0. and self.location != self.destination:
            vec_to_destination = self.destination - self.location
            distance_to_destination = vec_to_destination.get_length()
            heading = vec_to_destination.normalized()
            travel_distance = min(distance_to_destination, time_passed_seconds * self.speed)
            self.location += travel_distance * heading


class Table:
    def __init__(self):
        self.back_ground = pygame.surface.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT)).convert()
        self.back_ground.fill(Color.WHITE)

        pygame.draw.circle(self.back_ground, Color.PALE_GREEN, config.CENTER_POS, config.RADIUS)
        self.entities: Dict[int, Card] = {}

    def add_entity(self, entity: Card):
        self.entities[entity.id] = entity

    def remove_entity(self, entity_id: int):
        del self.entities[entity_id]

    def reset_entity(self):
        self.entities = {}

    def reset_player_card(self):
        new_entities = copy.copy(self.entities)
        for entity in self.entities.values():
            if entity.player != PlayerType.EMPTY:
                del new_entities[entity.id]
        self.entities = new_entities

    def pos_in_card(self, pos: Vec2d, player: PlayerType):
        entities = copy.copy(self.entities)
        for entity in entities.values():
            location = entity.location
            size = entity.size
            if 0 <= (pos[0] - location[0]) <= size[0] and \
                    0 <= (pos[1] - location[1]) <= size[1] and entity.player == player:
                return entity.id
        return -1

    def get(self, entity_id: int):
        return self.entities[entity_id]

    def process(self, time_passed_ms: float):
        time_passed_seconds = time_passed_ms / 1000.0
        entities = copy.copy(self.entities)
        for entity in entities.values():
            entity.process(time_passed_seconds)

    def render(self, surface: Surface, show_player_list: Optional[List[PlayerType]] = []):
        surface.blit(self.back_ground, (0, 0))
        for entity in self.entities.values():
            if entity.player in show_player_list:
                entity.show = True
                entity.render(surface)


