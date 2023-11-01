import sys
from pprint import pprint
sys.path.append("./Source/Majiang/")

import copy
import random

from typing import List, Optional, Tuple, Dict

from config import base_config
from Source.Majiang.entity.entities import Table
from elements import LogicCard
from logic.player import Player
from logic.elements import Cards
from utils.constants import (
    CardType,
    BASE_CARD_TYPE
)


def tidy_hands(cards: List[LogicCard]):
    cards.sort(key=lambda x: x.id)
    return cards


def tidy_all(players: List[Player]):
    for player in players:
        id_list = []
        for card in player.hands:
            id_list.append(card.id)
        player.hands.sort(key=lambda x: x.id)

    return players

def id_to_cls(card_id: int):
    return (card_id - 1) // 4 + 1


class Referee:  

    @staticmethod
    def send_card(players: List[Player], cards: Cards):
        for player in players:
            player.hands.extend(cards.draw(base_config.INIT_CARD_NUMS))

    @staticmethod
    def get_all_laizi(cards: Cards, laizi_exp: Optional[LogicCard] = None):
        # 获取所有的癞子
        res: Cards = Cards()
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
        all_shunzi: List[List[LogicCard]] = []

        cards: List[LogicCard] = sorted(cards.to_list(), key=lambda x: x.id)
        card_nums = len(cards)

        for index, card in enumerate(cards):

            # 跳过字牌
            if card.type not in BASE_CARD_TYPE:
                continue
            
            shunzi: List[LogicCard] = [LogicCard]
            has_neighbor = False

            for i in range(index + 1, card_nums):
                
                if cards[i].type != card.type:
                    break

                if cards[i].type == card.type:
                    if cards[i].num - card.num > 2:
                        break
                    else:
                        if cards[i].num  - card.num == 1:
                            if has_neighbor:
                                continue
                            has_neighbor = True
                            shunzi.append(cards[i])
                        elif cards[i].num - card.num == 2 and has_neighbor:
                            shunzi.append(cards[i])
                            all_shunzi.append(Cards.from_list(shunzi))
                            break
                        else:
                            break
        
        return all_shunzi

    @staticmethod
    def get_all_dazi(cards: Cards):
        # 获取所有搭子
        all_dazi: List[Cards] = []

        cards: List[LogicCard] = sorted(cards.to_list(), key=lambda x: x.id)
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
                            all_dazi.append(Cards.from_list([card, cards[i]]))
                            break
                        elif cards[i].num - card.num == 2:
                            all_dazi.append(Cards.from_list([card, cards[i]]))
                            break
                        else:
                            break
        
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
                
                if cards[i].type != card.type:
                    break

                if cards[i].type == card.type:
                    if card.num == cards[i].num:
                        count += 1
                        kezi.append(cards[i])
                        if count == k_count:
                            all_kezi.append(Cards.from_list(kezi))
                            break
                    else:
                        break
            
        
        return all_kezi

    def _evaluate(self, cards: List[LogicCard], depth: int = 0, now_max_depth: int = 0, max_depth: int = 4):
        all_kanzi = self.get_all_shunzi(cards) + self.get_all_kezi(cards)

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
            
            now_depth = self._evaluate(evaluate_cards, depth=depth, now_max_depth=now_max_depth, max_depth=max_depth)
            if now_depth > now_max_depth:
                    now_max_depth = now_depth
            
            if now_max_depth == max_depth:
                return now_max_depth
        
        return now_max_depth

    def check_win(self, cards: List[LogicCard]):
        '''胡牌判定'''
        
        # 找出所有对子
        all_duizi = self.get_all_kezi(cards, k_count=2)
        
        max_kan_nums = len(cards) // 3
        
        for duizi in all_duizi:
            
            evaluate_cards = copy.deepcopy(cards)
            for LogicCard in duizi:
                evaluate_cards.remove(LogicCard)
            
            if max_kan_nums == self._evaluate(evaluate_cards, max_depth=max_kan_nums):
                return True

        return False
        