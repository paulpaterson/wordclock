from collections import namedtuple
from typing import Iterator, NamedTuple


class GRID(NamedTuple):
    rows: int
    cols: int

COLOR = namedtuple('COLOR', ['red', 'green', 'blue'])
COORD = namedtuple('COORD', ['row', 'col'])

WHITE = COLOR(255, 255, 255)
BLACK = COLOR(0, 0, 0)
RED = COLOR(255, 0, 0)
GREEN = COLOR(0, 255, 0)
BLUE = COLOR(0, 0, 255)
ORANGE = COLOR(255, 255, 0)
YELLOW = COLOR(0, 255, 255)



class NoSuchLight(Exception):
    """A light was not found"""

class OutOfGridRange(Exception):
    """Tried to get a coordinate that would be outside of the grid"""


class Light:
    """Represents a single light in the matrix"""

    def __init__(self) -> None:
        """Initialise the light"""
        self.on = False
        self.color = WHITE

    def set_color(self, color: COLOR, on: bool|None=True) -> None:
        """Set the color of the light"""
        self.color = color
        if on is not None:
            self.on = on

    def turn_on(self) -> None:
        """Turn the light on"""
        self.on = True

    def turn_off(self) -> None:
        """Turn the light off"""
        self.on = False

    def toggle(self) -> None:
        """Toggle the light"""
        self.on = not self.on

    def get_shown_color(self) -> COLOR:
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

    def rows(self) -> list[list[Light]]:
        """Iterate over the rows of lights"""
        return self.lights

    def get_light_at(self, coords: COORD) -> Light:
        """Return the light at a certain coordinate"""
        if coords.row < 0 or coords.col < 0:
            raise NoSuchLight(f'Cannot use negative rows or columns: {coords}')
        try:
            light: Light = self.lights[coords.row][coords.col]
        except IndexError:
            raise NoSuchLight(f'No light found at {coords}')
        return light

    def get_row_coords(self, row: int) -> list[COORD]:
        """Return a row of coords"""
        if row < 0 or row >= self.size.rows:
            raise OutOfGridRange(f'Row {row} would be outside the grid ({self.size}')
        return [COORD(row, col) for col in range(self.size.cols)]

    def get_col_coords(self, col: int) -> list[COORD]:
        """Return a col of coords"""
        if col < 0 or col >= self.size.cols:
            raise OutOfGridRange(f'Col {col} would be outside the grid ({self.size}')
        return [COORD(row, col) for row in range(self.size.rows)]

    def get_edge_coords(self) -> list[COORD]:
        """Return a list of the edge cells"""
        return self.get_ring_coords(0)

    def get_ring_coords(self, distance: int) -> list[COORD]:
        """Return a ring of cells at a certain distance from the edge"""
        if distance == self.size.rows / 2 or distance == self.size.cols / 2:
            return []
        result = self.get_row_coords(distance)[distance:self.size.cols-distance]
        result += self.get_col_coords(self.size.cols - distance - 1)[distance + 1:self.size.rows-distance]
        result += list(reversed(self.get_row_coords(self.size.rows - distance - 1)))[distance + 1:self.size.cols-distance]
        result += list(reversed(self.get_col_coords(distance)))[distance + 1:self.size.rows-distance - 1]
        return result

    def get_box_coords(self, top_left: COORD, size: GRID) -> list[COORD]:
        """Return a box of cells"""
        #
        # Validity check
        if top_left.col < 0 or top_left.row < 0 or top_left.row + size.rows > self.size.rows or top_left.col + size.cols > self.size.cols:
            raise OutOfGridRange(f'Box ({top_left}, {size}) would be outside range of grid ({size}')
        return [COORD(row, col) for col in range(top_left.col, top_left.col + size.cols)
                for row in range(top_left.row, top_left.row + size.rows)]

    def __iter__(self) -> Iterator[Light]:
        """Iterate through the lights"""
        for row in self.rows():
            for col in row:
                yield col

    def __len__(self) -> int:
        """Return the number of lights"""
        return self.size.rows * self.size.cols
