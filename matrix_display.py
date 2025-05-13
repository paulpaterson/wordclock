"""Drives a Matrix Display with various display modes"""

import click
import blessed
from collections import namedtuple

GRID = namedtuple('Grid', ['rows', 'cols'])
COLOR = namedtuple('Color', ['red', 'green', 'blue'])

WHITE = COLOR(255, 255, 255)
BLACK = COLOR(0, 0, 0)


class Light:
    """Represents a single light in the matrix"""

    def __init__(self):
        """Initialise the light"""
        self.on = False
        self.color = WHITE

    def set_color(self, color: COLOR, on=True):
        """Set the color of the light"""
        self.color = color
        if on:
            self.on = on

    def get_shown_color(self):
        """Return which color should be shown"""
        return self.color if self.on else BLACK


class Mode:
    """An abstract mode that drives the matrix display"""

    def __init__(self, parameters):
        """Initialise the mode"""

    def update(self, board):
        """Update the board according to the mode"""



class DisplayMatrix:
    """Represents the matrix being displayed"""

    def __init__(self, size: GRID, modes: list[Mode]):
        """Initialise the matrix"""
        self.term = blessed.Terminal()
        self.size = size
        self.lights = self.get_init_lights()
        self.modes = modes

    def get_init_lights(self) -> list[list[Light]]:
        """Create the lights in their initial state"""
        lights = []
        for row in range(self.size.rows):
            lights.append([])
            for col in range(self.size.cols):
                lights[-1].append(Light())
        #
        return lights

    def display_board(self):
        """Update the display of the board"""
        print(self.term.home + self.term.clear)
        for row in self.lights:
            for light in row:
                color = light.get_shown_color()
                print(self.term.color_rgb(*color) + "■", end="")
            print('')


if __name__ == "__main__":
    b = DisplayMatrix(GRID(16, 16), [])
    b.lights[1][1].on = True
    b.lights[14][14].set_color(COLOR(255, 0, 0))
    b.lights[10][12].set_color(COLOR(255, 255, 0))
    b.display_board()




