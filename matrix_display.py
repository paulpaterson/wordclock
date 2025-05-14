"""Drives a Matrix Display with various display modes"""
import time

import click
import blessed
from matrix_modes import Mode, CycleColors
from matrix_common import *


class DisplayMatrix:
    """Represents the matrix being displayed"""

    def __init__(self, size: GRID, modes: list[Mode]):
        """Initialise the matrix"""
        self.term = blessed.Terminal()
        self.size = size
        self.lights = LightCollection(size)
        self.modes = modes

    def display_board(self):
        """Update the display of the board"""
        print(self.term.home + self.term.clear)
        for row in self.lights.rows():
            for light in row:
                color = light.get_shown_color()
                print(self.term.color_rgb(*color) + "■", end="")
            print('')

    def update_board(self):
        """Update the board"""
        for mode in self.modes:
            mode.update(self.lights)


if __name__ == "__main__":
    b = DisplayMatrix(GRID(16, 16), [])
    b.modes.append(
        CycleColors(
            [COORD(2, 5), COORD(2, 6), COORD(2, 7), COORD(1, 5), COORD(1, 6), COORD(1, 7)],
            [RED, BLUE, GREEN]
        )
    )
    b.modes.append(
        CycleColors(
            [COORD(r, c) for r in [0, 15] for c in range(16)] + [COORD(r, c) for c in [0, 15] for r in range(16)],
            [GREEN, WHITE]
        )
    )
    while True:
        b.update_board()
        b.display_board()
        time.sleep(1)




