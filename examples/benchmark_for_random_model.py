import pandas as pd
from dotenv import load_dotenv
import os
from tqdm import tqdm

from core.game_manager import play_move_in_position
from players.random_move_player import RandomMovePlayer
from core.evaluate import evaluate_moves

fen_data = pd.read_csv("data/fen_analysis.csv")

load_dotenv()
stockfish_path = os.getenv("STOCKFISH_PATH")

model = RandomMovePlayer(name="RandomBot")

    
def main():
    moves = []
    fens = []
    
    for index, row in tqdm(fen_data.iterrows(), total=len(fen_data)):
        if index >= 100: 
            break
        fen = row["FEN"]
        fens.append(fen)
        move = play_move_in_position(model, fen)
        moves.append(move)
    
    scores, gains = evaluate_moves(fens, moves, stockfish_path)
    
    results = pd.DataFrame({
        "FEN": fens,
        "Move": moves,
        "Score After Move": scores,
        "Gain": gains
    })
    
    os.makedirs("results", exist_ok=True)
    results.to_csv("results/random_model_results.csv", index=False)
    missing_count = results["Gain"].isna().sum()
    print("Mean score gain for random model:", -results["Loss"].mean())
    print("Illegal moves:", missing_count)

if __name__ == "__main__":
    main()