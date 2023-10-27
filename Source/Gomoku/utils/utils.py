from utils.constants import Player

def reverse_player(turn: Player) -> Player:
    if turn == Player.BLACK:
        return Player.WHITE
    else:
        return Player.BLACK