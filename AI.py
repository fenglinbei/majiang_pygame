from enum import IntEnum
import time
from GameMap import *

class CHESS_TYPE(IntEnum):
    NONE = 0,
    SLEEP_TWO = 1,
    LIVE_TWO = 2,
    SLEEP_THREE = 3
    LIVE_THREE = 4,
    CHONG_FOUR = 5,
    LIVE_FOUR = 6,
    LIVE_FIVE = 7,


CHESS_TYPE_NUM = 8

count_change_list = [1, 2, 2, 3, 3, 4, 4, 5]

FIVE = CHESS_TYPE.LIVE_FIVE.value
FOUR, THREE, TWO = CHESS_TYPE.LIVE_FOUR.value, CHESS_TYPE.LIVE_THREE.value, CHESS_TYPE.LIVE_TWO.value
SFOUR, STHREE, STWO = CHESS_TYPE.CHONG_FOUR.value, CHESS_TYPE.SLEEP_THREE.value, CHESS_TYPE.SLEEP_TWO.value

class ChessAI():
    def __init__(self, chess_len):
        self.len = chess_len
        # [horizon, vertical, left diagonal, right diagonal]
        self.count = [[0 for x in range(CHESS_TYPE_NUM)] for i in range(2)]
        self.pos_score = [[(7 - max(abs(x - 7), abs(y - 7))) for x in range(chess_len)] for y in range(chess_len)]

    def reset(self):

        for i in range(len(self.count)):
            for j in range(len(self.count[0])):
                self.count[i][j] = 0

        self.save_count = 0

    def isWin(self, board, turn):
        return self.evaluate(board, turn, True)

    def genmove(self, board, turn):
        moves = []
        for y in range(self.len):
            for x in range(self.len):
                if board[y][x] == 0:
                    score = self.pos_score[y][x]
                    moves.append((score, x, y))

        moves.sort(reverse=True)
        return moves

    def search(self, board, turn):
        moves = self.genmove(board, turn)
        bestmove = None
        max_score = -0x7fffffff
        for score, x, y in moves:
            board[y][x] = turn.value
            score = self.evaluate(board, turn)
            board[y][x] = 0

            if score > max_score:
                max_score = score
                bestmove = (max_score, x, y)
                self.best_count = self.count
        return bestmove

    def findBestChess(self, board, turn):
        time1 = time.time()
        score, x, y = self.search(board, turn)
        time2 = time.time()
        print('time[%.2f] (%d, %d), score[%d] bestcount%s' % (
            (time2 - time1), x, y, score, self.best_count))
        return (x, y)

    def getScore(self, mine_count, opponent_count):
        mscore, oscore = 0, 0

        SCORE_FIVE, SCORE_FOUR, SCORE_SFOUR = 10000, 10000, 5000
        SCORE_THREE, SCORE_STHREE, SCORE_TWO, SCORE_STWO = 5001, 5000, 2500, 500

        mscore += SCORE_FIVE * mine_count[FIVE]
        mscore += SCORE_FOUR * mine_count[FOUR]
        mscore += SCORE_SFOUR * mine_count[SFOUR]
        mscore += SCORE_THREE * mine_count[THREE]
        mscore += SCORE_STHREE * mine_count[STHREE]
        mscore += SCORE_TWO * mine_count[TWO]
        mscore += SCORE_STWO * mine_count[STWO]

        oscore += SCORE_FIVE * opponent_count[FIVE]
        oscore += SCORE_FOUR * opponent_count[FOUR]
        oscore += SCORE_SFOUR * opponent_count[SFOUR]
        oscore += SCORE_THREE * opponent_count[THREE]
        oscore += SCORE_STHREE * opponent_count[STHREE]
        oscore += SCORE_TWO * opponent_count[TWO]
        oscore += SCORE_STWO * opponent_count[STWO]


        return (mscore, oscore)

    def countChange(self, count):
        for i in [0, 1]:
            for num in range(CHESS_TYPE_NUM):
                count[i][num] /= count_change_list[num]
        return count

    def evaluate(self, board, turn, checkWin=False):
        self.reset()

        if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
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
        #self.count = self.countChange(self.count)

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
            self.save_count += 1

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

        empty = MAP_ENTRY_TYPE.MAP_EMPTY.value
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
            self.count[mine-1][FIVE] += 1

        # Live Four : XMMMMX
        # Chong Four : XMMMMP, PMMMMX
        if m_range == 4:
            left_empty = right_empty = False
            if line[left_idx - 1] == empty:
                left_empty = True
            if line[right_idx + 1] == empty:
                right_empty = True
            if left_empty and right_empty:
                self.count[mine-1][FOUR] += 1
            elif left_empty or right_empty:
                self.count[mine-1][SFOUR] += 1

        # Chong Four : MXMMM, MMMXM, the two types can both exist
        # Live Three : XMMMXX, XXMMMX
        # Sleep Three : PMMMX, XMMMP, PXMMMXP
        if m_range == 3:
            left_empty = right_empty = False
            left_four = right_four = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:  # MXMMM
                    self.count[mine-1][SFOUR] += 1
                    left_four = True
                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:  # MMMXM
                    self.count[mine-1][SFOUR] += 1
                    right_four = True
                right_empty = True

            if left_four or right_four:
                pass
            elif left_empty and right_empty:
                if chess_range > 5:  # XMMMXX, XXMMMX
                    self.count[mine-1][THREE] += 1
                else:  # PXMMMXP
                    self.count[mine-1][STHREE] += 1
            elif left_empty or right_empty:  # PMMMX, XMMMP
                self.count[mine-1][STHREE] += 1

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
                        if line[right_idx + 1] == empty:  # XMXMMX
                            self.count[mine-1][THREE] += 1
                        else:  # XMXMMP
                            self.count[mine-1][STHREE] += 1
                        left_three = True
                    elif line[left_idx - 3] == opponent:  # PMXMMX
                        if line[right_idx + 1] == empty:
                            self.count[mine-1][STHREE] += 1
                            left_three = True

                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:
                    if line[right_idx + 3] == mine:  # MMXMM
                        self.count[mine-1][SFOUR] += 1
                        right_three = True
                    elif line[right_idx + 3] == empty:
                        # setRecord(self, x, y, right_idx+1, right_idx+2, dir_index, dir)
                        if left_empty:  # XMMXMX
                            self.count[mine-1][THREE] += 1
                        else:  # PMMXMX
                            self.count[mine-1][STHREE] += 1
                        right_three = True
                    elif left_empty:  # XMMXMP
                        self.count[mine-1][STHREE] += 1
                        right_three = True

                right_empty = True

            if left_three or right_three:
                pass
            elif left_empty and right_empty:  # XMMX
                self.count[mine-1][TWO] += 1
            elif left_empty or right_empty:  # PMMX, XMMP
                self.count[mine-1][STWO] += 1

        # Live Two: XMXMX, XMXXMX only check right direction
        # Sleep Two: PMXMX, XMXMP
        if m_range == 1:
            left_empty = right_empty = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:
                    if line[left_idx - 3] == empty:
                        if line[right_idx + 1] == opponent:  # XMXMP
                            self.count[mine-1][STWO] += 1
                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:
                    if line[right_idx + 3] == empty:
                        if left_empty:  # XMXMX
                            # setRecord(self, x, y, left_idx, right_idx+2, dir_index, dir)
                            self.count[mine-1][TWO] += 1
                        else:  # PMXMX
                            self.count[mine-1][STWO] += 1
                elif line[right_idx + 2] == empty:
                    if line[right_idx + 3] == mine and line[right_idx + 4] == empty:  # XMXXMX
                        self.count[mine-1][TWO] += 1

        return None

if __name__ == '__main__':
    AI = ChessAI(14)
    board = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    count = AI.evaluate(board)
    print(count)
