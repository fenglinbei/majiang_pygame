import sys
sys.path.append(".")

import copy
import pygame

from pygame import Surface
from typing import Dict, List, Optional, Tuple

from config import render_config
from utils.vector import Vec2d
from utils.constants import PlayerType, Color
from logic.elements import LogicCard


class Entity:
    def __init__(self) -> None:
        self.id: int = 0
        self.location = Vec2d(0, 0)
        self.destination = Vec2d(0, 0)
        self.speed: int = 0
    
    def render(self):
        pass


class Card(Entity):

    def __init__(
        self, 
        face: Surface, 
        back: Surface, 
        logic_card: LogicCard,
        show: bool = False,
        followed: bool = True,
        owner: PlayerType = PlayerType.EMPTY
        ):
        super().__init__()

        self.face = face
        self.back = back
        self.size = [face.get_width(), face.get_height()]
        self.owner = owner # 手牌拥有者
        self.speed = render_config.CARD_MOVEMENT_SPEED
        self.show = show # 是否展示手牌
        self.can_followed = followed # 是否跟随鼠标
        self.init_location = self.location
        
        self.id = logic_card.id
        self.cls = logic_card.cls
        self.type = logic_card.type
        self.num = logic_card.num

    def render(self, surface: Surface):
        surface.blit(self.back, self.location) if self.show else surface.blit(self.back, self.location)

    def process(self, time_passed_seconds: float):
        if self.speed > 0. and self.location != self.destination:
            vec_to_destination = self.destination - self.location
            distance_to_destination = vec_to_destination.get_length()
            heading = vec_to_destination.normalized()
            travel_distance = min(distance_to_destination, time_passed_seconds * self.speed)
            self.location += travel_distance * heading


class Font(Entity):
    def __init__(self, asset: Surface) -> None:
        self.asset = asset
        
    def render(self, surface: Surface):
        surface.blit(self.asset, self.location)


class Table(Entity):
    def __init__(self):
        self.back_ground = pygame.surface.Surface((render_config.SCREEN_WIDTH, render_config.SCREEN_HEIGHT)).convert()
        self.back_ground.fill(Color.WHITE)

        pygame.draw.circle(self.back_ground, Color.PALE_GREEN, render_config.CENTER_POS, render_config.RADIUS)
        self.entities: Dict[int, Card] = {}

    def add_entity(self, entity: Entity):
        self.entities[entity.id] = entity

    def remove_entity(self, entity_id: int):
        del self.entities[entity_id]

    def clear_entity(self):
        self.entities = {}

    def reset_player_card(self):
        new_entities = copy.copy(self.entities)
        for entity in self.entities.values():
            if entity.player != PlayerType.EMPTY:
                del new_entities[entity.id]
        self.entities = new_entities

    def pos_in_entity(self, pos: Tuple[int, int], player: PlayerType):
        for entity in self.entities.values():
            if entity.owner == player and \
                0 <= (pos[0] - entity.location[0]) <= entity.size[0] and \
                0 <= (pos[1] - entity.location[1]) <= entity.size[1]:
                return entity.id
        return None

    def __getitem__(self, entity_id: int):
        return self.entities[entity_id]
    
    def follow_mouse(self, pos: Tuple[int, int], last_id: int, player: PlayerType):
        entity_id = self.pos_in_entity(pos, player)
        
        if last_id > 0:
            card = self[last_id]
            if card.can_followed:
                card.location = Vec2d(pos[0] - card.size[0] / 2, pos[1] - card.size[1] / 2)
                card.destination = card.location
                return last_id
            
        elif entity_id > 0:
            card = self[entity_id]
            if card.can_followed:
                card.location = Vec2d(pos[0] - card.size[0] / 2, pos[1] - card.size[1] / 2)
                card.destination = card.location
                return entity_id
        return entity_id

    def process(self, time_passed_ms: float):
        time_passed_seconds = time_passed_ms / 1000.0
        entities = copy.copy(self.entities)
        for entity in entities.values():
            entity.process(time_passed_seconds)

    def render(self, surface: Surface, show_player_list: Optional[List[PlayerType]] = []):
        surface.blit(self.back_ground, (0, 0))
        for entity in self.entities.values():
            if entity.owner in show_player_list:
                entity.show = True
                entity.render(surface)


