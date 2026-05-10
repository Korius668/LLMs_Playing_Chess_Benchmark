import customtkinter as ctk
import chess.svg
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from PIL import Image, ImageTk
import io

class ChessBoardView(ctk.CTkFrame):
    def __init__(self, master, game_manager):
        super().__init__(master)
        self.gm = game_manager
        self.label = ctk.CTkLabel(self, text="")
        self.label.pack()
        self.update_view()

    def update_view(self):
        # Generowanie obrazu bez cairosvg
        svg_data = chess.svg.board(self.gm.board, size=450)
        drawing = svg2rlg(io.BytesIO(svg_data.encode("utf-8")))
        png_io = io.BytesIO()
        renderPM.drawToFile(drawing, png_io, fmt="PNG")
        
        img = Image.open(png_io)
        self.tk_img = ImageTk.PhotoImage(img)
        self.label.configure(image=self.tk_img)