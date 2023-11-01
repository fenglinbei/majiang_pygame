import pygame

from typing import List, Tuple

from config import asset_config, render_config
from utils.vector import Vec2d
from utils.constants import PlayerType
from processor.processor import Processor
from Source.Majiang.entity.entities import Table, Card
from logic.elements import Player, LogicCard

class Render:

    def __init__(self, table: Table):
        self.table = table

        self.assets = Processor(
            card_face_image_path=asset_config.CARD_FACE_PATH,
            card_back_image_path=asset_config.CARD_BACK_PATH,
            font_image_path=asset_config.FONT_PATH
            ).get_assets()
        
        self.font_place = (3 * render_config.RADIUS + 9 * self.assets.card_width,
                           4 * render_config.RADIUS + 0.5 * ((6 / 5) * render_config.RADIUS + 3 * self.assets.card_height) - 64)
        self.peng_place = {2: (render_config.SCREEN_WIDTH - 12 - self.assets.card_height, 12),
                           1: (render_config.SCREEN_WIDTH - 12 - self.assets.card_width, render_config.SCREEN_HEIGHT - 12 - self.assets.card_height),
                           3: (12, 12),
                           4: (12, render_config.SCREEN_WIDTH - 12 - self.assets.card_width)}
        self.place = {1: [(3 * render_config.RADIUS - 4 * self.assets.card_width,
                           4 * render_config.RADIUS + 0.5 * ((6 / 5) * render_config.RADIUS - 3 * self.assets.card_height)),
                          (3 * render_config.RADIUS + 7 * self.assets.card_width,
                           (26 / 5) * render_config.RADIUS)],
                      2: [(4 * render_config.RADIUS + 0.5 * ((6 / 5) * render_config.RADIUS - 3 * self.assets.card_height),
                           3 * render_config.RADIUS + 3 * self.assets.card_width),
                          ((26 / 5) * render_config.RADIUS,
                           3 * render_config.RADIUS - 3 * render_config.RADIUS + 5 * self.assets.card_width)],
                      3: [(3 * render_config.RADIUS + 3 * self.assets.card_width,
                           (4 / 5) * render_config.RADIUS + 0.5 * ((6 / 5) * render_config.RADIUS - 3 * self.assets.card_height) + 2 * self.assets.card_height),
                          (3 * render_config.RADIUS - 3 * render_config.RADIUS + 5 * self.assets.card_width,
                           (4 / 5) * render_config.RADIUS - self.assets.card_height)],
                      4: [((4 / 5) * render_config.RADIUS + 0.5 * ((6 / 5) * render_config.RADIUS - 3 * self.assets.card_height) + 2 * self.assets.card_height,
                           3 * render_config.RADIUS - 4 * self.assets.card_width),
                          ((4 / 5) * render_config.RADIUS - self.assets.card_height, 3 * render_config.RADIUS + 7 * self.assets.card_width)]}
        
        self.hands_card_list: List[Card] = []
        self.card_list: List[Card]
        
        self.text = ''

    def load_all_cards(self, all_cards: List[LogicCard]):
        # 加载所有的卡背与卡面
        for logic_card in all_cards:
                
            card = Card(
                face=self.assets.card_faces[logic_card.cls],
                back=self.assets.card_back,
                card_id=logic_card.id)
            
            self.card_list.append(card)
            
            
        #     if player == PlayerType.NAN:
        #         card.face = pygame.transform.rotate(card.face, 90)
        #         card.back = pygame.transform.rotate(card.back, 90)

        #     elif player == PlayerType.BEI:
        #         card.face = pygame.transform.rotate(card.face, 270)
        #         card.back = pygame.transform.rotate(card.back, 90)
                
        #     self.card_list.append(card)

        #     for logic_card in player.puts:
        #         card = Card(
        #             face=self.assets.card_faces[logic_card.cls],
        #             back=self.assets.card_back,
        #             card_id=logic_card.id,
        #             owner=player.player_type)
                

        #         if player == PlayerType.NAN:
        #             card.face = pygame.transform.rotate(card.face, 90)
        #             card.back = pygame.transform.rotate(card.back, 90)

        #         elif player == PlayerType.BEI:
        #             card.face = pygame.transform.rotate(card.face, 270)
        #             card.back = pygame.transform.rotate(card.back, 90)
                    
        #         self.puts_card_list.append(card)

        # return True

    def clean_card(self):
        self.hands_card_list.clear()
        self.puts_card_list.clear()

    def load_card(self, step: int, players: List[Player]):
        self.table.reset_player_card()
        pw, ph = self.assets.card_width + 1, self.assets.card_height + 1
        
        for player in players:

            for index, logic_card in enumerate(player.hands):
                
                card = self.card_list[logic_card.id]
                card.owner = player.player_type
                
                if player.player_type == PlayerType.DONG:
                    card.location = Vec2d(self.place[player.player_type][1][0] - index * pw,
                                          self.place[player.player_type][1][1])
                elif player.player_type == PlayerType.NAN:
                    card.location = Vec2d(self.place[player.player_type][1][0],
                                          self.place[player.player_type][1][1] + index * pw)
                    card.face = pygame.transform.rotate(card.face, 90)
                    card.back = pygame.transform.rotate(card.back, 90)
                elif player.player_type == PlayerType.XI:
                    card.location = Vec2d(self.place[player.player_type][1][0] + index * pw,
                                          self.place[player.player_type][1][1])
                elif player.player_type == PlayerType.BEI:
                    card.location = Vec2d(self.place[player.player_type][1][0],
                                          self.place[player.player_type][1][1] - index * pw)
                    card.face = pygame.transform.rotate(card.face, 270)
                    card.back = pygame.transform.rotate(card.back, 90)
                   
                card.destination = card.location
        
                self.table.add_entity(card)

            for index, logic_card in enumerate(player.puts):
                
                card = self.card_list[logic_card.id]
                card.owner = player.player_type
                
                if player.player_type == PlayerType.DONG:
                    card.location = Vec2d(self.place[player.player_type][0][0] + (index % 8) * pw,
                                          self.place[player.player_type][0][1] + (index // 8) * ph)
                elif player.player_type == PlayerType.NAN:
                    card.location = Vec2d(self.place[player.player_type][0][0] + (index // 8) * ph,
                                          self.place[player.player_type][0][1] - (index % 8) * pw)
                    card.face = pygame.transform.rotate(card.face, 90)
                    card.back = pygame.transform.rotate(card.back, 90)
                elif player.player_type == PlayerType.XI:
                    card.location = Vec2d(self.place[player.player_type][0][0] - (index % 8) * pw,
                                          self.place[player.player_type][0][1] - (index // 8) * ph)
                elif player.player_type == PlayerType.BEI:
                    card.location = Vec2d(self.place[player.player_type][0][0] - (index // 8) * ph,
                                          self.place[player.player_type][0][1] + (index % 8) * pw)
                    card.face = pygame.transform.rotate(card.face, 270)
                    card.back = pygame.transform.rotate(card.back, 90)
                
                card.destination = card.location

                card.can_followed = False
                card.show = True
                
                self.table.add_entity(card)

    def set_font(self, state_list, player):
        state_num = 0
        for state in state_list:
            card = Card(face=self.assets.fonts[state], back=self.assets.fonts[state])
            card.location = Vec2d(self.font_place[0] - (state_num * (self.assets.font_width + 16)), self.font_place[1])
            card.destination = card.location
            card.can_followed = False
            card.owner = player
            card.id = 200 + state_num
            self.table.add_entity(card)
            state_num += 1

    def remove_font(self):
        for state_num in range(200, 204):
            try:
                self.table.remove_entity(state_num)
            except:
                return

    def set_text(self, is_hupai: bool, player: str):
        if is_hupai:
            self.text = 'winner is %d' % player
        else:
            self.text = 'game over'

