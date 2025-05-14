from collections import namedtuple

GRID = namedtuple('Grid', ['rows', 'cols'])
COLOR = namedtuple('Color', ['red', 'green', 'blue'])
COORD = namedtuple('Coordinate', ['row', 'col'])

WHITE = COLOR(255, 255, 255)
BLACK = COLOR(0, 0, 0)
RED = COLOR(255, 0, 0)
GREEN = COLOR(0, 255, 0)
BLUE = COLOR(0, 0, 255)



class NoSuchLight(Exception):
    """A light was not found"""


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

    def turn_on(self):
        """Turn the light on"""
        self.on = True

    def turn_off(self):
        """Turn the light off"""
        self.on = False

    def toggle(self):
        """Toggle the light"""
        self.on = not self.on

    def get_shown_color(self):
        """Return which color should be shown"""
        return self.color if self.on else BLACK


class LightCollection:
    """Holds a collection of lights in a matrix"""

    def __init__(self, size: GRID):
        """Initialise the collection"""
        self.lights: list[list[Light]] = []
        self.size = size
        for row in range(size.rows):
            self.lights.append([])
            for col in range(size.cols):
                self.lights[-1].append(Light())

    def rows(self):
        """Iterate over the rows of lights"""
        return self.lights

    def get_light_at(self, coords: COORD):
        """Return the light at a certain coordinate"""
        try:
            return self.lights[coords.row][coords.col]
        except IndexError:
            raise NoSuchLight(f'No light found at {coords}')

    def get_row_coords(self, row: int) -> list[COORD]:
        """Return a row of coords"""
        return [COORD(row, col) for col in range(self.size.cols)]

    def get_col_coords(self, col: int) -> list[COORD]:
        """Return a col of coords"""
        return [COORD(row, col) for row in range(self.size.rows)]

    def get_edge_coords(self) -> list[COORD]:
        """Return all the edges"""
        result = self.get_row_coords(0)
        result += self.get_col_coords(self.size.cols - 1)[1:]
        result += list(reversed(self.get_row_coords(self.size.rows - 1)))[1:]
        result += list(reversed(self.get_col_coords(0)))[1:-1]
        return result
