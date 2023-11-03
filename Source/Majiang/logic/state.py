import copy
import pygame

from typing import Dict, List

from utils.vector import Vec2d
from logic.referee import Referee
from game_state import GameState
from config import render_config
from utils.constants import PlayerType
from logic.elements import Cards
from render.render import LOCATION_AND_SIZE
        

class State(object):
    def __init__(self, name: str):
        self.name: str = name

    def do_actions(self):
        pass

    def check_conditions(self):
        pass

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass


class StateMachine(object):
    def __init__(self):
        self.states: Dict[str, State] = {}
        self.active_state: State = None

    def add_state(self, state: State):
        self.states[state.name] = state

    def think(self, game_state):
        if self.active_state is None:
            return
        self.active_state.do_actions(game_state)
        
        new_state_name = self.active_state.check_conditions(game_state)
        if new_state_name is not None:
            self.set_state(new_state_name)

    def set_state(self, new_state_name: str):
        if self.active_state is not None:
            self.active_state.exit_actions()
        self.active_state = self.states[new_state_name]
        self.active_state.entry_actions()


class PutCard(State):
    """打出一张牌"""
    def __init__(self, player: PlayerType):
        State.__init__(self, 'putting')
        self.player = player
        self.card_is_choice = False
        self.card_is_arrived = False
        self.choice_entity_id = 0
        self.card = None

    def do_actions(self, state: GameState):
        if self.player.use_ai:
            if not self.card_is_choice:
                self.last_put_card_id = self.player.AI.put_card()[0]
                self.card_is_choice = True
                self.card = self.player.manager.table.get(self.last_put_card_id)
                self.card.destination = Vec2d(*render_config.CENTER_POS)
                self.card.show_flag = True
                
            if self.card.location != Vec2d(*render_config.CENTER_POS):
                self.card_is_arrived = False
            else:
                self.player.manager.move_card_to_table(self.last_put_card_id)
                self.card_is_choice = False
                self.card_is_arrived = True
        else:
            mouse_point = pygame.mouse.get_pos()
            pressed_mouse = pygame.mouse.get_pressed()
            
            # 如果鼠标按下，则获取按下位置的entity_id
            if pressed_mouse[0]:
                self.choice_entity_id = state.table.follow_mouse(mouse_point, self.last_put_card_id, self.player)
            else:
                if self.choice_entity_id > 0 and \
                   (render_config.CENTER_POS[0] - render_config.RADIUS < mouse_point[0] < render_config.CENTER_POS[0] + render_config.RADIUS) and \
                   (render_config.CENTER_POS[1] - render_config.RADIUS < mouse_point[1] < render_config.CENTER_POS[1] + render_config.RADIUS):
                
                    self.card_is_arrived = True
                    # self.player.put_card(self.choice_entity_id)
                    return
                self.choice_entity_id = 0
            self.card_is_arrived = False

    def check_conditions(self, **args):
        if self.card_is_arrived:
            return 'waiting'
        else:
            return None

    def exit_actions(self, state: GameState):
        if self.card_is_arrived:
            state.last_player = self.player
            interrupt_states = state.check_interrupt(self.choice_entity_id, self.player.player_type)
            if not interrupt_states:
                state.players[self.player].put_card(self.choice_entity_id)

        self.choice_entity_id = -1
        self.card_is_arrived = False
        self.card_is_choice = False


class DrawCard(State):
    """摸牌"""
    def __init__(self, player: PlayerType):
        State.__init__(self, 'drawing')
        self.player = player
        self.draw_card = None

    def do_actions(self, state: GameState):
        self.draw_card = state.cards.draw_one()
        

    def check_conditions(self, state: GameState):
        states = state.check_interrupt(self.draw_card.id, self.player, is_drawing=True)
        
        if states:
            return 'choosing' 
        else:
            return 'putting'

    def exit_actions(self, state: GameState):
        state.players[self.player].draw_card(self.draw_card)


class PengCard(State):
    def __init__(self, player: PlayerType):
        """已经选择碰牌后进行的操作"""
        State.__init__(self, 'peng')
        self.player = player

    def do_actions(self, state: GameState):
        player = state.players[self.player]
        peng_card = state.interrupt_card
        peng_cards = Cards([peng_card])

        all_duizi = Referee.get_all_kezi(player.hands, k_count=2)
        for duizi in all_duizi:
            if peng_card.cls == duizi[0].cls:
                peng_cards += duizi
                break
            
        player.peng_card(peng_cards)
        
        card_num = 0
        gang_num = len(player.gangs)
        peng_num = len(player.pengs)
        
        move_dis = (gang_num + peng_num - 1) * (16 + 3 * LOCATION_AND_SIZE.card_width)
        
        if move_dis < 0:
            move_dis = 0
            
        for logic_card in peng_cards:

            location = LOCATION_AND_SIZE.peng_place[self.player]
            card = state.table[logic_card.id]
            if self.player == PlayerType.DONG or self.player == PlayerType.XI:
                if card.owner != self.player:
                    if card.owner == PlayerType.NAN:
                        card.face = pygame.transform.rotate(card.face, 270)
                    elif card.owner == PlayerType.BEI:
                        card.face = pygame.transform.rotate(card.face, 90)
                        
                    card.owner = self.player
                    card.size = [LOCATION_AND_SIZE.card_width, LOCATION_AND_SIZE.card_height]

                card.destination = Vec2d(location[0] - (card.size[0] + 1) * card_num - move_dis, location[1])
                card.show = True
                card.speed = 1000
                
            elif self.player == PlayerType.NAN:
                if card.owner != self.player:
                    if card.owner == PlayerType.DONG or card.owner == PlayerType.XI:
                        # card.face = pygame.transform.rotate(card.image, 270)
                        # card.image = pygame.transform.rotate(card.image, 180)
                        card.face = pygame.transform.rotate(card.face, 90)
                    else:
                        card.face = pygame.transform.rotate(card.face, 180)
                        
                    card.owner = self.player
                    card.size = [LOCATION_AND_SIZE.card_width, LOCATION_AND_SIZE.card_height]

                card.destination = Vec2d(location[0], location[1] + (card.size[1] + 1) * card_num + move_dis)
                card.show = True
                card.speed = 1000
                
            else:
                if card.owner != self.player:
                    if card.owner == PlayerType.DONG or card.owner == PlayerType.XI:
                        card.face = pygame.transform.rotate(card.face, -90)
                    else:
                        card.face = pygame.transform.rotate(card.face, 180)
                    card.owner = self.player
                    card.size = [LOCATION_AND_SIZE.card_width, LOCATION_AND_SIZE.card_height]

                card.destination = Vec2d(location[0], location[1] - (card.size[1] + 1) * card_num - move_dis)
                card.show = True
                card.speed = 1000
                
            card_num += 1

    def check_conditions(self, **args):
        return 'putting'

    def exit_actions(self, state: GameState):
        state.next_player()
        state.interrupt_player = PlayerType.EMPTY
        state.interrupt_states.clear()


class GangCard(State):

    def __init__(self, player: PlayerType):
        State.__init__(self, 'gang')
        self.player = player

    def do_actions(self, state: GameState):
        player = state.players[self.player]
        gang_card = state.interrupt_card
        gang_cards = Cards([gang_card])
        all_kezi = Referee.get_all_kezi(player.hands) + player.pengs
        
        for kezi in all_kezi:
            if gang_card.cls == kezi[0].cls:
                gang_cards += kezi
        
        player.gang_card(gang_cards)
        
        card_num = 0
        gang_num = len(player.gangs)
        peng_num = len(player.pengs)
        move_dis = (gang_num + peng_num - 1) * (16 + 3 * LOCATION_AND_SIZE.card_width)
        peng_cards_location = None
        
        for peng_cards in player.pengs:
            if state.interrupt_card.cls == peng_cards[0].cls:
                peng_cards_location = state.table[peng_cards[1].id].location
                
        if move_dis < 0:
            move_dis = 0
            
        for logic_card in gang_cards:
            card = state.table[logic_card.id]
            location = LOCATION_AND_SIZE.peng_place[self.player]
            if self.player == PlayerType.DONG or self.player == PlayerType.XI:
                if card.owner != self.player:
                    if card.owner == PlayerType.NAN:
                        card.face = pygame.transform.rotate(card.face, 270)
                    elif card.owner == PlayerType.BEI:
                        card.face = pygame.transform.rotate(card.face, 90)
                        
                    card.owner = self.player
                    card.size = [LOCATION_AND_SIZE.card_width, LOCATION_AND_SIZE.card_height]

                if card_num == 3:
                    card.destination = Vec2d(location[0] - (card.size[0] + 1) * (card_num - 2) - move_dis,
                                             location[1] - 6) if not peng_cards_location else \
                                       Vec2d(peng_cards_location[0],
                                             peng_cards_location[1] - 6)
                    card.show = True
                    card.speed = 1000
                    return

                card.destination = Vec2d(location[0] - (card.size[0] + 1) * card_num - move_dis, location[1])
                card.show = True
                card.speed = 1000
                
            elif self.player == PlayerType.NAN:
                if card.owner != self.player:
                    if card.owner == PlayerType.DONG or card.owner == PlayerType.XI:
                        # card.face = pygame.transform.rotate(card.image, 270)
                        # card.image = pygame.transform.rotate(card.image, 180)
                        card.face = pygame.transform.rotate(card.face, 90)
                    else:
                        card.face = pygame.transform.rotate(card.face, 180)
                        
                    card.owner = self.player
                    card.size = [LOCATION_AND_SIZE.card_width, LOCATION_AND_SIZE.card_height]

                if card_num == 3:
                    card.destination = Vec2d(location[0] - 6,
                                             location[1] + (card.size[1] + 1) * (card_num - 2) + move_dis) if not peng_cards_location else \
                                       Vec2d(peng_cards_location[0] - 6,
                                             peng_cards_location[1])
                    card.show = True
                    card.speed = 1000
                    return

                card.destination = Vec2d(location[0], location[1] + (card.size[1] + 1) * card_num + move_dis)
                card.show = True
                card.speed = 1000
            else:
                if card.owner != self.player:
                    if card.owner == PlayerType.DONG or card.owner == PlayerType.XI:
                        card.face = pygame.transform.rotate(card.face, -90)
                    else:
                        card.face = pygame.transform.rotate(card.face, 180)
                    card.owner = self.player
                    card.size = [LOCATION_AND_SIZE.card_width, LOCATION_AND_SIZE.card_height]

                if card_num == 3:
                    card.destination = Vec2d(location[0] + 6,
                                             location[1] - (card.size[1] + 1) * (card_num - 2) - move_dis) if not peng_cards_location else \
                                       Vec2d(peng_cards_location[0] + 6,
                                             peng_cards_location[1])
                    card.show = True
                    card.speed = 1000
                    return

                card.destination = Vec2d(location[0], location[1] - (card.size[1] + 1) * card_num - move_dis)
                card.show= True
                card.speed = 1000
            card_num += 1

    def check_conditions(self, **args):
        return 'drawing'

    def exit_actions(self, state: GameState):
        state.next_player()
        state.interrupt_player = PlayerType.EMPTY
        state.interrupt_states.clear()


class Hu(State):
    def __init__(self, player: PlayerType):
        State.__init__(self, 'hu')
        self.player = player

    def entry_actions(self, state: GameState):
        state.table.set_text(True, self.player)
        for player in state.players:
            player.brain.set_state('end')
        state.winner = self.player


class End(State):
    def __init__(self, player: PlayerType):
        State.__init__(self, 'end')
        self.player = player


class Choice(State):
    def __init__(self, player: PlayerType):
        State.__init__(self, 'choosing')
        self.player = player
        self.font_id = 0
        self.last_place = None
        self.last_card = None
        self.choice = 'guo'

    def entry_actions(self, state: GameState):
        self.font_id = 0
            
        if not state.players[self.player].use_ai:
            state.table.set_font(state.interrupt_states)
            
        peng_card = state.table[state.interrupt_card.id]
        self.last_place = peng_card.location
        self.last_card = peng_card
        peng_card.location = Vec2d(*render_config.CENTER_POS)
        peng_card.destination = Vec2d(*render_config.CENTER_POS)

    def do_actions(self, state: GameState):
        if not state.players[self.player].use_ai:
            mouse_point = pygame.mouse.get_pos()
            pressed_mouse = pygame.mouse.get_pressed()
            if pressed_mouse[0]:
                self.font_id = state.table.follow_mouse(mouse_point, self.font_id, self.player)
                if self.font_id >= 200:
                    self.choice = state.interrupt_states[self.font_id - 200]
                    return
                self.font_id = 0
        else:
            self.choice = self.player.AI.choice(self.player.manager.player_list[self.player.player]['now_card'],
                                                self.player.manager.table_card,
                                                self.player.manager.peng_card,
                                                self.player.choice_state_list)
            self.font_id = 200

    def check_conditions(self, state: GameState):
        if self.font_id >= 200:
            if self.choice == 'guo':
                if 'hu' in state.interrupt_states or \
                    ('gang' in state.interrupt_states and state.interrupt_player == self.player):
                    state.interrupt_states = []
                    return 'putting'
                state.interrupt_states = []
                self.last_card.location = self.last_place
                self.last_card.destination = self.last_place
                state.interrupt_player = PlayerType.EMPTY
                return 'waiting'
            else:
                return self.choice
        else:
            return None

    def exit_actions(self, state: GameState):
        self.font_id = 0
        state.table.remove_font()


class Wait(State):
    def __init__(self, player: PlayerType):
        State.__init__(self, 'waiting')
        self.player = player

    def check_conditions(self, game_state: GameState):
        if game_state.interrupt_player == self.player:
            return 'choosing'
        else:
            if self.player == game_state.now_player:
                return 'drawing'
            else:
                return None
            