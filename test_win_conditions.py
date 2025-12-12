import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import CubicGame
from constants import *

def run_test(test_name, positions):
    """تشغيل اختبار فردي"""
    print(f"  Testing {test_name}...")
    
    game = CubicGame()
    
    for i, (x, y, z) in enumerate(positions):
        # تأكد أن اللاعب الصحيح يلعب
        if game.current_player != PLAYER_X:
            game.switch_player()
            
        success = game.make_move(x, y, z)
        if not success:
            print(f"    FAIL: Move failed at position ({x}, {y}, {z})")
            return False
            
        # تبديل اللاعب بعد كل حركة ما عدا الأخيرة
        if i < len(positions) - 1:
            game.switch_player()
    
    # التحقق من النتيجة
    if game.game_over and game.winner == PLAYER_X:
        print(f"    PASS: {test_name} detected")
        return True
    else:
        print(f"    FAIL: {test_name} not detected")
        return False

def main():
    """الاختبار الرئيسي"""
    print("Testing all win conditions...")
    
    # تعريف جميع أنواع الفوز
    win_tests = [
        ("horizontal win", [(0,0,0), (0,1,0), (0,2,0), (0,3,0)]),
        ("vertical win", [(0,0,0), (1,0,0), (2,0,0), (3,0,0)]),
        ("depth win", [(0,0,0), (0,0,1), (0,0,2), (0,0,3)]),
        ("diagonal win", [(0,0,0), (1,1,1), (2,2,2), (3,3,3)])
    ]
    
    passed = 0
    failed = 0
    
    for test_name, positions in win_tests:
        if run_test(test_name, positions):
            passed += 1
        else:
            failed += 1
    
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    if main():
        print("SUCCESS: All win condition tests passed!")
        exit(0)
    else:
        print("FAIL: Some win condition tests failed!")
        exit(1)