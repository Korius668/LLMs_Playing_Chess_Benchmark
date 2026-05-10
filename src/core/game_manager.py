
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
            # Ruch nielegalny = automatyczna przegrana w benchmarku
            return False