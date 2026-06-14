import chess
import chess.engine
from tqdm.asyncio import tqdm


def evaluate_move(fen, move_uci, stockfish_path):
    board = chess.Board(fen)

    with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:

        info_best = engine.analyse(board, chess.engine.Limit(time=0.1))
        before_score = info_best["score"].white().score(mate_score=10000)

        move = chess.Move.from_uci(move_uci)
        if move not in board.legal_moves:
            return "Illegal Move", None
            
        board.push(move)
        
        info_after = engine.analyse(board, chess.engine.Limit(time=0.1))
        after_score = info_after["score"].white().score(mate_score=10000)

        gain = after_score - before_score
        return after_score, gain

def centipawn_diff(engine, board, board2):
    info_best = engine.analyse(board, chess.engine.Limit(time=0.1))
    before_score = info_best["score"].relative.score(mate_score=10000)
    

    
    info_after = engine.analyse(board2, chess.engine.Limit(time=0.1))
    after_score = info_after["score"].relative.score(mate_score=10000)

    gain = after_score - before_score
    
    return after_score, gain


def centipawn_score(engine, board):
    info_after = engine.analyse(board, chess.engine.Limit(time=0.1))
    after_score = info_after["score"].white().score(mate_score=10000)

    return after_score

def calculate_material_balance(board: chess.Board) -> int:

    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }
    
    white_score = 0
    black_score = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                white_score += value
            else:
                black_score += value
                
    white_perspective_score = white_score - black_score

    multiplier = 1 if board.turn == chess.WHITE else -1
    
    return white_perspective_score * multiplier


def calculate_mobility(board: chess.Board, board_2: chess.Board) -> int:
    current_turn = board.turn
    board.turn = chess.WHITE
    white_moves = board.legal_moves.count()
    board.turn = chess.BLACK
    black_moves = board.legal_moves.count()
    board.turn = current_turn

    board_2.turn = chess.WHITE
    white_moves_diff = board_2.legal_moves.count() - white_moves
    board_2.turn = chess.BLACK
    black_moves_diff = board_2.legal_moves.count() - black_moves

    if board.turn == chess.WHITE:
        return white_moves_diff, black_moves_diff
    else:
        return black_moves_diff, white_moves_diff
    
def count_doubled_pawns(board: chess.Board) -> int:
    doubled_pawns = 0
    current_turn = board.turn
    for file_index in range(8):
        pawns_in_file = 0
        for rank_index in range(8):
            square = chess.square(file_index, rank_index)
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN and piece.color == current_turn:
                pawns_in_file += 1
        if pawns_in_file > 1:
            doubled_pawns += (pawns_in_file - 1)
    return doubled_pawns

def evaluate_moves(fens, moves, stockfish_path):
    after_scores, gains, material_balances, player_mobility_differences, opponent_mobility_differences, doubled_pawnses = [], [], [], [], [], []
    with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
        for fen, move_uci in tqdm(zip(fens, moves), total=len(fens), unit="scores"):
           
            try:
                move = chess.Move.from_uci(move_uci)
                board = chess.Board(fen)
                board_2 = chess.Board(fen)
                board_2.push(move)

                if move not in board.legal_moves:
                    after_scores.append(None)
                    gains.append(None)
                    material_balances.append(None)
                    player_mobility_differences.append(None)
                    opponent_mobility_differences.append(None)
                    doubled_pawnses.append(None)
                    continue
            except (chess.InvalidMoveError, ValueError):
                # print(f"Invalid move '{move_uci}' for possible moves: {list(board.legal_moves)}")
                after_scores.append(None)
                gains.append(None)
                material_balances.append(None)
                player_mobility_differences.append(None)
                opponent_mobility_differences.append(None)
                doubled_pawnses.append(None)
                continue
            
            after_score, gain = centipawn_diff(engine, board, board_2 )
            material_balance = calculate_material_balance(board)
            player_mobility_diff, opponent_mobility_diff = calculate_mobility(board, board_2)
            doubled_pawns = count_doubled_pawns(board)
            
            after_scores.append(after_score)
            gains.append(gain)
            material_balances.append(material_balance)
            player_mobility_differences.append(player_mobility_diff)
            opponent_mobility_differences.append(opponent_mobility_diff)
            doubled_pawnses.append(doubled_pawns)
            
    return {"after_scores": after_scores, "gains": gains, "material_balances": material_balances, "player_mobility_differences": player_mobility_differences, "opponent_mobility_differences": opponent_mobility_differences, "doubled_pawnses": doubled_pawnses}
