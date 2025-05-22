from matrix_modes import *

def get_modes(board):
    return [
        ShowImage(
            board.lights.get_box_coords(COORD(0, 0), GRID(16, 16)),
            pathlib.Path('images', 'cloudy_weather.gif'),
            GRID(16, 16),
        )
    ]