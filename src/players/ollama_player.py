import re
import chess
from langchain_community.llms import Ollama
from core.player_base import BasePlayer

class OllamaPlayer(BasePlayer):
    def __init__(self, model_name="llama3", name="Ollama-AI"):
        super().__init__(name)
        self.llm = Ollama(model=model_name, temperature=0) # Temp 0 dla stabilności
        self.pattern = re.compile(r"([a-h][1-8][a-h][1-8][qrbn]?)")

    def get_move(self, board: chess.Board) -> chess.Move:
        history = " ".join([m.uci() for m in board.move_stack[-20:]])
        prompt = f"""
        System: You are a professional chess player.
        Current FEN: {board.fen()}
        Last moves: {history}
        Legal moves: {", ".join([m.uci() for m in board.legal_moves])}
        
        Task: Provide your next move in UCI format. 
        Respond ONLY with the move (e.g., e2e4).
        """
        
        raw_response = self.llm.invoke(prompt).strip().lower()
        match = self.pattern.search(raw_response)
        
        if match:
            move_str = match.group(1)
            move = chess.Move.from_uci(move_str)
            if move in board.legal_moves:
                return move
        return None # Manager obsłuży błąd (np. przegrana przez nielegalny ruch)
    