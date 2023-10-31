from Source.Majiang.utils.vector import Vec2d
import copy
import Source.Majiang.assets_processor.processor as processor
import pygame
import Source.Majiang.logic.logic as logic
from pygame.locals import *
from Source.Majiang.mj_AI import AI
from sys import exit





class StateMachine(object):
    def __init__(self):
        self.states = {}
        self.active_state = None

    def add_state(self, state):
        self.states[state.name] = state

    def think(self):
        if self.active_state is None:
            return
        self.active_state.do_actions()
        new_state_name = self.active_state.check_conditions()
        if new_state_name is not None:
            self.set_state(new_state_name)

    def set_state(self, new_state_name):
        if self.active_state is not None:
            self.active_state.exit_actions()
        self.active_state = self.states[new_state_name]
        self.active_state.entry_actions()


class State(object):
    def __init__(self, name):
        self.name = name

    def do_actions(self):
        pass

    def check_conditions(self):
        pass

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass


class PutCard(State):
    def __init__(self, player):
        State.__init__(self, 'putting')
        self.player = player
        self.card_is_choice = False
        self.card_is_arrived = False
        self.last_put_card_id = 0
        self.card = None

    def do_actions(self):
        if self.player.use_ai:
            if not self.card_is_choice:
                self.last_put_card_id = self.player.AI.put_card(manager.player_list[self.player.player]['now_card'],
                                                                manager.table_card, self.player.player)[0]
                self.card_is_choice = True
                self.card = self.player.manager.table.get(self.last_put_card_id)
                self.card.destination = Vec2d(*CENTER_POS)
                self.card.show_flag = True
            if self.card.location != Vec2d(*CENTER_POS):
                self.card_is_arrived = False
            else:
                self.player.manager.move_card_to_table(self.last_put_card_id)
                self.card_is_choice = False
                self.card_is_arrived = True
        else:
            mouse_point = pygame.mouse.get_pos()
            pressed_mouse = pygame.mouse.get_pressed()
            if pressed_mouse[0]:
                self.last_put_card_id = printer.follow_mouse(mouse_point, self.last_put_card_id, self.player.player)
            else:
                if (mouse_point[0] - CENTER_POS[0]) ** 2 + (
                        mouse_point[1] - CENTER_POS[1]) ** 2 <= RADIUS ** 2 and self.last_put_card_id > 0:
                    self.card_is_arrived = True
                    self.player.manager.move_card_to_table(self.last_put_card_id)
                    return
                self.last_put_card_id = 0
            self.card_is_arrived = False

    def check_conditions(self):
        if self.card_is_arrived:
            return 'waiting'
        else:
            return None

    def exit_actions(self):
        if self.card_is_arrived:
            self.player.manager.last_player = self.player.player
            self.player.manager.set_turn(self.last_put_card_id, self.player.player)
            self.player.manager.player_list = self.player.manager.tidy_card(self.player.manager.player_list)
        self.player.printer.read_card(self.player.manager.player_list, self.player.manager.table_card)
        self.player.printer.load_card(14)
        self.last_put_card_id = 0
        self.card_is_arrived = False
        self.card_is_choice = False
        # print(self.player.manager.ks_look_count)


class DrawCard(State):
    def __init__(self, player):
        State.__init__(self, 'drawing')
        self.player = player

    def do_actions(self):
        self.player.draw_card_id = self.player.manager.card[0]['id']

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
            peng_card.location = Vec2d(*CENTER_POS)
            peng_card.destination = Vec2d(*CENTER_POS)
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


class Player(object):
    def __init__(self, player_num, card_manager, card_printer, use_ai):
        self.player = player_num
        self.brain = StateMachine()
        self.use_ai = use_ai
        self.AI = AI(card_manager, player_num)
        self.manager = card_manager
        self.printer = card_printer
        put_state = PutCard(self)
        draw_state = DrawCard(self)
        peng_state = PengCard(self)
        gang_state = GangCard(self)
        hu_state = Hu(self)
        wait_state = Wait(self)
        choice_state = Choice(self)
        end_state = End(self)
        self.brain.add_state(put_state)
        self.brain.add_state(draw_state)
        self.brain.add_state(peng_state)
        self.brain.add_state(gang_state)
        self.brain.add_state(hu_state)
        self.brain.add_state(wait_state)
        self.brain.add_state(choice_state)
        self.brain.add_state(end_state)
        self.draw_card_id = 0
        self.choice_state_list = []
        self.peng_cls_list = []


class Printer(object):

    def __init__(self, table):
        self.table = table
        self.path = './data/image/img.png'
        self.back = './data/image/green.png'
        self.font = './data/image/font.png'
        self.src = processor.mjPic(self.path, self.back, self.font)
        self.img_dic = {1: [], 2: [], 3: [], 4: []}
        self.img_dic_put = {1: [], 2: [], 3: [], 4: []}
        card_img = self.src[0]
        self.p = [card_img.get_width(), card_img.get_height()]
        self.font_list = self.src.font_list
        self.font_dic = {'hu': self.src.font_list[0], 'peng': self.src.font_list[1],
                         'gang': self.src.font_list[2], 'guo': self.src.font_list[3]}
        self.font_size = self.src.font_list[0].get_size()
        self.font_place = (3 * RADIUS + 9 * self.p[0],
                           4 * RADIUS + 0.5 * ((6 / 5) * RADIUS + 3 * self.p[1]) - 64)
        self.peng_place = {2: (SCREEN_SIZE[0] - 12 - self.p[1], 12),
                           1: (SCREEN_SIZE[0] - 12 - self.p[0], SCREEN_SIZE[1] - 12 - self.p[1]),
                           3: (12, 12),
                           4: (12, SCREEN_SIZE[0] - 12 - self.p[0])}
        self.place = {1: [(3 * RADIUS - 4 * self.p[0],
                           4 * RADIUS + 0.5 * ((6 / 5) * RADIUS - 3 * self.p[1])),
                          (3 * RADIUS + 7 * self.p[0],
                           (26 / 5) * RADIUS)],
                      2: [(4 * RADIUS + 0.5 * ((6 / 5) * RADIUS - 3 * self.p[1]),
                           3 * RADIUS + 3 * self.p[0]),
                          ((26 / 5) * RADIUS,
                           3 * RADIUS - 3 * RADIUS + 5 * self.p[0])],
                      3: [(3 * RADIUS + 3 * self.p[0],
                           (4 / 5) * RADIUS + 0.5 * ((6 / 5) * RADIUS - 3 * self.p[1]) + 2 * self.p[1]),
                          (3 * RADIUS - 3 * RADIUS + 5 * self.p[0],
                           (4 / 5) * RADIUS - self.p[1])],
                      4: [((4 / 5) * RADIUS + 0.5 * ((6 / 5) * RADIUS - 3 * self.p[1]) + 2 * self.p[1],
                           3 * RADIUS - 4 * self.p[0]),
                          ((4 / 5) * RADIUS - self.p[1], 3 * RADIUS + 7 * self.p[0])]}
        self.text = ''
        self.text_2 = ''

    def read_card(self, players, table_cards):
        self.clean_card()
        for player in players:
            cards = players[player]['now_card']
            table_card = table_cards[player]['now_card']
            for card in cards:
                card_img = self.src[card['cls']]
                if player == 1:
                    self.img_dic[player].append([card_img, self.src[0],
                                                 card['cls'], card['id']])
                elif player == 2:
                    self.img_dic[player].append([pygame.transform.rotate(card_img, 90),
                                                 pygame.transform.rotate(self.src[0], 90),
                                                 card['cls'], card['id']])
                elif player == 3:
                    self.img_dic[player].append([card_img,
                                                 self.src[0],
                                                 card['cls'], card['id']])
                elif player == 4:
                    self.img_dic[player].append([pygame.transform.rotate(card_img, 270),
                                                 pygame.transform.rotate(self.src[0], 90),
                                                 card['cls'], card['id']])

            for card in table_card:
                card_img = self.src[card['cls']]
                if player == 1:
                    self.img_dic_put[player].append([card_img, self.src[0],
                                                     card['cls'], card['id']])
                elif player == 2:
                    self.img_dic_put[player].append([pygame.transform.rotate(card_img, 90),
                                                     pygame.transform.rotate(self.src[0], 90),
                                                     card['cls'], card['id']])
                elif player == 3:
                    self.img_dic_put[player].append([card_img,
                                                     self.src[0],
                                                     card['cls'], card['id']])
                elif player == 4:
                    self.img_dic_put[player].append([pygame.transform.rotate(card_img, 270),
                                                     pygame.transform.rotate(self.src[0], 90),
                                                     card['cls'], card['id']])

        return True

    def clean_card(self):
        self.img_dic = {1: [], 2: [], 3: [], 4: []}
        self.img_dic_put = {1: [], 2: [], 3: [], 4: []}

    def load_card(self, step):
        self.table.reset_player_card()
        init_step = step
        pw, ph = self.p[0] + 1, self.p[1] + 1
        for player in range(1, 5):

            if len(self.img_dic[player]) < step:
                step = len(self.img_dic[player])
            else:
                step = init_step

            if player == 1:
                for num in range(step):
                    card = Card(self.img_dic[player][num][0], self.img_dic[player][num][1])
                    card.location = Vec2d(self.place[player][1][0] - (step - num) * pw,
                                          self.place[player][1][1])
                    card.destination = card.location
                    card.player = 1
                    card.cls, card.id = self.img_dic[player][num][2], self.img_dic[player][num][3]
                    self.table.add_entity(card)
                step = init_step

                for num in range(len(self.img_dic_put[player])):
                    card = Card(self.img_dic_put[player][num][0], self.img_dic_put[player][num][1])
                    card.location = Vec2d(self.place[player][0][0] + (num % 8) * pw,
                                          self.place[player][0][1] + (num // 8) * ph)
                    card.destination = card.location
                    card.player = 1
                    card.can_followed = False
                    card.show_flag = True
                    card.cls, card.id = self.img_dic_put[player][num][2], self.img_dic_put[player][num][3]
                    self.table.add_entity(card)


            elif player == 2:
                for num in range(step):
                    card = Card(self.img_dic[player][num][0], self.img_dic[player][num][1])
                    card.location = Vec2d(self.place[player][1][0], self.place[player][1][1] + (step - num) * pw)
                    card.destination = card.location
                    card.player = 2
                    card.cls, card.id = self.img_dic[player][num][2], self.img_dic[player][num][3]
                    self.table.add_entity(card)
                step = init_step

                for num in range(len(self.img_dic_put[player])):
                    card = Card(self.img_dic_put[player][num][0], self.img_dic_put[player][num][1])
                    card.location = Vec2d(self.place[player][0][0] + (num // 8) * ph,
                                          self.place[player][0][1] - (num % 8) * pw)
                    card.destination = card.location
                    card.player = 2
                    card.can_followed = False
                    card.show_flag = True
                    card.cls, card.id = self.img_dic_put[player][num][2], self.img_dic_put[player][num][3]
                    self.table.add_entity(card)

            elif player == 3:
                for num in range(step):
                    card = Card(self.img_dic[player][num][0], self.img_dic[player][num][1])
                    card.location = Vec2d(self.place[player][1][0] + (step - num) * pw, self.place[player][1][1])
                    card.destination = card.location
                    card.player = 3
                    card.cls, card.id = self.img_dic[player][num][2], self.img_dic[player][num][3]
                    self.table.add_entity(card)
                step = init_step

                for num in range(len(self.img_dic_put[player])):
                    card = Card(self.img_dic_put[player][num][0], self.img_dic_put[player][num][1])
                    card.location = Vec2d(self.place[player][0][0] - (num % 8) * pw,
                                          self.place[player][0][1] - (num // 8) * ph)
                    card.destination = card.location
                    card.player = 3
                    card.can_followed = False
                    card.show_flag = True
                    card.cls, card.id = self.img_dic_put[player][num][2], self.img_dic_put[player][num][3]
                    self.table.add_entity(card)

            elif player == 4:
                for num in range(step):
                    card = Card(self.img_dic[player][num][0], self.img_dic[player][num][1])
                    card.location = Vec2d(self.place[player][1][0], self.place[player][1][1] - (step - num) * pw)
                    card.destination = card.location
                    card.player = 4
                    card.cls, card.id = self.img_dic[player][num][2], self.img_dic[player][num][3]
                    self.table.add_entity(card)
                step = init_step

                for num in range(len(self.img_dic_put[player])):
                    card = Card(self.img_dic_put[player][num][0], self.img_dic_put[player][num][1])
                    card.location = Vec2d(self.place[player][0][0] - (num // 8) * ph,
                                          self.place[player][0][1] + (num % 8) * pw)
                    card.destination = card.location
                    card.player = 4
                    card.can_followed = False
                    card.show_flag = True
                    card.cls, card.id = self.img_dic_put[player][num][2], self.img_dic_put[player][num][3]
                    self.table.add_entity(card)

    def follow_mouse(self, pos, last_id, now_player):
        card_id = self.table.pos_in_card(pos, now_player)
        if last_id > 0:
            card = self.table.get(last_id)
            if card.can_followed:
                card.location = Vec2d(pos[0] - card.size[0] / 2, pos[1] - card.size[1] / 2)
                card.destination = card.location
                return last_id
        elif card_id > 0:
            card = self.table.get(card_id)
            if card.can_followed:
                card.location = Vec2d(pos[0] - card.size[0] / 2, pos[1] - card.size[1] / 2)
                card.destination = card.location
                return card_id
        return card_id

    def set_font(self, state_list, player):
        state_num = 0
        for state in state_list:
            card = Card(self.font_dic[state], self.font_dic[state])
            card.location = Vec2d(self.font_place[0] - (state_num * (self.font_size[0] + 16)), self.font_place[1])
            card.destination = card.location
            card.can_followed = False
            card.player = player
            card.id = 200 + state_num
            self.table.add_entity(card)
            state_num += 1

    def remove_font(self):
        for state_num in range(200, 204):
            try:
                self.table.remove_entity(state_num)
            except:
                return

    def set_text(self, judgement, win_player):
        if judgement['is_win']:
            self.text = 'winner   is   %d' % win_player
            self.text_2 = ''
        else:
            self.text = 'game    over'
            self.text_2 = ''

