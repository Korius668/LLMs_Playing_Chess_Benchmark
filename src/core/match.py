import os
import time
import random
import chess
import chess.engine
import pandas as pd
from datetime import datetime
from pathlib import Path

from core.game_manager import GameManager
from core.evaluate import centipawn_score


class MatchResult:
    def __init__(self, white_player, black_player, match_id):
        self.white_player = white_player
        self.black_player = black_player
        self.match_id = match_id
        self.moves_data = []
        self.winner = None
        self.result = None
        self.termination_reason = None
        
    def add_move(self, move_number, move_uci, player_name, time_taken_ms, centipawn_score_value):
        self.moves_data.append({
            'move_number': move_number,
            'move_uci': move_uci,
            'player_name': player_name,
            'time_taken_ms': time_taken_ms,
            'centipawn_score': centipawn_score_value
        })
    
    def to_csv(self, filepath):
        df = pd.DataFrame(self.moves_data)
        df.to_csv(filepath, index=False)
        

def play_match(white_player, black_player, match_id, stockfish_path=None, max_moves=200, results_dir="results/tournament", verbose=False):
    """
    Play a chess match between two players.
    
    Args:
        white_player: Player object for white pieces
        black_player: Player object for black pieces
        match_id: Unique identifier for the match
        stockfish_path: Path to stockfish executable
        max_moves: Maximum moves before draw
        results_dir: Directory to save match results
        verbose: Print move-by-move information during the game
        
    Returns:
        MatchResult object with all game data
    """
    os.makedirs(results_dir, exist_ok=True)
    
    manager = GameManager(white_player, black_player)
    match_result = MatchResult(white_player, black_player, match_id)
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"Match: {white_player.name} (White) vs {black_player.name} (Black)")
        print(f"{'='*70}\n")
    
    engine = None
    if stockfish_path and os.path.exists(stockfish_path):
        try:
            engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        except Exception as e:
            if verbose:
                print(f"Warning: Could not initialize stockfish engine: {e}")
            engine = None
    
    move_number = 1
    move_count = 0
    
    try:
        while not manager.board.is_game_over() and move_count < max_moves:
            current_player = manager.white if manager.board.turn == chess.WHITE else manager.black
            
            # Measure move time
            move_start = time.perf_counter()
            move = current_player.get_move(manager.board)
            move_end = time.perf_counter()
            time_taken_ms = (move_end - move_start) * 1000
            
            # Validate and play move
            if move and move in manager.board.legal_moves:
                # Evaluate position if engine available
                cp_score = None
                if engine:
                    try:
                        board_before = manager.board.copy()
                        manager.board.push(move)
                        board_after = manager.board.copy()
                        
                        cp_score = centipawn_score(engine, board_after)
                    except Exception as e:
                        if verbose:
                            print(f"Warning: Could not evaluate move: {e}")
                        manager.board.push(move)
                else:
                    manager.board.push(move)
                
                match_result.add_move(
                    move_number=move_number,
                    move_uci=move.uci(),
                    player_name=current_player.name,
                    time_taken_ms=time_taken_ms,
                    centipawn_score_value=cp_score
                )
                
                if verbose:
                    move_display = move.uci()
                    try:
                        move_display = manager.board.san(move)
                    except:
                        pass
                    
                    score_str = ""
                    if cp_score is not None:
                        score_val = cp_score / 100.0
                        perspective = "White" if manager.board.turn == chess.BLACK else "Black"
                        score_str = f" | {perspective}: {score_val:+.1f}"
                    
                    time_str = f"{time_taken_ms:.0f}ms"
                    print(f"Move {move_number}. {current_player.name:12} plays {move_display:8} ({time_str}){score_str}")
                
                move_count += 1
                if manager.board.turn == chess.BLACK:
                    move_number += 1
            else:
                # Invalid move - opponent wins
                match_result.winner = manager.black.name if manager.board.turn == chess.WHITE else manager.white.name
                match_result.result = "win"
                match_result.termination_reason = f"Invalid move from {current_player.name}"
                if verbose:
                    print(f"\n❌ Invalid move from {current_player.name}! {match_result.winner} wins!")
                break
        
        # Determine game outcome if not already set
        if match_result.winner is None:
            if manager.board.is_game_over():
                result = manager.board.result()
                if result == "1-0":
                    match_result.winner = white_player.name
                    match_result.result = "win"
                    match_result.termination_reason = "Checkmate or resignation"
                    if verbose:
                        print(f"\n🏆 {white_player.name} (White) wins by checkmate!")
                elif result == "0-1":
                    match_result.winner = black_player.name
                    match_result.result = "win"
                    match_result.termination_reason = "Checkmate or resignation"
                    if verbose:
                        print(f"\n🏆 {black_player.name} (Black) wins by checkmate!")
                else:  # "1/2-1/2"
                    match_result.winner = None
                    match_result.result = "draw"
                    match_result.termination_reason = "Stalemate or draw agreement"
                    if verbose:
                        print(f"\n🤝 Game drawn (stalemate)")
            elif move_count >= max_moves:
                match_result.winner = None
                match_result.result = "draw"
                match_result.termination_reason = "Move limit reached"
                if verbose:
                    print(f"\n🤝 Game drawn (move limit reached: {move_count} moves)")
        
    finally:
        if engine:
            engine.quit()
    
    # Save results
    csv_filepath = os.path.join(results_dir, f"match_{match_id}.csv")
    match_result.to_csv(csv_filepath)
    
    return match_result


def play_match_with_random_colors(player1, player2, match_id, stockfish_path=None, max_moves=200, results_dir="results/tournament", verbose=False):
    """
    Play a match between two players with randomly assigned colors.
    
    Args:
        player1: First player
        player2: Second player
        match_id: Unique identifier for the match
        stockfish_path: Path to stockfish executable
        max_moves: Maximum moves before draw
        results_dir: Directory to save match results
        verbose: Print move-by-move information during the game
        
    Returns:
        MatchResult object
    """
    if random.random() < 0.5:
        white = player1
        black = player2
        color_assignment = f"{player1.name} (W) vs {player2.name} (B)"
    else:
        white = player2
        black = player1
        color_assignment = f"{player2.name} (W) vs {player1.name} (B)"
    
    if not verbose:
        print(f"Match {match_id}: {color_assignment}")
    
    return play_match(white, black, match_id, stockfish_path, max_moves, results_dir, verbose)
