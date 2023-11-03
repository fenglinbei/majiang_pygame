from typing import List, Union

from logic.state import StateMachine, PutCard, DrawCard, PengCard, GangCard, Hu, Wait, Choice, End
from utils.constants import PlayerType
from logic.elements import LogicCard, Cards



class Player:

    def __init__(self, player_type: PlayerType, use_ai: bool) -> None:
        self.player_type = player_type

        self.hands: Cards = Cards()
        
        self.pengs: List[Cards] = []
        self.gangs: List[Cards] = []
        self.chis: List[Cards] = []
        
        self.puts: Cards = Cards()
        
        self.brain = StateMachine()
        self.use_ai = use_ai
        
        # if use_ai:
        #     self.AI = AI(logic, player_type)
            
        self.draw_card_id = 0
        self.choice_states = []
        self.peng_cls = []
        
    def put_card(self, card_id: int):
        for card in self.hands:
            if card.id == card_id:
                self.puts.add(card)
                self.hands.remove(card)
                break
    
    def draw_card(self, card: Union[LogicCard, Cards]):
        if isinstance(card, Cards):
            self.hands + card
        else:
            self.hands.add(card)
        
    def peng_card(self, cards: Cards):
        self.pengs.append(cards)
        for card in cards:
            self.hands.remove(card)
            
    def gang_card(self, cards: Cards):
        self.gangs.append(cards)
        for card in cards:
            self.hands.remove(card)
        
        
    def think(self, game_state):
        self.brain.think(game_state)
        
    def init_state(self):
        put_state = PutCard(self.player_type)
        draw_state = DrawCard(self.player_type)
        peng_state = PengCard(self.player_type)
        gang_state = GangCard(self.player_type)
        hu_state = Hu(self.player_type)
        wait_state = Wait(self.player_type)
        choice_state = Choice(self.player_type)
        end_state = End(self.player_type)
        
        self.brain.add_state(put_state)
        self.brain.add_state(draw_state)
        self.brain.add_state(peng_state)
        self.brain.add_state(gang_state)
        self.brain.add_state(hu_state)
        self.brain.add_state(wait_state)
        self.brain.add_state(choice_state)
        self.brain.add_state(end_state)