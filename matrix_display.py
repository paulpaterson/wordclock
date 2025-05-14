"""Drives a Matrix Display with various display modes"""
import time

import click
import blessed
from matrix_modes import Mode, CycleColors
from matrix_common import *

# Load LED control stuff if it is there
baud_rate = 800
try:
    from pi5neo import Pi5Neo
except ImportError:
    matrix_leds = None
else:
    matrix_leds = lambda n: Pi5Neo('/dev/spidev0.0', n, baud_rate)


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

    def display_leds(self):
        """Update the LED board"""
        if not matrix_leds:
            raise ImportError('Cannot import the led control')
        #
        # There is an odd pattern to the for loops here
        # because the LED numbers go in a line that zig zags
        # across the matrix
        idx = 0
        for col in range(self.size.cols):
            if col % 2 == 0:
                row_range = range(self.size.rows)
            else:
                row_range = range(self.size.rows -1, -1, -1)
            for row in row_range:
                light = self.lights.get_light_at(COORD(row, col))
                color = light.get_shown_color()
                matrix_leds.set_led_color(idx, *color)
                #
                idx += 1

    def update_board(self):
        """Update the board"""
        for mode in self.modes:
            mode.update(self.lights)


if __name__ == "__main__":
    b = DisplayMatrix(GRID(16, 16), [])
    b.modes.append(
        CycleColors(
            b.lights.get_edge_coords(),
            [RED, BLUE, GREEN]
        )
    )
    b.modes.append(
        CycleColors(
            b.lights.get_ring_coords(1),
            [ORANGE, YELLOW]
        )
    )
    b.modes.append(
        CycleColors(
            b.lights.get_box_coords(COORD(3, 4), GRID(2, 4)),
            [YELLOW, WHITE],
            synchronized=True
        )
    )
    while True:
        b.update_board()
        b.display_board()
        if matrix_leds:
            b.display_leds()
        time.sleep(1)




