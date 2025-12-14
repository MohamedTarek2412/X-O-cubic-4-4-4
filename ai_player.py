import math
import time
import random
import threading
from collections import OrderedDict
from typing import Self
from constants import *

class AdvancedAIPlayer:
    def __init__(self, player_symbol, difficulty=3, heuristic_type=2):
        self.player_symbol = player_symbol 
        self.heuristic_type = heuristic_type
        self.opponent_symbol = PLAYER_O if player_symbol == PLAYER_X else PLAYER_X
        self.difficulty = difficulty  
        self.set_difficulty(difficulty)
          

        self.nodes_evaluated = 0
        self.last_search_time = 0.0

        self.transposition_table = OrderedDict()
        self.search_cancelled = False
        self.lock = threading.Lock()
        self.killer_moves = {}

    def reset_metrics(self):
        self.nodes_evaluated = 0
        self.last_search_time = 0.0

    def get_metrics(self):
        return {
            "nodes": self.nodes_evaluated,
            "time": round(self.last_search_time, 4),
            "depth": self.depth,
            "difficulty": self.difficulty,
            "heuristic": self.heuristic_type
        }
    
    
    def set_difficulty(self, level):
        difficulties = {
            1: {'depth': 2, 'max_time': 1},
            2: {'depth': 3, 'max_time': 2},
            3: {'depth': 4, 'max_time': 3},
            4: {'depth': 5, 'max_time': 5},
            5: {'depth': 6, 'max_time': 8}
        }
        config = difficulties.get(level, difficulties[3])
        self.depth = config['depth']
        self.max_time = config['max_time']

    def find_best_move(self, game):
        self.nodes_evaluated = 0
        self.search_cancelled = False
        self.reset_metrics()
        start_time = time.time()
        
        immediate_win = self.find_immediate_win(game, self.player_symbol)
        if immediate_win:
            return immediate_win
            
        immediate_block = self.find_immediate_win(game, self.opponent_symbol)
        if immediate_block:
            return immediate_block
        
        double_threat = self.find_double_threat_move(game)
        if double_threat:
            return double_threat
        
        best_move = self.iterative_deepening_search(game, start_time)
        
        search_time = time.time() - start_time
        print(f"AI: Found move in {search_time:.2f}s, evaluated {self.nodes_evaluated} nodes, difficulty: {self.difficulty}")
        
        self.last_search_time = time.time() - start_time

        return best_move if best_move else self.get_fallback_move(game)


    def iterative_deepening_search(self, game, start_time):
        best_move = None
        best_value = -math.inf
        
        if game.move_count == 0:
            return random.choice(CENTER_POSITIONS)
        elif game.move_count == 1:
            return self.get_second_move_response(game)
        
        for current_depth in range(1, self.depth + 1):
            if self.check_timeout(start_time):
                break
                
            try:
                move, value = self.alpha_beta_search(game, current_depth, start_time)
                if move and value > best_value:
                    best_value = value
                    best_move = move
                    if value > WIN_SCORE - 1000:
                        break
            except TimeoutError:
                break
                
        return best_move

    def alpha_beta_search(self, game, depth, start_time):
        best_value = -math.inf
        best_move = None
        alpha = -math.inf
        beta = math.inf
        
        moves = self.get_ordered_moves(game)
        
        for move in moves:
            if self.check_timeout(start_time):
                raise TimeoutError()
                
            new_game = game.copy()
            new_game.make_move(move[0], move[1], move[2])
            new_game.switch_player()
            
            move_value = self.alpha_beta_minimax(new_game, depth - 1, alpha, beta, False, start_time)
            
            if move_value > best_value:
                best_value = move_value
                best_move = move
                
            alpha = max(alpha, best_value)
            if beta <= alpha:
                self.store_killer_move(depth, move)  
                break
                
        return best_move, best_value

    def get_ordered_moves(self, game):
        moves = game.get_possible_moves()
        if not moves:
            return moves
            
        killer_moves = self.killer_moves.get(game.move_count, [])
        ordered_moves = []
        
        for move in killer_moves:
            if move in moves:
                ordered_moves.append(move)
                moves.remove(move)
        
        ordered_moves.extend(moves)
        return ordered_moves

    def store_killer_move(self, depth, move):
        if depth not in self.killer_moves:
            self.killer_moves[depth] = []
        
        if move not in self.killer_moves[depth]:
            self.killer_moves[depth].insert(0, move)
            self.killer_moves[depth] = self.killer_moves[depth][:3]

    def alpha_beta_minimax(self, game, depth, alpha, beta, maximizing_player, start_time):
        self.nodes_evaluated += 1
        
        if self.check_timeout(start_time):
            return 0
            
        if game.game_over:
            if game.winner == self.player_symbol:
                return WIN_SCORE + depth * 1000  
            elif game.winner == self.opponent_symbol:
                return -WIN_SCORE - depth * 1000  
            else:
                return 0
                
        if depth == 0:
            return self.evaluate(game)

            
        state_key = game.get_game_state() + str(depth) + str(maximizing_player)
        if state_key in self.transposition_table:
            return self.transposition_table[state_key]
            
        moves = self.get_ordered_moves(game)
        
        if maximizing_player:
            max_eval = -math.inf
            for move in moves:
                if self.check_timeout(start_time):
                    break
                    
                new_game = game.copy()
                new_game.make_move(move[0], move[1], move[2])
                new_game.switch_player()
                
                eval = self.alpha_beta_minimax(new_game, depth - 1, alpha, beta, False, start_time)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                
                if beta <= alpha:
                    self.store_killer_move(depth, move)
                    break
                    
            self.store_transposition(state_key, max_eval)
            return max_eval
        else:
            min_eval = math.inf
            for move in moves:
                if self.check_timeout(start_time):
                    break
                    
                new_game = game.copy()
                new_game.make_move(move[0], move[1], move[2])
                new_game.switch_player()
                
                eval = self.alpha_beta_minimax(new_game, depth - 1, alpha, beta, True, start_time)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                
                if beta <= alpha:
                    self.store_killer_move(depth, move)
                    break
                    
            self.store_transposition(state_key, min_eval)
            return min_eval
        

    def evaluate(self, game):
        if self.heuristic_type == 1:
            return self.quick_evaluate(game)
        return self.comprehensive_evaluate(game)

    def comprehensive_evaluate(self, game):
        if game.game_over:
            if game.winner == self.player_symbol:
                return WIN_SCORE
            elif game.winner == self.opponent_symbol:
                return -WIN_SCORE
            return 0
            
        score = 0
        
        player_score = self.evaluate_player_position(game, self.player_symbol)
        opponent_score = self.evaluate_player_position(game, self.opponent_symbol)
        
        score += player_score
        score -= opponent_score * 1.1  
        
        score += self.evaluate_center_control(game, self.player_symbol) * CENTER_BONUS
        score -= self.evaluate_center_control(game, self.opponent_symbol) * CENTER_BONUS
        
        score += self.evaluate_corners(game, self.player_symbol) * CORNER_BONUS
        score -= self.evaluate_corners(game, self.opponent_symbol) * CORNER_BONUS
        
        score += self.evaluate_double_threats(game, self.player_symbol) * DOUBLE_THREAT_BONUS
        score -= self.evaluate_double_threats(game, self.opponent_symbol) * DOUBLE_THREAT_BONUS
        
        mobility = len(game.get_possible_moves())
        if game.current_player == self.player_symbol:
            score += mobility * MOBILITY_BONUS
        else:
            score -= mobility * MOBILITY_BONUS
            
        return int(score)

    def evaluate_player_position(self, game, player):
        score = 0
        opponent = self.opponent_symbol if player == self.player_symbol else self.player_symbol
        
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                for z in range(BOARD_SIZE):
                    if game.board[x][y][z] == player:
                        for dx, dy, dz in DIRECTIONS:
                            line_score = self.evaluate_line_from_point(game, x, y, z, dx, dy, dz, player, opponent)
                            score += line_score
                            
        return score

    def evaluate_line_from_point(self, game, x, y, z, dx, dy, dz, player, opponent):
        player_count = 0
        empty_count = 0
        blocked = False
        
        for i in range(WINNING_LENGTH):
            nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
            if not (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and 0 <= nz < BOARD_SIZE):
                blocked = True
                break
                
            cell = game.board[nx][ny][nz]
            if cell == player:
                player_count += 1
            elif cell == opponent:
                blocked = True
                break
            else:
                empty_count += 1
        
        if blocked:
            return 0
            
        if player_count == 4:
            return WIN_SCORE
        elif player_count == 3 and empty_count == 1:
            return THREE_IN_LINE
        elif player_count == 2 and empty_count == 2:
            return TWO_IN_LINE
        elif player_count == 1 and empty_count == 3:
            return TWO_IN_LINE // 2
            
        return 0

    def evaluate_center_control(self, game, player):
        control = 0
        for pos in CENTER_POSITIONS:
            x, y, z = pos
            if game.board[x][y][z] == player:
                control += 1
        return control

    def evaluate_corners(self, game, player):
        control = 0
        for pos in CORNER_POSITIONS:
            x, y, z = pos
            if game.board[x][y][z] == player:
                control += 1
        return control

    def evaluate_double_threats(self, game, player):
        threats = 0
        possible_moves = game.get_possible_moves()
        
        for move in possible_moves:
            x, y, z = move
            game.board[x][y][z] = player
            win_count = self.count_winning_lines(game, player, x, y, z)
            game.board[x][y][z] = EMPTY
            
            if win_count >= 2:
                threats += 1
                
        return threats

    def count_winning_lines(self, game, player, x, y, z):
        count = 0
        for dx, dy, dz in DIRECTIONS:
            if self.check_line_for_win(game, x, y, z, dx, dy, dz, player):
                count += 1
        return count

    def check_line_for_win(self, game, x, y, z, dx, dy, dz, player):
        total_count = 1 
        
        for i in range(1, WINNING_LENGTH):
            nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
            if not (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and 0 <= nz < BOARD_SIZE):
                break
            if game.board[nx][ny][nz] != player:
                break
            total_count += 1
            
        for i in range(1, WINNING_LENGTH):
            nx, ny, nz = x - i*dx, y - i*dy, z - i*dz
            if not (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and 0 <= nz < BOARD_SIZE):
                break
            if game.board[nx][ny][nz] != player:
                break
            total_count += 1
            
        return total_count >= WINNING_LENGTH

    def find_immediate_win(self, game, player):
        for move in game.get_possible_moves():
            x, y, z = move
            game.board[x][y][z] = player
            if game.check_win_optimized(x, y, z, player):
                game.board[x][y][z] = EMPTY
                return move
            game.board[x][y][z] = EMPTY
        return None

    def find_double_threat_move(self, game):
        for move in game.get_possible_moves():
            x, y, z = move
            game.board[x][y][z] = self.player_symbol
            threat_count = self.count_winning_lines(game, self.player_symbol, x, y, z)
            game.board[x][y][z] = EMPTY
            
            if threat_count >= 2:
                return move
        return None

    def get_second_move_response(self, game):
        for x, y, z in CENTER_POSITIONS:
            if game.board[x][y][z] == self.opponent_symbol:
                return random.choice(CORNER_POSITIONS)
        
        return random.choice(CENTER_POSITIONS)

    def get_fallback_move(self, game):
        moves = game.get_possible_moves()
        if not moves:
            return None
            
        best_score = -math.inf
        best_move = moves[0]
        
        for move in moves[:8]: 
            x, y, z = move
            game.board[x][y][z] = self.player_symbol
            score = self.quick_evaluate(game)
            game.board[x][y][z] = EMPTY
            
            if score > best_score:
                best_score = score
                best_move = move
                
        return best_move

    def quick_evaluate(self, game):
        score = 0
        for pos in CENTER_POSITIONS:
            x, y, z = pos
            if game.board[x][y][z] == self.player_symbol:
                score += 20
            elif game.board[x][y][z] == self.opponent_symbol:
                score -= 25
                
        for pos in CORNER_POSITIONS:
            x, y, z = pos
            if game.board[x][y][z] == self.player_symbol:
                score += 10
            elif game.board[x][y][z] == self.opponent_symbol:
                score -= 12
                
        return score

    def check_timeout(self, start_time):
        if time.time() - start_time > self.max_time:
            self.search_cancelled = True
            return True
        return False

    def store_transposition(self, key, value):
        with self.lock:
            if len(self.transposition_table) >= MAX_CACHE_SIZE:
                self.transposition_table.popitem(last=False)
            self.transposition_table[key] = value




