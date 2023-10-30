# 参数获取
import os

# import dotenv

from utils.constants import Player

# dotenv.load_dotenv()

DEFAULTS = {
    'GAME_VERSION': 'V1.0',
    'REC_SIZE': 50,
    'MAP_POINT_SIZE': 8,
    'CHESS_LEN': 15,

    'INFO_WIDTH': 200,
    'BUTTON_WIDTH': 140,
    'BUTTON_HEIGHT': 50,

    'PLAYER_USED': Player.BLACK,
    'FIRST_HAND': False,
    'USE_AI': False
}


def get_env(key):
    return os.environ.get(key, DEFAULTS.get(key))


def get_bool_env(key):
    if isinstance(key, bool):
        return get_env(key).lower() == 'true'
    return key


def get_path(key):
    return os.path.join(get_env('DATA_PATH'), get_env(key))


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

        self.REC_SIZE = get_env('REC_SIZE')
        self.MAP_POINT_SIZE = get_env('MAP_POINT_SIZE')
        self.CHESS_LEN = get_env('CHESS_LEN')
        self.INFO_WIDTH = get_env('INFO_WIDTH')
        self.BUTTON_WIDTH = get_env('BUTTON_WIDTH')
        self.BUTTON_HEIGHT = get_env('BUTTON_HEIGHT')

        self.CHESS_RADIUS = self.REC_SIZE // 2 - 2
        self.MAP_WIDTH = self.CHESS_LEN * self.REC_SIZE
        self.MAP_HEIGHT = self.CHESS_LEN * self.REC_SIZE

        self.LOGIC_MAP_HIGHT = self.CHESS_LEN
        self.LOGIC_MAP_WIDTH = self.CHESS_LEN

        self.SCREEN_WIDTH = self.MAP_WIDTH + self.INFO_WIDTH
        self.SCREEN_HEIGHT = self.MAP_HEIGHT

        self.PLAYER_USED = get_env('PLAYER_USED')
        self.FIRST_HAND = get_env('FIRST_HAND')
        self.USE_AI = get_env('USE_AI')


config = Config()
ai_config = AIConfig()
