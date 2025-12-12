# constants.py
BOARD_SIZE = 4
WINNING_LENGTH = 4

PLAYER_X = "X"
PLAYER_O = "O"
EMPTY = None

# إعدادات AI محسنة
AI_DEPTH = 5
MAX_SEARCH_TIME = 3
MAX_CACHE_SIZE = 100000

# قيم استرشادية محسنة
WIN_SCORE = 1000000
THREE_IN_LINE = 10000
TWO_IN_LINE = 200
BLOCK_OPPONENT_WIN = 50000
CENTER_BONUS = 100
MOBILITY_BONUS = 10
DOUBLE_THREAT_BONUS = 3000
CORNER_BONUS = 30

# جميع اتجاهات الفوز في 3D (76 اتجاه)
DIRECTIONS = []
for dx in (-1, 0, 1):
    for dy in (-1, 0, 1):
        for dz in (-1, 0, 1):
            if (dx, dy, dz) != (0, 0, 0):
                DIRECTIONS.append((dx, dy, dz))

# مراكز استراتيجية موسعة
CENTER_POSITIONS = [
    (1, 1, 1), (1, 1, 2), (1, 2, 1), (1, 2, 2),
    (2, 1, 1), (2, 1, 2), (2, 2, 1), (2, 2, 2)
]

# أوزان المواقع محسنة
POSITION_WEIGHTS = [
    [4, 3, 3, 4],
    [3, 2, 2, 3],
    [3, 2, 2, 3],
    [4, 3, 3, 4]
]

# زوايا مهمة
CORNER_POSITIONS = [
    (0, 0, 0), (0, 0, 3), (0, 3, 0), (0, 3, 3),
    (3, 0, 0), (3, 0, 3), (3, 3, 0), (3, 3, 3)
]