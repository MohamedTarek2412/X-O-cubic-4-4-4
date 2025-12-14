import time
from game import CubicGame
from ai_player import AdvancedAIPlayer
from constants import PLAYER_X, PLAYER_O


def run_single_game(difficulty_x=3, difficulty_o=3, heuristic=2):
    

    game = CubicGame()

    ai_x = AdvancedAIPlayer(
        PLAYER_X,
        difficulty=difficulty_x,
        heuristic_type=heuristic
    )
    ai_o = AdvancedAIPlayer(
        PLAYER_O,
        difficulty=difficulty_o,
        heuristic_type=heuristic
    )

    total_nodes_x = 0
    total_nodes_o = 0
    total_time_x = 0.0
    total_time_o = 0.0

    while not game.game_over:
        if game.current_player == PLAYER_X:
            move = ai_x.find_best_move(game)
            metrics = ai_x.get_metrics()
            total_nodes_x += metrics["nodes"]
            total_time_x += metrics["time"]
        else:
            move = ai_o.find_best_move(game)
            metrics = ai_o.get_metrics()
            total_nodes_o += metrics["nodes"]
            total_time_o += metrics["time"]

        if move:
            game.make_move(*move)
            game.switch_player()
        else:
            break

    return {
        "winner": game.winner,
        "moves": game.move_count,
        "x_nodes": total_nodes_x,
        "o_nodes": total_nodes_o,
        "x_time": round(total_time_x, 3),
        "o_time": round(total_time_o, 3),
    }


def run_experiment(
    games=30,
    difficulty_x=3,
    difficulty_o=3,
    heuristic=2
):
    

    results = {
        "X_wins": 0,
        "O_wins": 0,
        "draws": 0,
        "avg_moves": 0,
        "avg_nodes_x": 0,
        "avg_nodes_o": 0,
        "avg_time_x": 0,
        "avg_time_o": 0,
    }

    total_moves = 0
    total_nodes_x = 0
    total_nodes_o = 0
    total_time_x = 0
    total_time_o = 0

    for i in range(games):
        print(f"Running game {i + 1}/{games}")
        result = run_single_game(
            difficulty_x,
            difficulty_o,
            heuristic
        )

        if result["winner"] == PLAYER_X:
            results["X_wins"] += 1
        elif result["winner"] == PLAYER_O:
            results["O_wins"] += 1
        else:
            results["draws"] += 1

        total_moves += result["moves"]
        total_nodes_x += result["x_nodes"]
        total_nodes_o += result["o_nodes"]
        total_time_x += result["x_time"]
        total_time_o += result["o_time"]

    results["avg_moves"] = round(total_moves / games, 2)
    results["avg_nodes_x"] = int(total_nodes_x / games)
    results["avg_nodes_o"] = int(total_nodes_o / games)
    results["avg_time_x"] = round(total_time_x / games, 3)
    results["avg_time_o"] = round(total_time_o / games, 3)

    return results


if __name__ == "__main__":
    results = run_experiment(
        games=20,
        difficulty_x=3,
        difficulty_o=3,
        heuristic=2
    )

    print("\n===== EXPERIMENT RESULTS =====")
    for key, value in results.items():
        print(f"{key}: {value}")
