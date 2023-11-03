import sys
sys.path.append(".")

import copy
import pygame

from pygame import Surface
from typing import Dict, List, Optional, Tuple

from config import render_config, asset_config, base_config
from utils.vector import Vec2d
from utils.constants import PlayerType, Color
from logic.elements import LogicCard
from processor.processor import Processor
from render.render import LOCATION_AND_SIZE
from logic.player import Player


class Entity:
    def __init__(self) -> None:
        self.id: int = 0
        self.location = Vec2d(0, 0)
        self.destination = Vec2d(0, 0)
        self.speed: int = 0
        self.render = False
    

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
        self.render = False
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
        self.assets = Processor(
            card_face_image_path=asset_config.CARD_FACE_PATH,
            card_back_image_path=asset_config.CARD_BACK_PATH,
            font_image_path=asset_config.FONT_PATH
            ).get_assets()
        
        self.back_ground = pygame.surface.Surface((render_config.SCREEN_WIDTH, render_config.SCREEN_HEIGHT)).convert()
        self.back_ground.fill(Color.WHITE)

        pygame.draw.circle(self.back_ground, Color.PALE_GREEN, render_config.CENTER_POS, render_config.RADIUS)
        self.entities: Dict[int, Card] = {}
        self.text = ""
        
        self.show_players = [base_config.INIT_PLAYER]
        
        self.pw, self.ph = self.assets.card_width + 1, self.assets.card_height + 1

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
        return -1

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
    
    def set_text(self, is_win: bool, player: str):
        if is_win:
            self.text = 'winner is %d' % player
        else:
            self.text = 'game over'
    
    def set_font(self, state_list: List[str]):
        state_num = 0
        for state in state_list:
            font = Font(asset=self.assets.fonts[state])
            font.location = Vec2d(LOCATION_AND_SIZE.font_place[0] - (state_num * (self.assets.font_width + 16)), LOCATION_AND_SIZE.font_place[1])
            font.destination = font.location
            font.id = 200 + state_num
            self.add_entity(font)
            state_num += 1

    def remove_font(self):
        for state_num in range(200, 204):
            try:
                self.remove_entity(state_num)
            except:
                return
            
    def load_cards(self, all_cards: List[LogicCard]):
        # 加载所有的卡背与卡面
        for logic_card in all_cards:
                
            card = Card(
                face=self.assets.card_faces[logic_card.cls],
                back=self.assets.card_back,
                card_id=logic_card.id)
            
            self.entities[logic_card.id] = card
    
    def update_cards(self, players: List[Player]):
        for player in players:
            
            if player.brain.active_state.name in ["putting", "drawing", "peng", "gang"]:
                
                for index, logic_card in enumerate(player.hands):
                    card = self.entities[logic_card.id]
                    
                    if player.player_type == PlayerType.DONG:
                        card.location = Vec2d(
                            LOCATION_AND_SIZE[player.player_type][1][0] - index * self.pw,
                            LOCATION_AND_SIZE[player.player_type][1][1]
                            )
                    
                    elif player.player_type == PlayerType.NAN:
                        card.location = Vec2d(
                            LOCATION_AND_SIZE[player.player_type][1][0],
                            LOCATION_AND_SIZE[player.player_type][1][1] + index * self.pw
                            )
                        card.face = pygame.transform.rotate(card.face, 90)
                        card.back = pygame.transform.rotate(card.back, 90)
                    elif player.player_type == PlayerType.XI:
                        card.location = Vec2d(
                            LOCATION_AND_SIZE[player.player_type][1][0] + index * self.pw,
                            LOCATION_AND_SIZE[player.player_type][1][1])

                    elif player.player_type == PlayerType.BEI:
                        card.location = Vec2d(
                            LOCATION_AND_SIZE[player.player_type][1][0],
                            LOCATION_AND_SIZE[player.player_type][1][1] - index * self.pw)
                        card.face = pygame.transform.rotate(card.face, 270)
                        card.back = pygame.transform.rotate(card.back, 90)
                    
            if player.brain.active_state.name == "putting":
                
                for logic_card in player.puts:
                    card = self.entities[logic_card.id]
                    
                    if player.player_type == PlayerType.DONG:
                        card.location = Vec2d(LOCATION_AND_SIZE[player.player_type][0][0] + (index % 8) * self.pw,
                                            LOCATION_AND_SIZE[player.player_type][0][1] + (index // 8) * self.ph)
                    elif player.player_type == PlayerType.NAN:
                        card.location = Vec2d(LOCATION_AND_SIZE[player.player_type][0][0] + (index // 8) * self.ph,
                                            LOCATION_AND_SIZE[player.player_type][0][1] - (index % 8) * self.pw)
                        card.face = pygame.transform.rotate(card.face, 90)
                        card.back = pygame.transform.rotate(card.back, 90)
                    elif player.player_type == PlayerType.XI:
                        card.location = Vec2d(LOCATION_AND_SIZE[player.player_type][0][0] - (index % 8) * self.pw,
                                            LOCATION_AND_SIZE[player.player_type][0][1] - (index // 8) * self.ph)
                    elif player.player_type == PlayerType.BEI:
                        card.location = Vec2d(LOCATION_AND_SIZE[player.player_type][0][0] - (index // 8) * self.ph,
                                            LOCATION_AND_SIZE[player.player_type][0][1] + (index % 8) * self.pw)
                        card.face = pygame.transform.rotate(card.face, 270)
                        card.back = pygame.transform.rotate(card.back, 90)
                        
                card.destination = card.location
                card.can_followed = False
                card.show = True
    
    def clean_card(self):
        for card in self.entities.values():
            card.render = False
                        

    def process(self, time_passed_ms: float):
        time_passed_seconds = time_passed_ms / 1000.0
        entities = copy.copy(self.entities)
        for entity in entities.values():
            entity.process(time_passed_seconds)


