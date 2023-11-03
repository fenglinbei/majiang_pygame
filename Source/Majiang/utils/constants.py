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

    WANG = 1
    TONG = 2
    SUO = 2
    FENG = 4
    JIAN = 5
    HUA = 6

BASE_CARD_TYPE = [CardType.WANG, CardType.TONG, CardType.SUO]

class Feng(IntEnum):
    DONG = 1
    NAN = 2
    XI = 3
    BEI = 4

class Jian(IntEnum):
    ZHONG = 5
    FA = 6
    BAI = 7


class Hua(IntEnum):
    CHUN = 1
    XIA = 2
    QIU = 3
    DONG = 4
    MEI = 5
    LAN = 6
    ZHU = 7
    JU = 8
    
class InterruptState(IntEnum):
    GUO = 0
    PENG = 1
    GANG = 2
    CHI = 3
    HU = 4