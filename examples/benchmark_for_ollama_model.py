import pandas as pd
from dotenv import load_dotenv
import os
from tqdm import tqdm

from core.game_manager import play_move_in_position
from players import OllamaPlayer
from core.evaluate import evaluate_moves

PHI = "phi3:3.8b"


load_dotenv()
stockfish_path = os.getenv("STOCKFISH_PATH")

fen_data = pd.read_csv("data/fen_analysis.csv")

model = OllamaPlayer(name="PHI", model_name=PHI, verbose=True)
 
def main():
    moves = []
    fens = []
    
    for index, row in tqdm(fen_data.iterrows(), total=len(fen_data), unit="moves"):
        if index >= 4000: 
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
    results.to_csv("results/phi_model_results.csv", index=False)
    missing_count = results["Gain"].isna().sum()
    print("Mean score gain for", model.name,  ":", results["Gain"].mean())
    print("Illegal moves:", missing_count)

if __name__ == "__main__":
    main()