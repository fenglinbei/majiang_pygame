from enum import IntEnum

class PlayerType(IntEnum):
    EMPTY = 0
    DONG = 1
    NAN = 2
    XI = 3
    BEI = 4

class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    PALE_GREEN = (200, 255, 200)

class CardMode(IntEnum):
    FULL = 0
    ONLY_BASE = 1
    NOT_HUA = 2

class CardType(IntEnum):

    WANG = 0
    TONG = 1
    SUO = 2
    FENG = 3
    JIAN = 4
    HUA = 5

BASE_CARD_TYPE = [CardType.WANG, CardType.TONG, CardType.SUO]

class Feng(IntEnum):
    DONG = 0
    NAN = 1
    XI = 2
    BEI = 3

class Jian(IntEnum):
    ZHONG = 4
    FA = 5
    BAI = 6


class Hua(IntEnum):
    CHUN = 7
    XIA = 8
    QIU = 9
    DONG = 10
    MEI = 11
    LAN = 12
    ZHU = 13
    JU = 14
    
class InterruptState(IntEnum):
    GUO = 0
    PENG = 1
    GANG = 2
    CHI = 3
    HU = 4