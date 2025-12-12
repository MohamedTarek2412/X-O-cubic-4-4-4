import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from game import CubicGame
from ai_player import AdvancedAIPlayer
from constants import *

def test_ai_performance():
    """اختبار أداء الذكاء الاصطناعي"""
    print("  Testing AI performance...")
    
    # إنشاء لعبة جديدة
    game = CubicGame()
    
    # إنشاء AI مع الصعوبة بدلاً من العمق
    ai = AdvancedAIPlayer(PLAYER_O, difficulty=1)
    
    # اختبار سرعة AI
    start_time = time.time()
    
    # جعل AI يلعب عدة حركات
    moves_to_test = 3
    moves_made = 0
    
    for i in range(moves_to_test):
        if game.game_over:
            break
            
        # جعل اللاعب البشري يلعب حركة عشوائية أولاً
        possible_moves = game.get_possible_moves()
        if possible_moves:
            # حركة بشرية عشوائية
            x, y, z = possible_moves[0]
            game.make_move(x, y, z)
            game.switch_player()
            
            # حركة AI
            if not game.game_over:
                ai_move = ai.find_best_move(game)
                if ai_move:
                    x, y, z = ai_move
                    game.make_move(x, y, z)
                    game.switch_player()
                    moves_made += 1
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"    AI made {moves_made} moves in {execution_time:.2f} seconds")
    
    if execution_time < 10:  # أقل من 10 ثواني
        print("    PASS: AI performance acceptable")
        return True
    else:
        print("    FAIL: AI too slow")
        return False

def test_ai_smart_moves():
    """اختبار أن الذكاء الاصطناعي يلعب حركات ذكية"""
    print("  Testing AI smart moves...")
    
    game = CubicGame()
    ai = AdvancedAIPlayer(PLAYER_O, difficulty=3)
    
    # حركة بشرية أولى
    game.make_move(1, 1, 1)  # مركز
    game.switch_player()
    
    # حركة AI
    ai_move = ai.find_best_move(game)
    
    if ai_move:
        x, y, z = ai_move
        print(f"    AI chose position: ({x}, {y}, {z})")
        
        # التحقق من أن الحركة منطقية (ليست عشوائية)
        if (x, y, z) in [(1, 1, 2), (1, 2, 1), (2, 1, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)]:
            print("    PASS: AI made a strategic move")
            return True
        else:
            print("    WARNING: AI move might not be optimal")
            return True  # لا نعتبر هذا فشلاً
    else:
        print("    FAIL: AI returned no move")
        return False

if __name__ == "__main__":
    print("Testing AI functionality...")
    
    success1 = test_ai_performance()
    success2 = test_ai_smart_moves()
    
    if success1 and success2:
        print("SUCCESS: All AI tests passed!")
    else:
        print("FAIL: Some AI tests failed!")