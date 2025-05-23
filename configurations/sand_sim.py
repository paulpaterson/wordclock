from matrix_modes import *

def get_modes(board):
    return [
        SandSim(
            board.lights.get_box_coords(COORD(0, 0), GRID(16, 16)),
            GRID(16, 16),
            {
                0: COLOR(0, 0, 0),
                1: COLOR(255, 0, 0),
                2: COLOR(0, 255, 0),
                3: COLOR(0, 0, 255),
            },
            5,
            1,
            200
        )
    ]
