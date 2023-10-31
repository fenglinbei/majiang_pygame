# 参数获取
import os
from utils.constants import CardMode

DEFAULTS = {
    'GAME_VERSION': 'V1.0',
    'SCREEN_WIDTH': 960,
    'SCREEN_HEIGHT': 960,
    'FONT_SIZE': 36,

    'CARD_MOVEMENT_SPEED': 450
}


def get_env(key):
    return os.environ.get(key, DEFAULTS.get(key))


def get_bool_env(key):
    if isinstance(key, bool):
        return get_env(key).lower() == 'true'
    return key


def get_path(key):
    return os.path.join(get_env('DATA_PATH'), get_env(key))


class BaseConfig:
    def __init__(self) -> None:
        self.CARD_MODE = CardMode.NOT_HUA
        self.INIT_CARD_NUMS = 13

class AIConfig:

    def __init__(self):
        self.AI_SEARCH_DEPTH = 2
        self.AI_LIMITED_MOVE_NUM = 20
        self.SCORE_MAX = 0x7fffffff
        self.SCORE_MIN = -1 * self.SCORE_MAX
        self.SCORE_FIVE, self.SCORE_FOUR, self.SCORE_SFOUR = 10000, 10000, 5000
        self.SCORE_THREE, self.SCORE_STHREE, self.SCORE_TWO, self.SCORE_STWO = 4900, 600, 2450, 300


class Config:
    """ Configuration class. """

    def __init__(self):
        self.ai = AIConfig()

        self.GAME_VERSION = get_env('GAME_VERSION')

        self.SCREEN_WIDTH = get_env('SCREEN_WIDTH')
        self.SCREEN_HEIGHT = get_env('SCREEN_HEIGHT')
        self.FONT_SIZE = get_env('FONT_SIZE')

        self.CENTER_POS = (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2)
        self.RADIUS = self.SCREEN_WIDTH / 6

        self.CARD_MOVEMENT_SPEED = get_env('CARD_MOVEMENT_SPEED')

config = Config()
base_config = BaseConfig()
