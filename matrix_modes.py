"""Modes that control lights on the matrix"""

import pathlib
import PIL.Image
from matrix_common import *


class ModeUpdateError(Exception):
    """An error occurred while updating the mode"""


class Mode:
    """An abstract mode that drives the matrix display"""

    def __init__(self, locations: list[COORD]):
        """Initialise the mode"""
        self.light_locations = locations

    def update(self, lights: LightCollection):
        """Update the board according to the mode"""



class CycleColors(Mode):
    """A mode that cycles colors"""

    def __init__(self, locations, colors: list[COLOR], synchronized=False):
        """Initialise the mode"""
        super().__init__(locations)
        self.color_list = colors
        self.synchronized = synchronized

    def update(self, lights: LightCollection):
        """Update all the colors"""
        if not self.color_list:
            raise ModeUpdateError(f'There are no colors defined in this mode, {self}')
        #
        colors = self.color_list[:]
        for location in self.light_locations:
            light = lights.get_light_at(location)
            light.set_color(colors[0])
            if not self.synchronized:
                colors.insert(0, colors.pop())
        #
        # Cycle the lights for next time
        self.color_list.append(self.color_list.pop(0))


class ShowImage(Mode):
    """A mode that shows one or more images in sequence"""

    def __init__(self, locations, file: pathlib.Path, size: GRID):
        """Initialise the mode"""
        super().__init__(locations)
        self.original_image = PIL.Image.open(file)
        self.frames: list[PIL.Image] = []
        self.size = size
        #
        # Extract all the frames if there are some
        if self.original_image.n_frames > 0:
            for idx in range(self.original_image.n_frames):
                self.original_image.seek(idx)
                self.frames.append(self.get_frame_from(self.original_image))
        else:
            self.frames.append(self.original_image)

    def get_frame_from(self, image: PIL.Image):
        """Return a scaled and converted frame"""
        frame = image.convert('RGB')
        frame = frame.resize(self.size)
        return frame

    def update(self, lights: LightCollection):
        """Update the representation of the picture"""
        #
        # Get the frame to display
        frame = self.frames.pop(0)
        self.frames.append(frame)
        #
        # Now light up the display pixels
        for location in self.light_locations:
            light = lights.get_light_at(location)
            light.set_color(frame.getpixel((location.col, location.row)))
