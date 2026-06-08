import inspect
import re
import chess
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache

from core.player_base import BasePlayer


class OllamaPlayer(BasePlayer):
    def __init__(self, model_name="llama2", name="Ollama-AI", verbose=False, cache=False):
        super().__init__(name)
        self.verbose = verbose
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', model_name)
        model_specific_cache = SQLiteCache(database_path=f"chess_cache_{safe_name}.db", allowed_objects="messages")
        self.llm = ChatOllama(
            name = model_name,
            model=model_name,
            cache= model_specific_cache,
            temperature=0,
            num_predict=32,
            num_gpu=1,
            num_thread=4,
            repeat_penalty=1,
            top_p=0.9
        )

        
    def get_move(self, board: chess.Board ) -> chess.Move:
        # history = " ".join([m.uci() for m in board.move_stack[-20:]])
        prompt = inspect.cleandoc(f"""
            System: You are a professional chess player engine. Your job is to select the absolute best move from a provided list of legal moves. You must never invent a move.
            Current Board: 
            {board}

            Moves are in long algebraic notation (e.g. e2e4 for moving a piece from e2 to e4).
            Additional 5-th character means that you are making a promotion: with the respective letter at the end q, r, b, or n if to queen, rook, bishop, or knight.
            
            Legal moves: {", ".join([m.uci() for m in board.legal_moves])}
            Task: Choose the best legal move.
        """)
 
        legal_uci_moves = [m.uci() for m in board.legal_moves]

        strict_enum_schema = {
            "type": "string",
            "enum": legal_uci_moves
        }
        
        try:           
            llm = self.llm.with_structured_output(strict_enum_schema)
            
            messages = [HumanMessage(content=prompt)]
            move_str = llm.invoke(messages)        
            
            if self.verbose:
                print(f"{self.llm.model} move: {move_str}")

            return chess.Move.from_uci(move_str)
                    
        except Exception as exc:
            print(f"OllamaPlayer error: {exc}")
            
        return None
    
    
    # def get_move_with_reasoning(self, board: chess.Board) -> chess.Move:
    #     # history = " ".join([m.uci() for m in board.move_stack[-20:]])
    #     prompt = inspect.cleandoc(f"""
    #         System: You are a professional chess player engine. Your job is to select the absolute best move from a provided list of legal moves. You must never invent a move.
    #         Current Board: 
    #         {board}

    #         Moves are in long algebraic notation (e.g. e2e4 for moving a piece from e2 to e4).
    #         Additional 5-th character means that you are making a promotion: with the respective letter at the end q, r, b, or n if to queen, rook, bishop, or knight.
            
    #         Legal moves: {", ".join([m.uci() for m in board.legal_moves])}
    #         Task: Choose the best legal move.
    #     """)
 
    #     legal_uci_moves = [m.uci() for m in board.legal_moves]

    #     strict_enum_schema = {
    #         "type": "string",
    #         "enum": legal_uci_moves
    #     }
        
    #     try:           
    #         llm = self.llm.with_structured_output(strict_enum_schema)
            
    #         messages = [HumanMessage(content=prompt)]
    #         move_str = llm.invoke(messages)        
            
    #         if self.verbose:
    #             print(f"{self.llm.model} move: {move_str}")

    #         return chess.Move.from_uci(move_str)
                    
    #     except Exception as exc:
    #         print(f"OllamaPlayer error: {exc}")
            
    #     return None