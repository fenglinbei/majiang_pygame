from typing import Tuple

from entity.entities import Table
from utils.constants import PlayerType
from utils.vector import Vec2d

def follow_mouse(table: Table, pos: Tuple[int, int], last_id: int, player: PlayerType):
    entity_id = table.pos_in_entity(pos, player)
    
    if last_id > 0:
        card = table[last_id]
        if card.can_followed:
            card.location = Vec2d(pos[0] - card.size[0] / 2, pos[1] - card.size[1] / 2)
            card.destination = card.location
            return last_id
        
    elif entity_id > 0:
        card = table[entity_id]
        if card.can_followed:
            card.location = Vec2d(pos[0] - card.size[0] / 2, pos[1] - card.size[1] / 2)
            card.destination = card.location
            return entity_id
    return entity_id