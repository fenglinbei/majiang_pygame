from typing import List

from logic.state import StateMachine, GameState
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
        
        
    def think(self):
        self.brain.think()
        
    def init_state(self):
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