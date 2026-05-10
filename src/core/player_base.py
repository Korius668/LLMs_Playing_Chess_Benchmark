import chess

class BasePlayer:
    def __init__(self, name="BasePlayer"):
        self.name = name

    def get_move(self, board: chess.Board) -> chess.Move:
        """Przyjmuje obiekt board, zwraca obiekt Move."""
        raise NotImplementedError
    