
import chess

class GameManager:
    def __init__(self, white_player, black_player):
        self.board = chess.Board()
        self.white = white_player
        self.black = black_player
        self.history = []

    def play_next_move(self):
        if self.board.is_game_over():
            return False

        current_player = self.white if self.board.turn == chess.WHITE else self.black
        move = current_player.get_move(self.board)

        if move and move in self.board.legal_moves:
            self.board.push(move)
            self.history.append(move.uci())
            return True
        else:
            return False
        
def play_move_in_position(model, fen):
    try:
        board = chess.Board(fen)
    except ValueError:
        return "Invalid FEN"   
    move = model.get_move(board)
    
    return move.uci() if move else "FAILED"