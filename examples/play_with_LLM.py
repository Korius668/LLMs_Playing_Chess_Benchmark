import chess
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.llm import LLMChain

MIXTRAL = "mixtral:8x7b"
GEMMA = "gemma2:27b"
QWEN = "qwen2.5:72b"
LLAMA = "llama3.1:8b"
PHI = "phi3:3.8b"


class ChessGame:
    def __init__(self, model_name=QWEN):
        self.board = chess.Board()
        # Konfiguracja modelu przez LangChain
        self.llm = Ollama(model=model_name)

        self.template = """
        You are a professional chess engine. Your goal is to provide the best legal move in the given position.
        
        Current position (FEN): {fen}
        Move history (PGN): {history}
        
        Rules:
        1. Respond ONLY with a single move in UCI format (e.g., e2e4, g1f3, e7e8q).
        2. Do not provide any explanations, comments, or extra text.
        3. Ensure the move is legal according to the FEN provided.
        
        Your move:"""
        
        self.prompt = PromptTemplate(template=self.template, input_variables=["fen", "history"])
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def display_board(self):
        print("\n" + str(self.board))
        print(f"\nFEN: {self.board.fen()}")

    def get_llm_move(self):
        history = " ".join([move.uci() for move in self.board.move_stack])
        response = self.chain.run(fen=self.board.fen(), history=history)
        return response.strip().lower()

    def play(self):
        print("Witaj w ChessLLM! Grasz białymi. Wpisuj ruchy w formacie UCI (np. e2e4).")
        
        while not self.board.is_game_over():
            self.display_board()
            
            if self.board.turn == chess.WHITE:
                user_move = input("\nTwój ruch (UCI): ")
                try:
                    move = chess.Move.from_uci(user_move)
                    if move in self.board.legal_moves:
                        self.board.push(move)
                    else:
                        print("Ruch nielegalny! Spróbuj ponownie.")
                except ValueError:
                    print("Błędny format! Użyj np. e2e4.")
            else:
                print("\nLLM myśli...")
                move_str = self.get_llm_move()
                try:
                    move = chess.Move.from_uci(move_str)
                    if move in self.board.legal_moves:
                        print(f"LLM zagrał: {move_str}")
                        self.board.push(move)
                    else:
                        print(f"LLM próbował nielegalnego ruchu: {move_str}. Koniec gry.")
                        break
                except ValueError:
                    print(f"LLM zwrócił śmieci zamiast ruchu: {move_str}")
                    break

        print("\nKoniec gry!")
        print(f"Wynik: {self.board.result()}")

if __name__ == "__main__":

    game = ChessGame(model_name=QWEN)
    game.play()