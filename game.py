# game.py
from constants import *
import threading
import pickle
import os

class CubicGame:
    def __init__(self):
        self.lock = threading.Lock()
        self.reset_game()
        self.move_history = []

    def reset_game(self):
        with self.lock:
            self.board = [[[EMPTY for _ in range(BOARD_SIZE)] 
                          for _ in range(BOARD_SIZE)] 
                          for _ in range(BOARD_SIZE)]
            self.current_player = PLAYER_X
            self.game_over = False
            self.winner = None
            self.winning_line = None
            self.move_count = 0
            self.move_history = []

    def make_move(self, x, y, z):
        """صنع حركة مع تتبع التاريخ"""
        with self.lock:
            if self.board[x][y][z] is not EMPTY or self.game_over:
                return False
                
            self.board[x][y][z] = self.current_player
            self.move_history.append((x, y, z, self.current_player))
            self.move_count += 1
            
            # فحص الفوز بكفاءة
            if self.check_win_optimized(x, y, z, self.current_player):
                self.game_over = True
                self.winner = self.current_player
                self.winning_line = self.get_winning_line_optimized(x, y, z, self.current_player)
            elif self.is_full():
                self.game_over = True
                self.winner = None
                
            return True

    def check_win_optimized(self, x, y, z, player):
        """فحص الفوز بشكل محسن حول النقطة الأخيرة"""
        for dx, dy, dz in DIRECTIONS:
            count = 1  # النقطة الحالية
            
            # التحقق في الاتجاه الإيجابي
            for i in range(1, WINNING_LENGTH):
                nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
                if not (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and 0 <= nz < BOARD_SIZE):
                    break
                if self.board[nx][ny][nz] != player:
                    break
                count += 1
                
            # التحقق في الاتجاه المعاكس
            for i in range(1, WINNING_LENGTH):
                nx, ny, nz = x - i*dx, y - i*dy, z - i*dz
                if not (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and 0 <= nz < BOARD_SIZE):
                    break
                if self.board[nx][ny][nz] != player:
                    break
                count += 1
                
            if count >= WINNING_LENGTH:
                return True
                
        return False

    def get_winning_line_optimized(self, x, y, z, player):
        """الحصول على خط الفوز بشكل محسن"""
        for dx, dy, dz in DIRECTIONS:
            line = [(x, y, z)]
            
            # في الاتجاه الإيجابي
            for i in range(1, WINNING_LENGTH):
                nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
                if not (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and 0 <= nz < BOARD_SIZE):
                    break
                if self.board[nx][ny][nz] != player:
                    break
                line.append((nx, ny, nz))
                
            # في الاتجاه المعاكس
            for i in range(1, WINNING_LENGTH):
                nx, ny, nz = x - i*dx, y - i*dy, z - i*dz
                if not (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and 0 <= nz < BOARD_SIZE):
                    break
                if self.board[nx][ny][nz] != player:
                    break
                line.insert(0, (nx, ny, nz))
                
            if len(line) >= WINNING_LENGTH:
                return line[:WINNING_LENGTH]
                
        return None

    def undo_move(self):
        """تراجع عن الحركة الأخيرة"""
        with self.lock:
            if not self.move_history:
                return False
                
            x, y, z, player = self.move_history.pop()
            self.board[x][y][z] = EMPTY
            self.move_count -= 1
            self.game_over = False
            self.winner = None
            self.winning_line = None
            self.current_player = player  # العودة للاعب السابق
            return True

    def switch_player(self):
        """تبديل اللاعب"""
        with self.lock:
            self.current_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X

    def is_full(self):
        """فحص إذا كانت اللوحة ممتلئة"""
        return self.move_count == BOARD_SIZE ** 3

    def get_possible_moves(self):
        """الحصول على جميع الحركات الممكنة مرتبة استراتيجياً"""
        moves = []
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                for z in range(BOARD_SIZE):
                    if self.board[x][y][z] is EMPTY:
                        # حساب الوزن الاستراتيجي
                        weight = (POSITION_WEIGHTS[x][y] + 
                                 POSITION_WEIGHTS[z][x] + 
                                 POSITION_WEIGHTS[y][z])
                        
                        # مكافأة المركز
                        if (x, y, z) in CENTER_POSITIONS:
                            weight += 2
                            
                        # مكافأة الزوايا
                        if (x, y, z) in CORNER_POSITIONS:
                            weight += 1
                            
                        moves.append((weight, (x, y, z)))
        
        # ترتيب حسب الوزن (الأعلى أولاً)
        moves.sort(reverse=True, key=lambda x: x[0])
        return [move for _, move in moves]

    def copy(self):
        """إنشاء نسخة من حالة اللعبة"""
        new_game = CubicGame()
        new_game.board = [[[self.board[x][y][z] for z in range(BOARD_SIZE)] 
                         for y in range(BOARD_SIZE)] 
                         for x in range(BOARD_SIZE)]
        new_game.current_player = self.current_player
        new_game.game_over = self.game_over
        new_game.winner = self.winner
        new_game.winning_line = self.winning_line.copy() if self.winning_line else None
        new_game.move_count = self.move_count
        new_game.move_history = self.move_history.copy()
        return new_game

    def save_game(self, filename):
        """حفظ اللعبة الحالية"""
        with open(filename, 'wb') as f:
            pickle.dump({
                'board': self.board,
                'current_player': self.current_player,
                'move_history': self.move_history
            }, f)

    def load_game(self, filename):
        """تحميل لعبة محفوظة"""
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                self.board = data['board']
                self.current_player = data['current_player']
                self.move_history = data['move_history']
                self.move_count = len(self.move_history)
                # إعادة حساب حالة اللعبة
                self.game_over = False
                self.winner = None
                self.winning_line = None

    def get_game_state(self):
        """الحصول على حالة اللعبة كسلسلة للتخزين المؤقت"""
        state_parts = []
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                for z in range(BOARD_SIZE):
                    cell = self.board[x][y][z]
                    if cell == PLAYER_X:
                        state_parts.append('X')
                    elif cell == PLAYER_O:
                        state_parts.append('O')
                    else:
                        state_parts.append('.')
        state_parts.append(self.current_player)
        return ''.join(state_parts)