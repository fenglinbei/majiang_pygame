from typing import List

from utils.constants import PlayerType, CardType

class Card:
    def __init__(self, card_type: CardType, num: int, card_id: int):
        self.type = card_type
        self.num = num
        self.id = card_id
    
    def __repr__(self) -> str:
        return f"Card: {self.type} num: {self.num} id: {self.id}"
    
    def __eq__(self, __value: object) -> bool:
        if __value.id == self.id:
            return True
        else:
            False

class Player:

    def __init__(self, player_type: PlayerType) -> None:
        self.player_type = player_type

        self.hands: List[Card] = []
        self.pengs: List[Card] = []
        self.gangs: List[Card] = []
        self.chis: List[Card] = []