import time
import random

from pprint import pprint
from typing import List

from config import ai_config
from map.game_map import Map
from utils.constants import ChessType, Player

from utils.utils import reverse_player


CHESS_TYPE_NUM = len(ChessType.__members__)

count_change_list = [1, 2, 2, 3, 3, 4, 4, 5]

FIVE = ChessType.LIVE_FIVE

FOUR, THREE, TWO = ChessType.LIVE_FOUR,\
                   ChessType.LIVE_THREE,\
                   ChessType.LIVE_TWO

SFOUR, STHREE, STWO = ChessType.CHONG_FOUR,\
                      ChessType.SLEEP_THREE,\
                      ChessType.SLEEP_TWO

SCORE_FIVE, SCORE_FOUR, SCORE_SFOUR = ai_config.SCORE_FIVE,\
                                      ai_config.SCORE_FOUR,\
                                      ai_config.SCORE_SFOUR

SCORE_THREE, SCORE_STHREE, SCORE_TWO, SCORE_STWO = ai_config.SCORE_THREE,\
                                                   ai_config.SCORE_STHREE,\
                                                   ai_config.SCORE_TWO,\
                                                   ai_config.SCORE_STWO


class ChessAI:

    def __init__(self, chess_len: str):
        self.len = chess_len
        # [horizon, vertical, left diagonal, right diagonal]
        self.record = [[[0, 0, 0, 0] for x in range(chess_len)] for y in range(chess_len)]
        self.count = [[0 for x in range(CHESS_TYPE_NUM)] for i in range(2)]

    def reset(self):
        for y in range(self.len):
            for x in range(self.len):
                for i in range(4):
                    self.record[y][x][i] = 0

        for i in range(len(self.count)):
            for j in range(len(self.count[0])):
                self.count[i][j] = 0

    @staticmethod
    def click(game_map, x, y, turn):
        game_map.click(x, y, turn)

    def isWin(self, board, turn):
        return self.evaluate(board, turn, True)

    # evaluate score of point, to improve pruning efficiency
    def evaluatePointScore(self, board, x, y, mine, opponent):
        dir_offset = [(1, 0), (0, 1), (1, 1), (1, -1)]  # direction from left to right
        for i in range(len(self.count)):
            for j in range(len(self.count[0])):
                self.count[i][j] = 0

        board[y][x] = mine
        self.evaluatePoint(board, x, y, mine, opponent, self.count[mine - 1])
        mine_count = self.count[mine - 1]
        board[y][x] = opponent
        self.evaluatePoint(board, x, y, opponent, mine, self.count[opponent - 1])
        opponent_count = self.count[opponent - 1]
        board[y][x] = 0

        m_score = self.getScore(mine_count, opponent_count)[0]
        o_score = self.getScore(mine_count, opponent_count)[1]

        return m_score, o_score

    # check if has a none empty position in it's radius range
    def hasNeighbor(self, board, x, y, radius):
        start_x, end_x = (x - radius), (x + radius)
        start_y, end_y = (y - radius), (y + radius)

        for i in range(start_y, end_y + 1):
            for j in range(start_x, end_x + 1):
                if i >= 0 and i < self.len and j >= 0 and j < self.len:
                    if board[i][j] != 0:
                        return True
        return False

    # get all positions near chess
    def genmove(self, board, player):
        fives = []
        mfours, ofours = [], []
        msfours, osfours = [], []

        mine = player
        opponent = reverse_player(player)

        moves = []
        radius = 1

        for y in range(self.len):
            for x in range(self.len):
                if board[y][x] == 0 and self.hasNeighbor(board, x, y, radius):
                    mscore, oscore = self.evaluatePointScore(board, x, y, mine, opponent)
                    point = (max(mscore, oscore), x, y)

                    if mscore >= SCORE_FIVE or oscore >= SCORE_FIVE:
                        fives.append(point)
                    elif mscore >= SCORE_FOUR:
                        mfours.append(point)
                    elif oscore >= SCORE_FOUR:
                        ofours.append(point)
                    elif mscore >= SCORE_SFOUR:
                        msfours.append(point)
                    elif oscore >= SCORE_SFOUR:
                        osfours.append(point)

                    moves.append(point)

        if len(fives) > 0: return fives

        if len(mfours) > 0: return mfours

        if len(ofours) > 0:
            if len(msfours) == 0:
                return ofours
            else:
                return ofours + msfours
        
        if not moves:
            start_y = 4
            start_x = 4
            end_y = self.len - 5
            end_x = self.len - 5

            y = random.randint(start_y, end_y)
            x = random.randint(start_x, end_x)

            point = (1, x, y)
            moves.append(point)
            return moves

        moves.sort(reverse=True)

        # FIXME: decrease think time: only consider limited moves with higher scores
        if self.maxdepth > 2 and len(moves) > ai_config.AI_LIMITED_MOVE_NUM:
            moves = moves[:ai_config.AI_LIMITED_MOVE_NUM]
            
        return moves

    def _search(self, board, player, depth, alpha=ai_config.SCORE_MIN, beta=ai_config.SCORE_MAX):
        score = self.evaluate(board, player)


        if depth <= 0 or abs(score) >= SCORE_FIVE:
            return score

        moves = self.genmove(board, player)

        bestmove = None
        self.alpha += len(moves)

        # if there are no moves, just return the score
        if len(moves) == 0:
            return score

        for _, x, y in moves:
            board[y][x] = player

            score = - self._search(board, reverse_player(player), depth - 1, -beta, -alpha)

            board[y][x] = 0
            self.belta += 1

            # alpha/beta pruning
            if score > alpha:
                alpha = score
                bestmove = (x, y)
                if alpha >= beta:
                    break


        if depth == self.maxdepth and bestmove:
            self.bestmove = bestmove

        return alpha

    def search(self, board: List[List[int]], player: Player, depth: int):
        self.maxdepth = depth
        self.bestmove = None
        score = self._search(board, player, depth)
        self.best_count = self.count
        x, y = self.bestmove
        return score, x, y

    def findBestChess(self, board: List[List[int]], player: Player):
        time1 = time.time()
        self.alpha = 0
        self.belta = 0
        score, x, y = self.search(board, player, ai_config.AI_SEARCH_DEPTH)
        time2 = time.time()
        pprint(board)
        pprint('time[%.2f] (%d, %d), score[%d] alpha[%d] belta[%d] bestcount%s' % (
        (time2 - time1), x, y, score, self.alpha, self.belta, self.best_count))
        return (x, y)

    def getPointScore(self, count):
        score = 0
        if count[FIVE] > 0:
            return SCORE_FIVE

        if count[FOUR] > 0:
            return SCORE_FOUR

        # FIXME: the score of one chong four and no live three should be low, set it to live three
        if count[SFOUR] > 1:
            score += count[SFOUR] * SCORE_SFOUR
        elif count[SFOUR] > 0 and count[THREE] > 0:
            score += count[SFOUR] * SCORE_SFOUR
        elif count[SFOUR] > 0:
            score += SCORE_THREE

        if count[THREE] > 1:
            score += 5 * SCORE_THREE
        elif count[THREE] > 0:
            score += SCORE_THREE

        if count[STHREE] > 0:
            score += count[STHREE] * SCORE_STHREE
        if count[TWO] > 0:
            score += count[TWO] * SCORE_TWO
        if count[STWO] > 0:
            score += count[STWO] * SCORE_STWO

        return score

        # calculate score, FIXME: May Be Improved

    def getScore(self, mine_count, opponent_count):
        mscore, oscore = 0, 0
        if mine_count[FIVE] > 0:
            return (SCORE_FIVE, 0)
        if opponent_count[FIVE] > 0:
            return (0, SCORE_FIVE)

        if mine_count[SFOUR] >= 2:
            mine_count[FOUR] += 1
        if opponent_count[SFOUR] >= 2:
            opponent_count[FOUR] += 1

        if mine_count[FOUR] > 0:
            return (9050, 0)
        if mine_count[SFOUR] > 0:
            return (9040, 0)

        if opponent_count[FOUR] > 0:
            return (0, 9030)
        if opponent_count[SFOUR] > 0 and opponent_count[THREE] > 0:
            return (0, 9020)

        if mine_count[THREE] > 0 and opponent_count[SFOUR] == 0:
            return (9010, 0)

        if (opponent_count[THREE] > 1 and mine_count[THREE] == 0 and mine_count[STHREE] == 0):
            return (0, 9000)

        if opponent_count[SFOUR] > 0:
            oscore += 400

        if mine_count[THREE] > 1:
            mscore += 500
        elif mine_count[THREE] > 0:
            mscore += 100

        if opponent_count[THREE] > 1:
            oscore += 2000
        elif opponent_count[THREE] > 0:
            oscore += 400

        if mine_count[STHREE] > 0:
            mscore += mine_count[STHREE] * 10
        if opponent_count[STHREE] > 0:
            oscore += opponent_count[STHREE] * 10

        if mine_count[TWO] > 0:
            mscore += mine_count[TWO] * 6
        if opponent_count[TWO] > 0:
            oscore += opponent_count[TWO] * 6

        if mine_count[STWO] > 0:
            mscore += mine_count[STWO] * 2
        if opponent_count[STWO] > 0:
            oscore += opponent_count[STWO] * 2

        return (mscore, oscore)

    def countChange(self, count):
        for i in [0, 1]:
            for num in range(CHESS_TYPE_NUM):
                count[i][num] /= count_change_list[num]
        return count

    def evaluate(self, board, turn, checkWin=False):
        self.reset()

        if turn == Player.BLACK:
            mine = 1
            opponent = 2
        else:
            mine = 2
            opponent = 1

        for y in range(self.len):
            for x in range(self.len):
                if board[y][x] == mine:
                    self.evaluatePoint(board, x, y, mine, opponent)
                elif board[y][x] == opponent:
                    self.evaluatePoint(board, x, y, opponent, mine)
        self.count = self.countChange(self.count)
        mine_count = self.count[mine - 1]
        opponent_count = self.count[opponent - 1]
        if checkWin:
            return mine_count[FIVE] > 0
        else:
            mscore, oscore = self.getScore(mine_count, opponent_count)
            return (mscore - oscore)

    def evaluatePoint(self, board, x, y, mine, opponent, count=None):
        dir_offset = [(1, 0), (0, 1), (1, 1), (1, -1)]  # direction from left to right
        for i in range(4):
            self.analysisLine(board, x, y, dir_offset[i], mine, opponent)

    # line is fixed len 9: XXXXMXXXX
    def getLine(self, board, x, y, dir_offset, mine, opponent):
        line = [0 for i in range(9)]

        tmp_x = x + (-5 * dir_offset[0])
        tmp_y = y + (-5 * dir_offset[1])
        for i in range(9):
            tmp_x += dir_offset[0]
            tmp_y += dir_offset[1]
            if (tmp_x < 0 or tmp_x >= self.len or
                    tmp_y < 0 or tmp_y >= self.len):
                line[i] = opponent  # set out of range as opponent chess
            else:
                line[i] = board[tmp_y][tmp_x]

        return line

    def analysisLine(self, board, x, y, dir_offset, mine, opponent):

        empty = Player.EMPTY
        left_idx, right_idx = 4, 4

        line = self.getLine(board, x, y, dir_offset, mine, opponent)

        while right_idx < 8:
            if line[right_idx + 1] != mine:
                break
            right_idx += 1
        while left_idx > 0:
            if line[left_idx - 1] != mine:
                break
            left_idx -= 1

        left_range, right_range = left_idx, right_idx
        while right_range < 8:
            if line[right_range + 1] == opponent:
                break
            right_range += 1
        while left_range > 0:
            if line[left_range - 1] == opponent:
                break
            left_range -= 1

        chess_range = right_range - left_range + 1
        if chess_range < 5:
            return None

        m_range = right_idx - left_idx + 1

        # M:mine chess, P:opponent chess or out of range, X: empty
        if m_range >= 5:
            self.count[mine - 1][FIVE] += 1

        # Live Four : XMMMMX
        # Chong Four : XMMMMP, PMMMMX
        if m_range == 4:
            left_empty = right_empty = False
            if line[left_idx - 1] == empty:
                left_empty = True
            if line[right_idx + 1] == empty:
                right_empty = True
            if left_empty and right_empty:
                self.count[mine - 1][FOUR] += 1
            elif left_empty or right_empty:
                self.count[mine - 1][SFOUR] += 1

        # Chong Four : MXMMM, MMMXM, the two types can both exist
        # Live Three : XMMMXX, XXMMMX
        # Sleep Three : PMMMX, XMMMP, PXMMMXP
        if m_range == 3:
            left_empty = right_empty = False
            left_four = right_four = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:  # MXMMM
                    self.count[mine - 1][SFOUR] += 1
                    left_four = True
                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:  # MMMXM
                    self.count[mine - 1][SFOUR] += 1
                    right_four = True
                right_empty = True

            if left_four or right_four:
                pass
            elif left_empty and right_empty:
                if chess_range > 5:  # XMMMXX, XXMMMX
                    self.count[mine - 1][THREE] += 1
                else:  # PXMMMXP
                    self.count[mine - 1][STHREE] += 1
            elif left_empty and line[left_idx - 2] == empty:  # XXMMMP
                self.count[mine - 1][STHREE] += 1
            elif right_empty and line[right_idx + 2] == empty:  # PMMMXX,
                self.count[mine - 1][STHREE] += 1

        # Chong Four: MMXMM, only check right direction
        # Live Three: XMXMMX, XMMXMX the two types can both exist
        # Sleep Three: PMXMMX, XMXMMP, PMMXMX, XMMXMP
        # Live Two: XMMX
        # Sleep Two: PMMX, XMMP
        if m_range == 2:
            left_empty = right_empty = False
            left_three = right_three = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:
                    if line[left_idx - 3] == empty:
                        if line[right_idx + 1] == empty:  # XXMXMMXXX, XMXMMXXXX
                            self.count[mine - 1][THREE] += 1
                        else:  # XMXMMP
                            self.count[mine - 1][STHREE] += 1
                        left_three = True
                    elif line[left_idx - 3] == opponent:  # PMXMMX
                        if line[right_idx + 1] == empty:
                            self.count[mine - 1][STHREE] += 1
                            left_three = True
                elif line[left_idx - 2] == empty:
                    if line[left_idx - 3] == mine:  # MXXMM
                        self.count[mine - 1][STHREE] += 1
                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:
                    if line[right_idx + 3] == mine:  # MMXMM
                        self.count[mine - 1][SFOUR] += 1
                        right_three = True
                    elif line[right_idx + 3] == empty:
                        if right_idx + 4 <= 8:
                            if line[right_idx + 4] == mine:  # MMXMXM
                                self.count[mine - 1][STHREE] += 1
                        if left_empty:  # XMMXMX
                            self.count[mine - 1][THREE] += 1
                        else:  # PMMXMX
                            self.count[mine - 1][STHREE] += 1
                        right_three = True
                    elif left_empty:  # XMMXMP
                        self.count[mine - 1][STHREE] += 1
                        right_three = True
                elif line[right_idx + 2] == empty:
                    if line[right_idx + 3] == mine:  # MMXXM
                        self.count[mine - 1][STHREE] += 1

                right_empty = True

            if left_three or right_three:
                pass
            elif left_empty and right_empty:  # XMMX
                self.count[mine - 1][TWO] += 1
            elif left_empty or right_empty:  # PMMX, XMMP
                self.count[mine - 1][STWO] += 1

        if m_range == 1:
            left_empty = right_empty = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:
                    if line[left_idx - 3] == empty:
                        if line[left_idx - 4] == mine:  # MXMXM
                            self.count[mine - 1][STHREE] += 1
                        if line[right_idx + 1] == opponent:  # XXMXMP
                            self.count[mine - 1][STWO] += 1
                        else:
                            self.count[mine - 1][TWO] += 1  # XMXMXXX
                    elif line[left_idx - 3] == mine:
                        if line[left_idx - 4] == empty:
                            if line[right_idx + 1] == empty:  # XMMXMXXXX
                                self.count[mine - 1][THREE] += 1
                            elif line[right_idx + 1] == opponent:  # XMMXMP
                                self.count[mine - 1][STHREE] += 1
                        elif line[left_idx - 4] == mine:  # MMMXMXXXX
                            self.count[mine - 1][SFOUR] += 1
                        elif line[left_idx - 4] == opponent and line[right_idx + 1] == empty:  # PMMXMX
                            self.count[mine - 1][STHREE] += 1
                elif line[left_idx - 2] == empty:
                    if line[left_idx - 3] == mine:
                        if line[left_idx - 4] == empty:  # XMXXMXX
                            self.count[mine - 1][TWO] += 1
                        if line[left_idx - 4] == mine:  # MMXXM
                            self.count[mine - 1][STHREE] += 1
                    if line[right_idx + 1] == empty:
                        if line[right_idx + 2] == mine and line[right_idx + 3] == opponent:
                            self.count[mine - 1][STWO] += 1  # XXMXMPP
                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:
                    if left_empty and line[left_idx - 2] == mine:  # MXMXM
                        self.count[mine - 1][STHREE] += 1
                    if line[right_idx + 3] == empty:
                        if line[right_idx + 4] == mine:  # MXMXM
                            self.count[mine - 1][STHREE] += 1
                        if left_empty:  # XXXMXMX
                            self.count[mine - 1][TWO] += 1
                        else:  # PMXMXX
                            self.count[mine - 1][STWO] += 1
                    elif line[right_idx + 3] == mine:
                        if line[right_idx + 4] == empty and left_empty:  # XXXXMXMMX
                            self.count[mine - 1][THREE] += 1
                        elif line[right_idx + 4] == mine:  # MXMMM
                            self.count[mine - 1][SFOUR] += 1
                        elif line[right_idx + 4] == opponent and left_empty:  # XMXMMP
                            self.count[mine - 1][STHREE] += 1
                elif line[right_idx + 2] == empty:
                    if line[right_idx + 3] == mine:  # XXMXXMX
                        if line[right_idx + 4] == empty:
                            self.count[mine - 1][TWO] += 1
                        elif line[right_idx + 4] == mine:  # MXXMM
                            self.count[mine - 1][STHREE] += 1
                    if line[left_idx - 1] == empty:
                        if line[left_idx - 2] == mine and line[left_idx - 3] == opponent:
                            self.count[mine - 1][STWO] += 1  # PPMXMXX

        return None
