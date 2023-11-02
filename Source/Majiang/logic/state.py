import copy
import pygame

from typing import Dict, List

from utils.vector import Vec2d
# from logic.player import Player
from logic.referee import Referee
from logic.elements import Cards
from entity.entities import Table
from config import render_config, base_config
from utils.constants import PlayerType, InterruptState, CardType


            
        

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

    def think(self, state: GameState):
        if self.active_state is None:
            return
        self.active_state.do_actions(state)
        
        new_state_name = self.active_state.check_conditions()
        if new_state_name is not None:
            self.set_state(new_state_name)

    def set_state(self, new_state_name: str):
        if self.active_state is not None:
            self.active_state.exit_actions()
        self.active_state = self.states[new_state_name]
        self.active_state.entry_actions()



class PutCard(State):
    """打出一张牌"""
    def __init__(self, player: Player):
        State.__init__(self, 'putting')
        self.player = player
        self.card_is_choice = False
        self.card_is_arrived = False
        self.choice_entity_id = 0
        self.card = None

    def do_actions(self, state: GameState):
        if self.player.use_ai:
            if not self.card_is_choice:
                self.last_put_card_id = self.player.AI.put_card(manager.player_list[self.player.player]['now_card'],
                                                                manager.table_card, self.player.player)[0]
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
                self.choice_entity_id = state.table.follow_mouse(mouse_point, self.last_put_card_id, self.player.player_type)
            else:
                if self.choice_entity_id > 0 and \
                   (render_config.CENTER_POS[0] - render_config.RADIUS < mouse_point[0] < render_config.CENTER_POS[0] + render_config.RADIUS) and \
                   (render_config.CENTER_POS[1] - render_config.RADIUS < mouse_point[1] < render_config.CENTER_POS[1] + render_config.RADIUS):
                
                    self.card_is_arrived = True
                    self.player.put_card(self.choice_entity_id)
                    return
                self.choice_entity_id = 0
            self.card_is_arrived = False

    def check_conditions(self):
        if self.card_is_arrived:
            return 'waiting'
        else:
            return None

    def exit_actions(self, state: GameState):
        if self.card_is_arrived:
            state.last_player = self.player.player_type
            state.check_interrupt(self.choice_entity_id, self.player.player_type)

        self.choice_entity_id = -1
        self.card_is_arrived = False
        self.card_is_choice = False


class DrawCard(State):
    """摸牌"""
    def __init__(self, player: Player):
        State.__init__(self, 'drawing')
        self.player = player

    def do_actions(self, state: GameState):
        self.player.draw_card = state.cards.draw_one()

    def check_conditions(self):
        state_list = self.player.manager.check_state(self.player.draw_card_id,
                                                     copy.deepcopy(self.player.manager.player_list[self.player.player]))
        state_list.append('guo')
        self.player.choice_state_list = state_list
        if len(state_list) == 1:
            if len(self.player.manager.card) == 1:
                return 'hu'
            return 'putting'
        else:
            return 'choosing'

    def exit_actions(self):
        self.player.manager.player_list[self.player.player]["now_card"].append(self.player.manager.card[0])
        self.player.manager.card.remove(self.player.manager.card[0])
        self.player.printer.read_card(self.player.manager.player_list, self.player.manager.table_card)
        self.player.printer.load_card(14)


class PengCard(State):
    def __init__(self, player):
        State.__init__(self, 'peng')
        self.player = player

    def do_actions(self):
        peng_card_id = self.player.manager.last_put
        peng_card_id_list = []
        peng_card_cls = self.player.manager.id_to_cls(peng_card_id)
        k_2_list = self.player.manager.loop_k(self.player.manager.player_list[self.player.player]['now_card'],
                                              k_count=2, l_cls=[])
        for k_2_cls_num in range(len(k_2_list['cls'])):
            if peng_card_cls in k_2_list['cls'][k_2_cls_num]:
                peng_card_id_list = k_2_list['id'][k_2_cls_num]
                break
        peng_card_id_list.append(peng_card_id)
        self.player.manager.move_card_to_peng(peng_card_id_list, self.player.player)
        card_num = 0
        gang_num = len(self.player.manager.player_list[self.player.player]['put_card']['g']) // 4
        peng_num = len(self.player.manager.player_list[self.player.player]['put_card']['p']) // 3
        move_dis = (gang_num + peng_num - 1) * (16 + 3 * self.player.printer.p[0])
        self.player.peng_cls_list.append((peng_card_cls, move_dis))
        if move_dis < 0:
            move_dis = 0
        for peng_card_id in peng_card_id_list:
            card = self.player.manager.table.get(peng_card_id)
            location = self.player.printer.peng_place[self.player.player]
            if self.player.player == 1:
                if card.player != 1:
                    if card.player == 2:
                        card.image = pygame.transform.rotate(card.image, 270)
                    elif card.player == 4:
                        card.image = pygame.transform.rotate(card.image, 90)
                    card.player = 1
                    card.size = [card.image.get_width(), card.image.get_height()]

                card.destination = Vec2d(location[0] - (card.size[0] + 1) * card_num - move_dis, location[1])
                card.show_flag = True
                card.is_player_card = False
                card.speed = 1000
            elif self.player.player == 2:
                if card.player != 2:
                    if card.player == 1 or card.player == 3:
                        card.image = pygame.transform.rotate(card.image, 270)
                        card.image = pygame.transform.rotate(card.image, 180)
                    else:
                        card.image = pygame.transform.rotate(card.image, 180)
                    card.player = 2
                    card.size = [card.image.get_width(), card.image.get_height()]

                card.destination = Vec2d(location[0], location[1] + (card.size[1] + 1) * card_num + move_dis)
                card.show_flag = True
                card.is_player_card = False
                card.speed = 1000
            elif self.player.player == 3:
                if card.player != 3:
                    if card.player == 2:
                        card.image = pygame.transform.rotate(card.image, 270)
                    elif card.player == 4:
                        card.image = pygame.transform.rotate(card.image, 90)
                    card.player = 3
                    card.size = [card.image.get_width(), card.image.get_height()]

                card.destination = Vec2d(location[0] + (card.size[0] + 1) * card_num + move_dis, location[1])
                card.show_flag = True
                card.is_player_card = False
                card.speed = 1000
            else:
                if card.player != 4:
                    if card.player == 1 or card.player == 3:
                        card.image = pygame.transform.rotate(card.image, -90)
                    else:
                        card.image = pygame.transform.rotate(card.image, 180)
                    card.player = 4
                    card.size = [card.image.get_width(), card.image.get_height()]

                card.destination = Vec2d(location[0], location[1] - (card.size[1] + 1) * card_num - move_dis)
                card.show_flag = True
                card.is_player_card = False
                card.speed = 1000
            card_num += 1

    def check_conditions(self):
        return 'putting'

    def exit_actions(self):
        if self.player.manager.peng_player != 1:
            self.player.manager.last_player = self.player.manager.peng_player - 1
        else:
            self.player.manager.last_player = 4
        self.player.manager.peng_player = 0
        self.player.manager.pg_state_list = []


class GangCard(State):
    pass

    def __init__(self, player):
        State.__init__(self, 'gang')
        self.player = player

    def __init__(self, player):
        State.__init__(self, 'gang')
        self.player = player

    def do_actions(self):
        gang_card = self.player.manager.get(self.player.manager.last_put)
        k_4_list = self.player.manager.loop_k(self.player.manager.player_list[self.player.player]['now_card'] +
                                              self.player.manager.player_list[self.player.player]['put_card']['p'] +
                                              [gang_card],
                                              k_count=4, l_cls=[])
        if len(k_4_list['id']) == 0:
            print(self.player.manager.player_list[self.player.player]['now_card'] +
                  self.player.manager.player_list[self.player.player]['put_card']['p'] +
                  [gang_card])
        gang_card_id_list = k_4_list['id'][0]
        self.player.manager.move_card_to_gang(gang_card_id_list, self.player.player)
        card_num = 0
        gang_num = len(self.player.manager.player_list[self.player.player]['put_card']['g']) // 4
        peng_num = len(self.player.manager.player_list[self.player.player]['put_card']['p']) // 3
        move_dis = (gang_num + peng_num - 1) * (16 + 3 * self.player.printer.p[0])
        for peng_card in self.player.peng_cls_list:
            if self.player.manager.id_to_cls(self.player.draw_card_id) == peng_card[0]:
                move_dis = peng_card[1]
        if move_dis < 0:
            move_dis = 0
        for gang_card_id in gang_card_id_list:
            card = self.player.manager.table.get(gang_card_id)
            location = self.player.printer.peng_place[self.player.player]
            if self.player.player == 1:
                if card.player != 1:
                    if card.player == 2:
                        card.image = pygame.transform.rotate(card.image, 270)
                    elif card.player == 4:
                        card.image = pygame.transform.rotate(card.image, 90)
                    card.player = 1
                    card.size = [card.image.get_width(), card.image.get_height()]

                if card_num == 3:
                    card.destination = Vec2d(location[0] - (card.size[0] + 1) * (card_num - 2) - move_dis,
                                             location[1] - 6)
                    card.show_flag = True
                    card.is_player_card = False
                    card.speed = 1000
                    return

                card.destination = Vec2d(location[0] - (card.size[0] + 1) * card_num - move_dis, location[1])
                card.show_flag = True
                card.is_player_card = False
                card.speed = 1000
            elif self.player.player == 2:
                if card.player != 2:
                    if card.player == 1:
                        card.image = pygame.transform.rotate(card.image, 270)
                        card.image = pygame.transform.rotate(card.image, 180)
                    elif card.player == 3:
                        card.image = pygame.transform.rotate(card.image, 270)
                    card.player = 2
                    card.size = [card.image.get_width(), card.image.get_height()]

                if card_num == 3:
                    card.destination = Vec2d(location[0] - 6,
                                             location[1] + (card.size[1] + 1) * (card_num - 2) + move_dis)
                    card.show_flag = True
                    card.is_player_card = False
                    card.speed = 1000
                    return

                card.destination = Vec2d(location[0], location[1] + (card.size[1] + 1) * card_num + move_dis)
                card.show_flag = True
                card.is_player_card = False
                card.speed = 1000
            elif self.player.player == 3:
                if card.player != 3:
                    if card.player == 2:
                        card.image = pygame.transform.rotate(card.image, 270)
                    elif card.player == 4:
                        card.image = pygame.transform.rotate(card.image, 90)
                    card.player = 3
                    card.size = [card.image.get_width(), card.image.get_height()]

                if card_num == 3:
                    card.destination = Vec2d(location[0] + (card.size[0] + 1) * (card_num - 2) + move_dis,
                                             location[1] + 6)
                    card.show_flag = True
                    card.is_player_card = False
                    card.speed = 1000
                    return

                card.destination = Vec2d(location[0] + (card.size[0] + 1) * card_num + move_dis, location[1])
                card.show_flag = True
                card.is_player_card = False
                card.speed = 1000
            else:
                if card.player != 4:
                    if card.player == 1 or card.player == 3:
                        card.image = pygame.transform.rotate(card.image, -90)
                    else:
                        card.image = pygame.transform.rotate(card.image, 180)
                    card.player = 4
                    card.size = [card.image.get_width(), card.image.get_height()]

                if card_num == 3:
                    card.destination = Vec2d(location[0] + 6,
                                             location[1] - (card.size[1] + 1) * (card_num - 2) - move_dis)
                    card.show_flag = True
                    card.is_player_card = False
                    card.speed = 1000
                    return

                card.destination = Vec2d(location[0], location[1] - (card.size[1] + 1) * card_num - move_dis)
                card.show_flag = True
                card.is_player_card = False
                card.speed = 1000
            card_num += 1

    def check_conditions(self):
        return 'drawing'

    def exit_actions(self):
        if self.player.manager.peng_player != 1:
            self.player.manager.last_player = self.player.manager.peng_player - 1
        else:
            self.player.manager.last_player = 4
        self.player.manager.peng_player = 0
        self.player.manager.pg_state_list = []


class Hu(State):
    def __init__(self, player):
        State.__init__(self, 'hu')
        self.player = player

    def entry_actions(self):
        judgement = self.player.manager.judge(self.player.manager.player_list[self.player.player]['now_card'])
        self.player.printer.set_text(judgement, self.player.player)
        for player in players:
            player.brain.set_state('end')
        self.player.manager.last_winner = self.player.player


class End(State):
    def __init__(self, player):
        State.__init__(self, 'end')
        self.player = player


class Choice(State):
    def __init__(self, player):
        State.__init__(self, 'choosing')
        self.player = player
        self.font_id = 0
        self.last_place = None
        self.last_card = None
        self.choice = 'guo'

    def entry_actions(self):
        self.font_id = 0
        if len(self.player.choice_state_list) <= 1:
            self.player.choice_state_list = self.player.manager.pg_state_list
        if not self.player.use_ai:
            self.player.printer.set_font(copy.deepcopy(self.player.choice_state_list), self.player.player)
        if self.player.manager.peng_player != 0:
            peng_card = self.player.manager.table.get(self.player.manager.peng_card['id'])
            self.last_place = peng_card.location
            self.last_card = peng_card
            peng_card.location = Vec2d(*render_config.CENTER_POS)
            peng_card.destination = Vec2d(*render_config.CENTER_POS)
        # print(self.player.choice_state_list)

    def do_actions(self):
        if not self.player.use_ai:
            mouse_point = pygame.mouse.get_pos()
            pressed_mouse = pygame.mouse.get_pressed()
            if pressed_mouse[0]:
                self.font_id = printer.follow_mouse(mouse_point, self.font_id, self.player.player)
                if self.font_id >= 200:
                    self.choice = self.player.choice_state_list[self.font_id - 200]
                    return
                self.font_id = 0
        else:
            self.choice = self.player.AI.choice(self.player.manager.player_list[self.player.player]['now_card'],
                                                self.player.manager.table_card,
                                                self.player.manager.peng_card,
                                                self.player.choice_state_list)
            self.font_id = 200

    def check_conditions(self):
        if self.font_id >= 200:
            if self.choice == 'guo':
                if 'hu' in self.player.choice_state_list or \
                        ('gang' in self.player.choice_state_list and
                         (self.player.manager.last_player + 1 == self.player.player or
                          (self.player.player == 1 and self.player.manager.last_player == 4))):
                    self.player.manager.pg_state_list = []
                    self.player.choice_state_list = []
                    return 'putting'
                self.player.manager.pg_state_list = []
                self.player.choice_state_list = []
                if self.player.manager.peng_player != 0:
                    self.last_card.location = self.last_place
                    self.last_card.destination = self.last_place
                self.player.manager.peng_player = 0
                return 'waiting'
            else:
                return self.choice
        else:
            return None

    def exit_actions(self):
        self.font_id = 0
        self.player.printer.remove_font()


class Wait(State):
    def __init__(self, player):
        State.__init__(self, 'waiting')
        self.player = player

    def check_conditions(self):
        if self.player.manager.peng_player == self.player.player:
            return 'choosing'
        else:
            if self.player.manager.peng_player != 0:
                return None
            if self.player.manager.last_player + 1 == self.player.player or (
                    self.player.manager.last_player == 4 and self.player.player == 1):
                return 'drawing'
            else:
                return None
        

class GameState:
    def __init__(self, table: Table) -> None:
        self.cards = Cards(card_mode=base_config.CARD_MODE)
        self.players = self.init_player()
        
        self.last_player = base_config.INIT_PLAYER
        self.interrupt_player = PlayerType.EMPTY
        
        self.table = table
    
    def init_player(self):
        players: List[Player] = []
        for player_type in PlayerType:
            if player_type == PlayerType.EMPTY:
                continue
            if player_type == base_config.INIT_PLAYER:
                players.append(Player(player_type, use_ai=False))
            else:
                players.append(Player(player_type, use_ai=True))
        return players
    
    def check_interrupt(self, card_id: int, now_player: PlayerType, is_putting: bool = False, is_drawing: bool = False):
        interrupt_states = [InterruptState.GUO]
        interrupt_card = self.cards[card_id]
        self.last_player = now_player
        
        if is_putting:
            if interrupt_card.type == CardType.HUA:
                return []
            
            for player in self.players:
                if player.player_type == now_player:
                    continue
                all_duizi = Referee.get_all_kezi(player.hands, k_count=2)
                all_kezi = Referee.get_all_kezi(player.hands, k_count=3)
                
                for duizi in all_duizi:
                    if put_cls in list(map(lambda x: x.cls, duizi)):
                        for kezi in all_kezi:
                            if put_cls in list(map(lambda x: x.cls, kezi)):
                                interrupt_states.append(InterruptState.PENG)
                                interrupt_states.append(InterruptState.GANG)
                                
                                self.interrupt_player = player
                                return interrupt_states
                        interrupt_states.append(InterruptState.PENG)
                        self.interrupt_player = player
                        return interrupt_states
                    
            return []
        elif is_drawing:
            if len(self.players[now_player].pengs + Referee.get_all_kezi(self.players[now_player].hands, k_count=3)) > 0:
                 interrupt_states.append(InterruptState.GANG)
            if Referee.check_win(self.players[now_player].hands + interrupt_card):
                interrupt_states.append(InterruptState.HU)
            
            return interrupt_states
    
    def check_state(self, card_id: int, LogicCard_list):
        state_list = []
        LogicCard = self.get(card_id)
        LogicCard_list['now_LogicCard'].append(LogicCard)
        k_count = self.loop_k(LogicCard_list['now_LogicCard'] + LogicCard_list['put_LogicCard']['p'], k_count=4, l_cls=[])
        if len(k_count['cls']) > 0:
            state_list.append('gang')
        if self.judge(LogicCard_list['now_LogicCard'])['is_win']:
            state_list.append('hu')
        return state_list