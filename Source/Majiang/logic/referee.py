from __future__ import annotations

import sys


sys.path.append("./Source/Majiang/")

import copy

from typing import List, Optional, Tuple, Dict

from config import base_config
from logic.elements import Cards,LogicCard
from utils.constants import (
    CardType,
    BASE_CARD_TYPE
)


# def tidy_hands(cards: List[LogicCard]):
#     cards.sort(key=lambda x: x.id)
#     return cards


# def tidy_all(players: List["Source.Majiang.logic.player.Player"]):
#     for player in players:
#         id_list = []
#         for card in player.hands:
#             id_list.append(card.id)
#         player.hands.sort(key=lambda x: x.id)

#     return players


class Referee:  

    @staticmethod
    def send_card(players, cards: Cards):
        for player in players:
            player.hands.extend(cards.draw(base_config.INIT_CARD_NUMS))

    @staticmethod
    def get_all_laizi(cards: Cards, laizi_exp: Optional[LogicCard] = None):
        # 获取所有的癞子
        res: Cards = Cards
        cards: List[LogicCard] = sorted(cards.to_list(), key=lambda x: x.id, reverse=True)
        for card in cards:
            # 癞子统计
            if not laizi_exp and card.type == CardType.HUA:
                res.add(card)
            elif laizi_exp:
                if laizi_exp.num == card.num and laizi_exp.type == card.type:
                    res.add(card)
        return res

    @staticmethod
    def get_all_shunzi(cards: Cards):
        # 获取所有顺子
        all_shunzi: List[Cards] = []

        cards: List[LogicCard] = sorted(cards.to_list(), key=lambda x: x.id)
        card_nums = len(cards)
        last_add_cls = -1
        last_cls = -1

        for index, card in enumerate(cards):

            # 跳过字牌
            if card.type not in BASE_CARD_TYPE:
                continue
            
            if last_cls == card.cls:
                continue
            last_cls = card.cls
            
            shunzi: List[LogicCard] = [card]
            has_neighbor = False

            for i in range(index + 1, card_nums):
                
                # 若下一张为两种不同的数牌，或序号相差大于2，则直接退出
                if cards[i].type != card.type or cards[i].cls - card.cls > 2:
                    break

                if cards[i].num  - card.num == 1 and not has_neighbor:
                    has_neighbor = True
                    shunzi.append(cards[i])
                elif cards[i].num - card.num == 2 and has_neighbor:
                    shunzi.append(cards[i])
                    all_shunzi.append(Cards(shunzi))
                    break

        
        return all_shunzi

    @staticmethod
    def get_all_dazi(cards: Cards):
        # 获取所有搭子
        all_dazi: List[Cards] = []

        cards: List[LogicCard] = sorted(cards.to_list(), key=lambda x: x.id)
        card_nums = len(cards)
        last_add_cls = -1
        last_cls = -1

        for index, card in enumerate(cards):

            # 跳过字牌, 根据排序顺序，若遍历到第一张非数牌，则以后均为非数牌，直接退出
            if card.type not in BASE_CARD_TYPE:
                break
            
            if last_cls == card.cls:
                continue
            last_cls = card.cls
            
            # 从当前牌的下一张开始遍历
            for i in range(index + 1, card_nums):
                
                # 若下一张为两种不同的数牌，或序号相差大于2，则直接退出
                if cards[i].type != card.type or cards[i].cls - card.cls > 2:
                    break
                
                # 优先添加序号相差为1的搭子
                if cards[i].cls != last_add_cls and cards[i].num  - card.num == 1:
                    all_dazi.append(Cards([card, cards[i]]))
                    last_add_cls = cards[i].cls
                elif cards[i].num - card.num == 2:
                    all_dazi.append(Cards([card, cards[i]]))
                    break
                elif cards[i].cls == last_add_cls:
                    continue
        
        return all_dazi

    @staticmethod
    def get_all_kezi(cards: Cards, k_count: int = 3, laizi_exp: Optional[LogicCard] = None):
        # 获取所有刻
        all_kezi: List[Cards] = []

        cards: List[LogicCard] = sorted(cards.to_list(), key=lambda x: x.id)
        card_nums = len(cards)

        for index, card in enumerate(cards):
            
            kezi: List[LogicCard] = [card]
            count = 1

            for i in range(index + 1, card_nums):
                
                if card.cls == cards[i].cls and \
                    card.cls != all_kezi[-1][0].cls if all_kezi else True:
                    count += 1
                    kezi.append(cards[i])
                    if count == k_count:
                        all_kezi.append(Cards(kezi))
                        break
                else:
                    break
            
        
        return all_kezi

    @staticmethod
    def _evaluate(self, cards: List[LogicCard], depth: int = 0, now_max_depth: int = 0, max_depth: int = 4):
        all_kanzi = Referee.get_all_shunzi(cards) + Referee.get_all_kezi(cards)

        if len(all_kanzi) == 0:
            return depth
        else:
            depth += 1
            if depth == max_depth:
                return depth
        for kanzi in all_kanzi:
            evaluate_cards = copy.deepcopy(cards)

            for LogicCard in kanzi:
                evaluate_cards.remove(LogicCard)
            
            now_depth = Referee._evaluate(evaluate_cards, depth=depth, now_max_depth=now_max_depth, max_depth=max_depth)
            if now_depth > now_max_depth:
                    now_max_depth = now_depth
            
            if now_max_depth == max_depth:
                return now_max_depth
        
        return now_max_depth

    def check_win(self, cards: List[LogicCard]):
        '''胡牌判定'''
        
        # 找出所有对子
        all_duizi = Referee.get_all_kezi(cards, k_count=2)
        
        max_kan_nums = len(cards) // 3
        
        for duizi in all_duizi:
            
            evaluate_cards = copy.deepcopy(cards)
            for LogicCard in duizi:
                evaluate_cards.remove(LogicCard)
            
            if max_kan_nums == Referee._evaluate(evaluate_cards, max_depth=max_kan_nums):
                return True

        return False
    
if __name__ == "__main__":
    from pprint import pprint
    from utils.constants import CardMode
    from utils.time_counter import run_time, test
    all_cards = Cards(card_mode=CardMode.FULL)
    
    def gen_random_cards(count: int):
        random_cards = []
        for i in range(count):
            random_cards.append(all_cards.draw(14, replace=True))
        return random_cards
    
    # def test_fun(fun: function, cards_count: int, per_card_test: int):
    #     for i in 
    #     test(fun, per_card_test)
    
    
    cards = Cards([
        all_cards.get(0),
        all_cards.get(1),
        all_cards.get(2),
        
        all_cards.get(4),
        all_cards.get(8),
        all_cards.get(12),
        all_cards.get(16),
        all_cards.get(20),
        all_cards.get(24),
        all_cards.get(28),
        
        all_cards.get(32),
        all_cards.get(33),
        all_cards.get(34),
        
        all_cards.get(13)
    ])
    # print(cards)
            
            
    
    pprint(test(Referee.check_win)(cards))