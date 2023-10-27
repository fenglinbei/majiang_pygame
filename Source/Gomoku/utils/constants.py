from enum import IntEnum


class Player(IntEnum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2
    

class ChessType(IntEnum):
    NONE = 0
    SLEEP_TWO = 1
    LIVE_TWO = 2
    SLEEP_THREE = 3
    LIVE_THREE = 4
    CHONG_FOUR = 5
    LIVE_FOUR = 6
    LIVE_FIVE = 7


class Color:
    LIGHT_YELLOW = (247, 238, 214)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    PLAYER_BLACK = (88, 87, 86)
    PLAYER_WHITE = (255, 251, 240)