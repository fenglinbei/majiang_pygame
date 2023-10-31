import sys
from pprint import pprint
sys.path.append(".")

import copy
import random

from typing import List, Optional, Tuple

from config import config, base_config
from element.elements import Table
from elements import Player, Card
from utils.constants import (
    Feng,
    Jian,
    Hua,
    CardMode, 
    PlayerType, 
    CardType,
    BASE_CARD_TYPE
)
base_list = ["wan", "tong", "suo"]
feng_list = ["dong", "nan", "xi", "bei", "zhong", "fa", "bai"]
hua_list = ["chun", "xia", "qiu", "dong", "mei", "lan", "zhu", "ju"]
PLAYER_LIST = {1: {'name': "dong", 'now_card': [], 'put_card': {'p': [], 'g': []}},
               2: {'name': "nan", 'now_card': [], 'put_card': {'p': [], 'g': []}},
               3: {'name': "xi", 'now_card': [], 'put_card': {'p': [], 'g': []}},
               4: {'name': "bei", 'now_card': [], 'put_card': {'p': [], 'g': []}}}


class Logic:

    def __init__(self, table: Table, card_mode: int = CardMode.FULL):
        self.card_mode = card_mode

        self.card: List[Card] = []
        self.all_cards: List[Card] = self.init_cards(card_mode)
        self.players = self.init_player()
        self.table_cards = self.init_player()

        self.last_card_id = 0
        self.table = table
        self.peng_card = None
        self.last_put = 0
        self.last_player = 0
        self.peng_player = 0
        self.pg_state_list = []
        self.ks_look_count = 0
        self.last_winner = 1

    @staticmethod
    def init_player():
        players: List[Player] = []
        for player_type in PlayerType:
            players.append(Player(player_type=player_type))
        return players
    
    @staticmethod
    def init_cards(card_mode: CardMode):
        # 创建一副完整的牌
        card_id = 0
        cards: List[Card] = []

        for card_type in CardType:

            if card_type in BASE_CARD_TYPE:
                for i in range(1, 10):
                    for j in range(4):
                        cards.append(Card(card_type=card_type, num=i, card_id=card_id))
                        card_id += 1
            
            elif card_mode == CardMode.ONLY_BASE:
                break

            elif card_mode != CardMode.ONLY_BASE:
                if card_type == CardType.FENG:
                    for feng in Feng:
                        for j in range(4):
                            cards.append(Card(card_type=card_type, num=feng, card_id=card_id))
                            card_id += 1
                elif card_type == CardType.JIAN:
                    for jian in Jian:
                        for j in range(4):
                            cards.append(Card(card_type=card_type, num=jian, card_id=card_id))
                            card_id += 1
                elif card_type == CardType.HUA and card_mode == CardMode.FULL:
                    for hua in Hua:
                        for j in range(4):
                            cards.append(Card(card_type=card_type, num=hua, card_id=card_id))
                            card_id += 1

        return cards
        

    def reset(self):
        self.card = self.init_cards(self.card_mode)
        self.players = self.init_player()
        self.table_cards = self.init_player()
        self.send_card()

    def send_card(self):
        # 发牌
        c = 0
        for player in self.players:
            player.hands.extend(self.card[c:c + base_config.INIT_CARD_NUMS])
            c += base_config.INIT_CARD_NUMS
        self.cards = self.cards[c:]
        return True

    def draw_card(self, player: PlayerType):
        self.players[player].hands.append(self.card.pop())
        # printer.read_card(self.player_list, self.table_card)
        # printer.load_card(14)

    @staticmethod
    def tidy_all(players: List[Player]):
        # 整理手牌
        for player in players:
            id_list = []
            for card in player.hands:
                id_list.append(card.id)
            player.hands.sort(key=lambda card: card.id)

        return players

    @staticmethod
    def tidy_hands(cards: List[Card]):
        cards.sort(key=lambda x: x.id)
        return cards

    @staticmethod
    def id_to_cls(card_id):
        raise NotImplementedError
        return (card_id - 1) // 4 + 1

    def get_card(self, card_id: int):
        for card in self.all_cards:
            if card_id == card.id:
                return card
        return None

    @staticmethod
    def get_all_laizi(cards: List[Card], laizi_exp: Optional[Card] = None):
        # 获取所有的癞子
        res: List[Card] = []
        for card in cards:
            # 癞子统计
            if not laizi_exp and card.type == CardType.HUA:
                res.append(card)
            elif laizi_exp:
                if laizi_exp.num == card.num and laizi_exp.type == card.type:
                    res.append(card)
        return res

    @staticmethod
    def get_all_shunzi(cards: List[Card]):
        # 获取所有顺子
        all_shunzi: List[List[Card]] = []

        cards.sort(key=lambda x: x.id)
        card_nums = len(cards)

        for index, card in enumerate(cards):

            # 跳过字牌
            if card.type not in BASE_CARD_TYPE:
                continue
            
            shunzi: List[Card] = [card]
            has_neighbor = False

            for i in range(index + 1, card_nums):
                
                if cards[i].type != card.type:
                    break

                if cards[i].type == card.type:
                    if cards[i].num - card.num > 2:
                        break
                    else:
                        if cards[i].num  - card.num == 1:
                            has_neighbor = True
                            shunzi.append(cards[i])
                        elif cards[i].num - card.num == 2 and has_neighbor:
                            shunzi.append(cards[i])
                            all_shunzi.append(shunzi)
                            break
                        else:
                            break
        
        return all_shunzi

    @staticmethod
    def has_one_shunzi(cards: List[Card]):
        # 检查是含有顺子

        cards.sort(key=lambda x: x.id)
        card_nums = len(cards)

        for index, card in enumerate(cards):

            # 跳过字牌
            if card.type not in BASE_CARD_TYPE:
                continue
            
            shunzi: List[Card] = [card]
            has_neighbor = False

            for i in range(index + 1, card_nums):
                
                if cards[i].type != card.type:
                    break

                if cards[i].type == card.type:
                    if cards[i].num - card.num > 2:
                        break
                    else:
                        if cards[i].num  - card.num == 1:
                            has_neighbor = True
                            shunzi.append(cards[i])
                        elif cards[i].num - card.num == 2 and has_neighbor:
                            return True
                        else:
                            break
        
        return False

    @staticmethod
    def get_all_dazi(cards: List[Card]):
        # 获取所有搭子
        all_dazi: List[List[Card]] = []

        cards.sort(key=lambda x: x.id)
        card_nums = len(cards)

        for index, card in enumerate(cards):

            # 跳过字牌
            if card.type not in BASE_CARD_TYPE:
                continue

            for i in range(index + 1, card_nums):
                
                if cards[i].type != card.type:
                    break

                if cards[i].type == card.type:
                    if cards[i].num - card.num > 2:
                        break
                    else:
                        # 优先添加序号相差为1的搭子
                        if cards[i].num  - card.num == 1:
                            all_dazi.append([card, cards[i]])
                            break
                        elif cards[i].num - card.num == 2:
                            all_dazi.append([card, cards[i]])
                            break
                        else:
                            break
        
        return all_dazi

    @staticmethod
    def get_all_kezi(cards: List[Card], k_count: int = 3, laizi_exp: Optional[Card] = None):
        # 获取所有刻
        all_kezi: List[List[Card]] = []

        cards.sort(key=lambda x: x.id)
        card_nums = len(cards)

        for index, card in enumerate(cards):
            
            kezi: List[Card] = [card]
            count = 1

            for i in range(index + 1, card_nums):
                
                if cards[i].type != card.type:
                    break

                if cards[i].type == card.type:
                    if card.num == cards[i].num:
                        count += 1
                        kezi.append(cards[i])
                        if count == k_count:
                            all_kezi.append(kezi)
                            break
                    else:
                        break
            
        
        return all_kezi
    
    @staticmethod
    def has_one_kezi(cards: List[Card], k_count: int = 3, laizi_exp: Optional[Card] = None):
        # 检查是否含有刻子
        cards.sort(key=lambda x: x.id)
        card_nums = len(cards)

        for index, card in enumerate(cards):
            
            count = 1

            for i in range(index + 1, card_nums):
                
                if cards[i].type != card.type:
                    break

                if cards[i].type == card.type:
                    if card.num == cards[i].num:
                        count += 1
                        if count == k_count:
                            return True
                    else:
                        break
            
        return False

    def remove_card_by_id(self, ori_card_list, rm_card_list_by_id):
        for card_id in rm_card_list_by_id:
            for card in ori_card_list:
                if card['id'] == card_id:
                    ori_card_list.remove(card)
                    break
        return ori_card_list

    def move_card_to_table(self, move_id):
        card = self.table.get(move_id)
        flag = True
        remove_card = None
        for p in self.player_list:
            for c in self.player_list[p]['now_card']:
                if card.id == c['id']:
                    remove_card = c
                    flag = False
                    break
            if not flag:
                break
        self.player_list[card.player]['now_card'].remove(remove_card)
        self.table_card[card.player]['now_card'].append(remove_card)
        self.peng_card = remove_card

    def move_card_to_peng(self, move_id_list, player):
        for move_id in move_id_list:
            for p in self.player_list:
                for card in self.player_list[p]['now_card']:
                    if move_id == card['id']:
                        self.player_list[p]['now_card'].remove(card)
                        self.player_list[player]['put_card']['p'].append(card)
                        self.table_card[player]['put_card']['p'].append(card)

        for p in self.table_card:
            for card in self.table_card[p]['now_card']:
                if card['id'] in move_id_list:
                    self.table_card[p]['now_card'].remove(card)
                    self.player_list[player]['put_card']['p'].append(card)
                    self.table_card[player]['put_card']['p'].append(card)
                    return

    def move_card_to_gang(self, move_id_list, player):
        for move_id in move_id_list:
            for p in self.player_list:
                for card in self.player_list[p]['now_card']:
                    if move_id == card['id']:
                        self.player_list[p]['now_card'].remove(card)
                        self.player_list[player]['put_card']['g'].append(card)
                        self.table_card[player]['put_card']['g'].append(card)

                for card in self.player_list[p]['put_card']['p']:
                    if move_id == card['id']:
                        self.player_list[p]['put_card']['p'].remove(card)
                        self.table_card[player]['put_card']['p'].remove(card)
                        self.player_list[player]['put_card']['g'].append(card)
                        self.table_card[player]['put_card']['g'].append(card)

            for p in self.table_card:
                for card in self.table_card[p]['now_card']:
                    if move_id == card['id']:
                        self.table_card[p]['now_card'].remove(card)
                        self.player_list[player]['put_card']['g'].append(card)
                        self.table_card[player]['put_card']['g'].append(card)


    def evaluate(self, evaluate_cards_list: Optional[List[List[Card]]] = None, evaluate_input: Optional[List[Tuple[List[Card], List[List[Card]]]]] = None):

        evaluate_res: List[Tuple(List[Card], List[List[Card]])] = []
        
        if evaluate_input:
            for (cards, all_kanzi) in evaluate_input:
                if len(all_kanzi) == 0:
                    continue
                
                for kanzi in all_kanzi:
                    evaluate_cards = copy.deepcopy(cards)
                    # 移除一个坎子的牌
                    for card in kanzi:
                        evaluate_cards.remove(card)
                    
                    # 移除一个坎子后，若剩余牌还有坎子，则将剩余的手牌与坎子组合添加到结果中
                    evaluate_kanzi = self.get_all_shunzi(evaluate_cards) + self.get_all_kezi(evaluate_cards)
                    if len(evaluate_kanzi) > 0:
                        evaluate_res.append((evaluate_cards, evaluate_kanzi))
        
        else:
            for cards in evaluate_cards_list:
                # 检查当前手牌是否含有坎子
                all_kanzi = self.get_all_shunzi(cards) + self.get_all_kezi(cards)
                
                if len(all_kanzi) == 0:
                    continue
                
                for kanzi in all_kanzi:
                    evaluate_cards = copy.deepcopy(cards)

                    for card in kanzi:
                        evaluate_cards.remove(card)
                    
                    # 移除一个坎子后，若剩余牌还有坎子，则将剩余的手牌与坎子组合添加到结果中
                    evaluate_kanzi = self.get_all_shunzi(evaluate_cards) + self.get_all_kezi(evaluate_cards)
                    if len(evaluate_kanzi) > 0:
                        evaluate_res.append((evaluate_cards, evaluate_kanzi))


        return evaluate_res
    
    def _evaluate(self, cards: List[Card], depth: int = 0, max_depth: int = 4):
        all_kanzi = self.get_all_shunzi(cards) + self.get_all_kezi(cards)

        if len(all_kanzi) == 0:
            return depth
        else:
            if depth + 1 == max_depth:
                return depth + 1
        for kanzi in all_kanzi:
            evaluate_cards = copy.deepcopy(cards)
            pprint(kanzi)

            for card in kanzi:
                evaluate_cards.remove(card)
            
            return self._evaluate(evaluate_cards, depth=depth + 1, max_depth=max_depth)



    def loop_ks(self, cards: List[Card]):
        self.ks_look_count += 1

        # 坎子的数量，既顺子和刻子的总和，根据坎子数和手牌数量判断是否胡牌
        kanzi_count = 0

        def remove_card_by_count_id(ori_card_list):
            count_id = self.loop_s(ori_card_list)['id'] + self.loop_k(ori_card_list)['id']
            card_list_list_after_rm = []
            # 截取
            for sk_3 in count_id:
                card_list_after_rm = self.remove_card_by_id(copy.deepcopy(ori_card_list), sk_3)
                count_id_after_rm = self.loop_s(card_list_after_rm)['id'] + self.loop_k(card_list_after_rm)['id']
                if len(count_id_after_rm) > 0:
                    card_list_list_after_rm.append(card_list_after_rm)
            return card_list_list_after_rm

        # 当至少含有一个坎子时，坎子数+1
        all_kanzi = self.get_all_shunzi(cards) + self.get_all_kezi(cards)
        if len(all_kanzi) > 0:
            kanzi_count += 1
        else:
            return kanzi_count
        
        # 取走任意一个坎子，若剩余牌还含有坎子，则坎子数+1
        evaluate_res: List[Tuple[List[Card], List[List[Card]]]] = []
        for kanzi in all_kanzi:
            evaluate_cards = copy.deepcopy(cards)

            # 移除一个坎子的牌
            for card in kanzi:
                evaluate_cards.remove(card)
            
            # 移除一个坎子后，若剩余牌还有坎子，则将剩余的手牌与坎子组合添加到结果中
            evaluate_kanzi = self.get_all_shunzi(evaluate_cards) + self.get_all_kezi(evaluate_cards)
            if len(evaluate_kanzi) > 0:
                evaluate_res.append((evaluate_cards, evaluate_kanzi))

        if len(evaluate_res) > 0:
            kanzi_count += 1
        else:
            return kanzi_count

        # 第二步提取
        sec_card_lists = []
        sec_card_list = []
        for first_cards in first_card_list:
            sec_cards = remove_card_by_count_id(first_cards)
            if len(sec_cards) > 0:
                sec_card_lists.append(sec_cards)
        if len(sec_card_lists) > 0:
            for a in sec_card_lists:
                for b in a:
                    sec_card_list.append(b)
            k_s_count = 3
        else:
            return k_s_count
        # 第三步提取
        third_card_lists = []
        third_card_list = []
        for sec_cards in sec_card_list:
            third_cards = remove_card_by_count_id(sec_cards)
            if len(third_cards) > 0:
                third_card_lists.append(third_cards)
        if len(third_card_lists) > 0:
            for a in third_card_lists:
                for b in a:
                    third_card_list.append(b)
            k_s_count = 4
        return k_s_count

    def judge(self, card_list):
        # 胡牌判定
        eye_count = self.loop_k(card_list, k_count=2)
        max_count = 0
        is_win = False
        judgement = {'is_win': False, 'type': 0, 'count': max_count}
        for eyes in eye_count['id']:
            card_list_after_rm_eye = self.remove_card_by_id(copy.deepcopy(card_list), eyes)
            all_count = self.loop_ks(copy.deepcopy(card_list_after_rm_eye))
            if all_count >= max_count:
                max_count = all_count
            if all_count * 3 == len(card_list_after_rm_eye):
                is_win = True
                judgement = {'is_win': True, 'type': 1, 'count': all_count}
                break

        if is_win:
            return judgement
        else:
            judgement = {'is_win': False, 'type': 0, 'count': max_count}
            return judgement

    def check_state(self, card_id, card_list):
        state_list = []
        card = self.get(card_id)
        card_list['now_card'].append(card)
        k_count = self.loop_k(card_list['now_card'] + card_list['put_card']['p'], k_count=4, l_cls=[])
        if len(k_count['cls']) > 0:
            state_list.append('gang')
        if self.judge(card_list['now_card'])['is_win']:
            state_list.append('hu')
        return state_list

    def set_turn(self, put_id, player_id):
        self.pg_state_list = ['guo']
        self.last_put = put_id
        self.last_player = player_id
        put_cls = self.id_to_cls(put_id)
        for player in self.player_list:
            if player == player_id:
                continue
            k_2_list = self.loop_k(self.player_list[player]['now_card'], k_count=2, l_cls=[])['cls']
            k_3_list = self.loop_k(self.player_list[player]['now_card'], k_count=3, l_cls=[])['cls']
            for counts_k_2 in k_2_list:
                if put_cls in counts_k_2:
                    for count_k_3 in k_3_list:
                        if put_cls in count_k_3:
                            self.pg_state_list.append('peng')
                            self.pg_state_list.append('gang')
                            self.peng_player = player
                            return
                    self.pg_state_list.append('peng')
                    self.peng_player = player
                    return

if __name__ == "__main__":
    logic = Logic(None)

    cards = [
        logic.all_cards[0],
        logic.all_cards[1],
        logic.all_cards[2],

        logic.all_cards[4],
        logic.all_cards[8],
        logic.all_cards[12],
        logic.all_cards[16],
        logic.all_cards[20],
        logic.all_cards[24],
        logic.all_cards[28],
        logic.all_cards[29],

        logic.all_cards[32],
        logic.all_cards[33],
        logic.all_cards[34],
    ]

    res = logic._evaluate(cards, max_depth=len(cards) // 4)
    pprint(res)