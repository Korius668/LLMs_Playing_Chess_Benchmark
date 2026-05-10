import customtkinter as ctk
from core.game_manager import GameManager
from players.ollama_player import OllamaPlayer
from players.random_move_player import RandomMovePlayer
from gui.board_view import ChessBoardView

QWEN = "qwen2.5-coder:1.5b-base"
LLAMA = "llama3.1:8b"


def main():
    # 1. Konfiguracja modularna
    player_white = RandomMovePlayer(name="RandomBot")
    # player_black = OllamaPlayer(model_name=LLAMA, name="LLAMA")
    player_black = RandomMovePlayer(name="RandomBot")
    # 2. Silnik
    manager = GameManager(player_white, player_black)
    
    # 3. GUI (Opcjonalne)
    root = ctk.CTk()
    root.title("Chess LLM Benchmark Arena")
    
    view = ChessBoardView(root, manager)
    view.pack(padx=20, pady=20)

    def game_loop():
        if manager.play_next_move():
            view.update_view()
            root.after(500, game_loop) # Kolejny ruch za 500ms
        else:
            print(f"Koniec! Wynik: {manager.board.result()}")

    ctk.CTkButton(root, text="Start Game", command=game_loop).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    main()