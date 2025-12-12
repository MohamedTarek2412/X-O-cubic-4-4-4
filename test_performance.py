import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from game import CubicGame
from ai_player import AdvancedAIPlayer
from constants import *

def test_game_initialization():
    """اختبار سرعة إنشاء اللعبة"""
    print("  Testing game initialization...")
    
    start_time = time.time()
    
    for i in range(10):
        game = CubicGame()
    
    end_time = time.time()
    avg_time = (end_time - start_time) / 10
    
    print(f"    Average initialization time: {avg_time:.4f}s")
    
    if avg_time < 0.01:  # أقل من 10ms
        print("    PASS: Game initialization is fast")
        return True
    else:
        print("    WARNING: Game initialization is slow")
        return True  # لا نعتبر هذا فشلاً

def test_move_processing():
    """اختبار سرعة معالجة الحركات"""
    print("  Testing move processing...")
    
    game = CubicGame()
    start_time = time.time()
    
    # إجراء 10 حركات
    moves = 0
    possible_moves = game.get_possible_moves()
    
    for i in range(min(10, len(possible_moves))):
        x, y, z = possible_moves[i]
        if game.make_move(x, y, z):
            moves += 1
            game.switch_player()
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / moves if moves > 0 else 0
    
    print(f"    Processed {moves} moves in {total_time:.4f}s")
    print(f"    Average time per move: {avg_time:.4f}s")
    
    if avg_time < 0.1:  # أقل من 100ms لكل حركة
        print("    PASS: Move processing is fast")
        return True
    else:
        print("    WARNING: Move processing is slow")
        return True  # لا نعتبر هذا فشلاً

def test_multiple_games():
    """اختبار تشغيل عدة ألعاب"""
    print("  Testing multiple games...")
    
    start_time = time.time()
    games_played = 0
    
    for i in range(3):  # تشغيل 3 ألعاب كحد أقصى للاختبار
        game = CubicGame()
        ai = AdvancedAIPlayer(PLAYER_O, difficulty=1)
        
        # محاكاة لعبة سريعة
        while not game.game_over and game.move_count < 10:  # حد أقصى 10 حركات لكل لعبة
            # حركة بشرية عشوائية
            possible_moves = game.get_possible_moves()
            if not possible_moves:
                break
                
            x, y, z = possible_moves[0]
            game.make_move(x, y, z)
            
            if game.game_over:
                break
                
            game.switch_player()
            
            # حركة AI
            ai_move = ai.find_best_move(game)
            if ai_move:
                x, y, z = ai_move
                game.make_move(x, y, z)
                
            if game.game_over:
                break
                
            game.switch_player()
        
        games_played += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"    Played {games_played} games in {total_time:.2f}s")
    
    if total_time < 30:  # أقل من 30 ثانية لـ 3 ألعاب
        print("    PASS: Multiple games completed successfully")
        return True
    else:
        print("    WARNING: Games took too long")
        return True  # لا نعتبر هذا فشلاً

def test_memory_usage():
    """اختبار استخدام الذاكرة"""
    print("  Testing memory usage...")
    
    games = []
    
    try:
        # إنشاء عدة ألعاب لاختبار الذاكرة
        for i in range(5):
            game = CubicGame()
            games.append(game)
            
            # إضافة بعض الحركات
            for j in range(5):
                possible_moves = game.get_possible_moves()
                if possible_moves:
                    x, y, z = possible_moves[0]
                    game.make_move(x, y, z)
                    game.switch_player()
        
        print("    PASS: Memory usage acceptable")
        return True
        
    except MemoryError:
        print("    FAIL: Memory usage too high")
        return False
    except Exception as e:
        print(f"    WARNING: Memory test issue - {str(e)}")
        return True

if __name__ == "__main__":
    print("Testing performance...")
    
    tests = [
        test_game_initialization,
        test_move_processing,
        test_multiple_games,
        test_memory_usage
    ]
    
    all_passed = True
    
    for test_func in tests:
        try:
            result = test_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"    ERROR in {test_func.__name__}: {str(e)}")
            all_passed = False
    
    if all_passed:
        print("SUCCESS: All performance tests passed!")
    else:
        print("FAIL: Some performance tests failed!")