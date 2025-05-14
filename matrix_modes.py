"""Modes that control lights on the matrix"""

from matrix_common import *


class ModeUpdateError(Exception):
    """An error occurred while updating the mode"""


class Mode:
    """An abstract mode that drives the matrix display"""

    def __init__(self, locations: list[COORD]):
        """Initialise the mode"""
        self.light_locations = locations

    def update(self, board):
        """Update the board according to the mode"""



class CycleColors(Mode):
    """A mode that cycles colors"""

    def __init__(self, locations, colors: list[COLOR]):
        """Initialise the mode"""
        super().__init__(locations)
        self.color_list = colors

    def update(self, lights: LightCollection):
        """Update all the colors"""
        if not self.color_list:
            raise ModeUpdateError(f'There are no colors defined in this mode, {self}')
        #
        colors = self.color_list[:]
        for location in self.light_locations:
            light = lights.get_light_at(location)
            light.set_color(colors[0])
            colors.insert(0, colors.pop())
        #
        # Cycle the lights for next time
        self.color_list.append(self.color_list.pop(0))