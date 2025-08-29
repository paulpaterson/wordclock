import matrix_display
import matrix_modes
from matrix_modes import *
import pathlib

def get_modes(board: matrix_display.DisplayMatrix, filename: str) -> list[matrix_modes.Mode]:
    return [
        ShowImage(
            board.lights.get_box_coords(COORD(0, 0), GRID(16, 16)),
            pathlib.Path('images', filename),
            GRID(16, 16),
        )
    ]