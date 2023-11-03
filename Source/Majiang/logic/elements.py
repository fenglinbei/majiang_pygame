import random

from typing import Optional, List, Dict

from utils.constants import CardType, CardMode, BASE_CARD_TYPE, Feng, Jian, Hua

class LogicCard:
    def __init__(self, card_type: CardType, num: int, card_cls: int, card_id: int):
        self.type = card_type
        self.num = num
        self.id = card_id
        self.cls = card_cls
    
    def __repr__(self) -> str:
        # return f"<Card: {self.type}, num: {self.num}, cls: {self.cls}, id: {self.id}>"
        if self.type == CardType.WANG:
            return str(self.num) + "m"
        elif self.type == CardType.TONG:
            return str(self.num) + "p"
        elif self.type == CardType.SUO:
            return str(self.num) + "s"
        elif self.type == CardType.FENG or self.type == CardType.JIAN:
            return str(self.num.value) + "z"
        elif self.type == CardType.HUA:
            return str(self.num.value) + "h"
    
    def __eq__(self, __value: object) -> bool:
        if __value.id == self.id:
            return True
        else:
            False
            
class Cards:
    
    def __init__(self, card_list: Optional[List[LogicCard]] = None, card_mode: Optional[CardMode] = None) -> None:
        if card_mode is not None:
            self.items = self.init_cards(card_mode)
        elif not card_list:
            self.items: Dict = {}
        elif card_list:
            self.items = {card.id: card for card in card_list}
            
    def __len__(self):
        return len(self.items)
    
    def __getitem__(self, index: int) -> LogicCard:
        return list(self.items.values())[index]
    
    def __delitem__(self, index: int):
        del self.items[index]
        
    def __add__(self, x):
        if isinstance(x, Cards):
            self.update(x)
            return self
        elif isinstance(x, LogicCard):
            self.items[x.id] = x
            return self

        return None

    def __repr__(self) -> str:
        return self.to_list().__repr__()
    
    def __iter__(self):
        self.index = 0
        return self
    
    def __next__(self):
        if self.index < len(self.items):
            result = self.__getitem__(self.index)
            self.index += 1
            return result
        else:
            raise StopIteration
    
    def update(self, x):
        self.items.update(x.items)

    def add(self, card: LogicCard):
        self.items[card.id] = card
    
    def get(self, card_id: int) -> LogicCard:
        return self.items[card_id]
    
    def remove(self, card: LogicCard):
        del self.items[card.id]
    
    def pop(self, key: int):
        self.items.pop(key)
        
    def to_list(self) -> List[LogicCard]:
        return list(self.items.values())

    @classmethod
    def from_list(cls, card_list: List[LogicCard]):
        cards = cls()
        cards.items = {card.id: card for card in card_list}
        return cards
    
    def draw_one(self) -> LogicCard:
        card = random.sample(list(self.items.values()), k=1)[0]
        del self.items[card.id]
        return random.sample(list(self.items.values()), k=1)[0]
    
    def draw(self, nums: int, replace: bool = False):
        card_list: List[LogicCard] = random.sample(list(self.items.values()), k=nums)
        if not replace:
            for card in card_list:
                del self.items[card.id]
        return Cards(card_list)
            
    @staticmethod
    def init_cards(card_mode: CardMode):
        card_id = 0
        card_cls = 0
        cards: Dict[int, LogicCard] = {}
        for card_type in CardType:

            if card_type in BASE_CARD_TYPE:
                for i in range(1, 10):
                    
                    for j in range(4):
                        cards[card_id] = LogicCard(card_type=card_type, num=i, card_cls=card_cls, card_id=card_id)
                        card_id += 1
                    
                    card_cls += 1
            
            elif card_mode == CardMode.ONLY_BASE:
                break

            elif card_mode != CardMode.ONLY_BASE:
                if card_type == CardType.FENG:
                    for feng in Feng:
                        for j in range(4):
                            cards[card_id] = LogicCard(card_type=card_type, num=feng, card_cls=card_cls, card_id=card_id)
                            card_id += 1
                        card_cls += 1
                elif card_type == CardType.JIAN:
                    for jian in Jian:
                        for j in range(4):
                            cards[card_id] = LogicCard(card_type=card_type, num=jian, card_cls=card_cls, card_id=card_id)
                            card_id += 1
                        card_cls += 1
                elif card_type == CardType.HUA and card_mode == CardMode.FULL:
                    for hua in Hua:
                        for j in range(1):
                            cards[card_id] = LogicCard(card_type=card_type, num=hua, card_cls=card_cls, card_id=card_id)
                            card_id += 1
                        card_cls += 1
        
        return cards