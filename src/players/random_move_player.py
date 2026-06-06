import random
import chess

from core.player_base import BasePlayer

class RandomMovePlayer(BasePlayer):
    """Model 'Mock' wykonujący losowe legalne ruchy."""
    
    def get_move(self, board: chess.Board, legal_moves: list=None) -> chess.Move:
        if legal_moves is None:
            legal_moves = list(board.legal_moves)
        
        return random.choice(legal_moves) if legal_moves else None
    