import matrix_display
import matrix_modes
from matrix_modes import *

def get_modes(board: matrix_display.DisplayMatrix) -> list[matrix_modes.Mode]:
    return [
            CycleColors(
                board.lights.get_edge_coords(),
                [RED, BLUE, GREEN]
            ),
            CycleColors(
                board.lights.get_ring_coords(1),
                [ORANGE, YELLOW]
            ),
            CycleColors(
                board.lights.get_box_coords(COORD(3, 4), GRID(2, 4)),
                [YELLOW, WHITE],
                synchronized=True
            ),
    ]

