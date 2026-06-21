import chess
import chess.svg
import cairosvg
import io
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

def create_chess_gif(df, white_name, black_name, output_filename="game.gif", duration=700):
    board = chess.Board()
    images = []

    # Load Pillow's default font
    try:
        font = ImageFont.load_default(size=18)
    except TypeError:
        font = ImageFont.load_default()

    def capture_frame(current_board, lastmove=None, cp_score="0.00"):
        # Render SVG and convert to Pillow Image
        svg_data = chess.svg.board(current_board, size=400, lastmove=lastmove)
        png_bytes = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))
        board_img = Image.open(io.BytesIO(png_bytes))

        # Create canvas with white margins
        canvas = Image.new("RGB", (400, 480), "white")
        canvas.paste(board_img, (0, 40))
        draw = ImageDraw.Draw(canvas)
        
        # Draw text
        draw.text((10, 10), f"Black: {black_name}", fill="black", font=font)
        draw.text((310, 10), f"CP: {cp_score}", fill="black", font=font)
        draw.text((10, 450), f"White: {white_name}", fill="black", font=font)

        images.append(canvas)

    # 1. Capture starting position
    capture_frame(board, cp_score="+0.20")

    # 2. Iterate through the DataFrame rows
    for index, row in df.iterrows():
        # Ensure your DataFrame columns are named 'uci' and 'cp'
        move_str = str(row['uci'])
        cp = str(row['cp']) 
        
        move = chess.Move.from_uci(move_str)
        if move in board.legal_moves:
            board.push(move)
            capture_frame(board, lastmove=move, cp_score=cp)
        else:
            print(f"Illegal move detected at row {index}: {move_str}. Stopping here.")
            break
    # 3. Save as GIF
    if images:
        images[0].save(
            output_filename,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=0
        )
        print(f"Successfully saved {output_filename}")



if __name__ == "__main__":


    df = pd.read_csv("results/tournaments/tournament_16/match_R2_M1.csv")
    df2 = df[["move_uci", "centipawn_score"]].rename(columns={
    "move_uci": "uci", 
    "centipawn_score": "cp"
})

    # 3. Extract names (adjust these indices if your CSV rows are structured differently!)
    white_player = df["player_name"].iloc[0]
    black_player = df["player_name"].iloc[1]
    create_chess_gif(df=df2,white_name=white_player, black_name=black_player, output_filename="match_T1_R2_M1.gif", duration=800)