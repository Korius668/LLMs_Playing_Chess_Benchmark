import pandas as pd
import chess
import chess.engine
from dotenv import load_dotenv
import os
from core.game_manager import play_move_in_position
from players.random_move_player import RandomMovePlayer
from tqdm import tqdm
fen_data = pd.read_csv("data/fen_analysis.csv")

load_dotenv()
stockfish_path = os.getenv("STOCKFISH_PATH")

model = RandomMovePlayer(name="RandomBot")

def evaluate_move(fen, move_uci, stockfish_path):
    board = chess.Board(fen)

    with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
        # 1. Ocena przed ruchem (znalezienie najlepszego ruchu)
        info_best = engine.analyse(board, chess.engine.Limit(time=0.1))
        best_score = info_best["score"].white().score(mate_score=10000)

        move = chess.Move.from_uci(move_uci)
        if move not in board.legal_moves:
            return "Illegal Move", None
            
        board.push(move)
        
        info_after = engine.analyse(board, chess.engine.Limit(time=0.1))
        after_score = info_after["score"].white().score(mate_score=10000)

        loss = best_score - after_score
        return after_score, loss
    
def main():
    results = pd.DataFrame(columns=["FEN", "Move", "Score After Move", "Loss"])
    for index, row in tqdm(fen_data.iterrows(), total=len(fen_data)):
        if index >= 100: 
            break
        fen = row["FEN"]
        
        move = play_move_in_position(model, fen)
        score, loss = evaluate_move(fen, move, stockfish_path)
        results = pd.concat([results, pd.DataFrame([{
            "FEN": fen,
            "Move": move,
            "Score After Move": score,
            "Loss": loss
        }])], ignore_index=True)

    results.to_csv("results/random_model_results.csv", index=False)
    print("Mean score gain for random model:", -results["Loss"].mean())
    
if __name__ == "__main__":
    main()