import sys
import os

# Add src folder to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from game import CubicGame

def test_basic_game():
    print("Testing basic game functionality...")
    game = CubicGame()
    
    # 1. Check empty board
    assert len(game.board) == 4, "Board should be 4x4x4"
    assert len(game.board[0]) == 4, "Board should be 4x4x4"
    assert len(game.board[0][0]) == 4, "Board should be 4x4x4"
    print("  PASS: Board is 4x4x4")
    
    # 2. Test simple moves
    assert game.make_move(0, 0, 0) == True, "Valid move should return True"
    assert game.board[0][0][0] == "X", "Cell should change to X"
    print("  PASS: Valid move works")
    
    # 3. Move to occupied cell
    assert game.make_move(0, 0, 0) == False, "Move to occupied cell should return False"
    print("  PASS: Occupied cell move blocked")
    
    # 4. Switch player
    game.switch_player()
    assert game.current_player == "O", "Player switch didn't work correctly"
    print("  PASS: Player switch works")
    
    print("SUCCESS: All basic tests passed!")

if __name__ == "__main__":
    test_basic_game()