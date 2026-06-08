import os
from tqdm import tqdm
import pandas as pd
from dotenv import load_dotenv

from core.game_manager import play_move_in_position
from core.evaluate import evaluate_moves

load_dotenv()
stockfish_path = os.getenv("STOCKFISH_PATH")

def benchmark(model,fen_data, results_path="results/benchmark_results.csv", limit=1000):
    moves = []
    fens = []
        
    try:
        for index, row in tqdm(fen_data.iterrows(), total=len(fen_data), unit="moves"):
            if index >= limit: 
                break
            fen = row["FEN"]
            fens.append(fen)
            move_uci = play_move_in_position(model, fen)
            moves.append(move_uci)
    except KeyboardInterrupt:
        print("Benchmarking interrupted by user.")
    finally:
        results = evaluate_moves(fens[:len(moves)], moves, stockfish_path)
        
        results = pd.DataFrame({
            "FEN": fens[:len(moves)],
            "Move": moves,
            "Score After Move": results["after_scores"],
            "Gain": results["gains"],
            "Material Balance": results["material_balances"],
            "Player Mobility diff": results["player_mobility_differences"],
            "Opponent Mobility diff": results["opponent_mobility_differences"],
            "Doubled Pawns": results["doubled_pawnses"]
        })
        
        os.makedirs("results", exist_ok=True)
        results.to_csv(results_path, index=False)
        missing_count = results["Gain"].isna().sum()
        print("Mean score gain for", model.name, ":", results["Gain"].mean())
        print("Illegal moves:", missing_count)
