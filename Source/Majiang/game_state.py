from typing import List

from logic.player import Player
from logic.referee import Referee
from logic.elements import Cards
from entity.entities import Table
from config import base_config
from utils.constants import PlayerType, InterruptState, CardType


class GameState:
    def __init__(self, table: Table) -> None:
        self.cards = Cards(card_mode=base_config.CARD_MODE)
        self.now_player = base_config.INIT_PLAYER
        self.players = self.init_player()
        self.draw_cards()
        self.last_player = PlayerType.EMPTY
        self.winner = PlayerType.EMPTY
        self.interrupt_player = PlayerType.EMPTY
        
        self.table = table
        
        self.table.load_cards(self.cards)
    
    def restart_game(self):
        self.table.reset_entity()

        self.now_player = self.winner
        self.players = self.init_player()
        self.draw_cards()
        
        self.last_player = PlayerType.EMPTY
        self.winner = PlayerType.EMPTY
        self.interrupt_player = PlayerType.EMPTY
    
    def init_player(self):
        players: List[Player] = []
        for player_type in PlayerType:
            if player_type == PlayerType.EMPTY:
                continue
            
            if player_type == base_config.INIT_PLAYER:
                player = Player(player_type, use_ai=False)
            else:
                player = Player(player_type, use_ai=True)
            
            if player_type == self.now_player:
                player.brain.set_state("drawing")
            else:
                player.brain.set_state("waiting")
                
            players.append(player)
            
        return players
    
    def update(self):
        self.table.update_cards(self.players)
    
    def next_player(self):
        if self.now_player != PlayerType.BEI:
            self.now_player += 1
        else:
            self.now_player = PlayerType.DONG
        return self.now_player
    
    def draw_cards(self):
        for player in self.players:
            player.draw_card(self.cards.draw(13))
    
    def check_interrupt(self, card_id: int, now_player: PlayerType, is_putting: bool = False, is_drawing: bool = False):
        self.interrupt_states = [InterruptState.GUO]
        self.interrupt_card = self.cards.get(card_id)
        self.last_player = now_player
        
        if is_putting:
            if self.interrupt_card.type == CardType.HUA:
                return []
            
            for player in self.players:
                if player.player_type == now_player:
                    continue
                all_duizi = Referee.get_all_kezi(player.hands, k_count=2)
                all_kezi = Referee.get_all_kezi(player.hands, k_count=3)
                
                for duizi in all_duizi:
                    if self.interrupt_card.cls == duizi[0].cls:
                        for kezi in all_kezi:
                            if self.interrupt_card.cls == kezi[0].cls:
                                self.interrupt_states.append(InterruptState.PENG)
                                self.interrupt_states.append(InterruptState.GANG)
                                
                                self.interrupt_player = player
                                return self.interrupt_states
                        self.interrupt_states.append(InterruptState.PENG)
                        self.interrupt_player = player
                        return self.interrupt_states
                    
            return []
        elif is_drawing:
            if Referee.get_all_kezi(self.players[now_player].hands, k_count=4) > 0:
                self.interrupt_states.append(InterruptState.GANG)
            
            else:
                for kezi in self.players[now_player].pengs:
                    if self.interrupt_card.cls == kezi[0].cls:
                        self.interrupt_states.append(InterruptState.GANG)
                        break
            
            
            if Referee.check_win(self.players[now_player].hands + self.interrupt_card):
                self.interrupt_states.append(InterruptState.HU)
            
            return self.interrupt_states if len(self.interrupt_states) > 1 else []