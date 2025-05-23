"""Modes that control lights on the matrix"""

import random
import time
import os
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


class SandSim(Mode):
    """A mode that runs a sand falling simulation"""

    def __init__(self, locations, size: GRID, colors: dict[int, COLOR],
                 drop_interval: int=5, drop_count: int=1, max_sim_length: int=200):
        super().__init__(locations)
        self.sim = SandSimulation(size.cols, size.rows)
        self.iteration = 0
        self.colors = colors
        self.drop_interval = drop_interval
        self.drop_count = drop_count
        self.max_sim_length = max_sim_length

    def update(self, lights: LightCollection):
        """Update the simulation"""
        self.sim.run_simulation(1, self.drop_interval, self.drop_count)
        for location in self.light_locations:
            sand = self.sim.grid[location.row][location.col]
            color =  self.colors[sand]
            light = lights.get_light_at(location)
            light.set_color(color)
        #
        self.iteration += 1
        if self.iteration >= self.max_sim_length:
            self.sim.init_grid()
            self.iteration = 0


class SandSimulation:
    def __init__(self, width=16, height=16):
        """
        Initializes the sand simulation grid.

        Args:
            width (int): The width of the simulation grid.
            height (int): The height of the simulation grid.
        """
        self.width = width
        self.height = height
        # Initialize the grid with empty spaces (0)
        self.init_grid()
        # Define sand types (colors) and their display characters
        # You can add more types here
        self.sand_types = {
            1: 'o',  # Orange sand
            2: '#',  # Gray sand
            3: '*',  # Yellow sand
        }
        self.empty_char = '.' # Character for empty space

    def init_grid(self):
        """Initialise the grid"""
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

    def _clear_screen(self):
        """Clears the terminal screen for animation."""
        # For Windows
        if os.name == 'nt':
            _ = os.system('cls')
        # For macOS and Linux
        else:
            _ = os.system('clear')

    def _draw_grid(self):
        """Prints the current state of the grid to the console."""
        self._clear_screen()
        print("Sand Falling Simulation (16x16)")
        print("------------------------------")
        for row in self.grid:
            # Convert sand type numbers to their display characters
            print(" ".join([self.sand_types.get(cell, self.empty_char) for cell in row]))
        print("------------------------------")
        print("Press Ctrl+C to stop.")

    def add_sand(self, col, sand_type=1):
        """
        Adds a single sand particle of a specified type at the top of a given column.

        Args:
            col (int): The column index where the sand should be added (0 to width-1).
            sand_type (int): The type of sand to add (e.g., 1, 2, 3).
        """
        if 0 <= col < self.width and sand_type in self.sand_types:
            if self.grid[0][col] == 0: # Only add if the top cell is empty
                self.grid[0][col] = sand_type
            else:
                print(f"Column {col} is blocked at the top. Cannot add sand.")
        else:
            print(f"Invalid column ({col}) or sand type ({sand_type}).")

    def _update_sand(self):
        """
        Applies the falling logic to all sand particles in the grid.
        Iterates from bottom to top to ensure correct falling behavior.
        """
        for r in range(self.height - 2, -1, -1): # Iterate from second-to-last row up to the first
            for c in range(self.width):
                current_cell = self.grid[r][c]

                if current_cell != 0: # If there's sand in the current cell
                    # Check directly below
                    if self.grid[r + 1][c] == 0:
                        self.grid[r + 1][c] = current_cell
                        self.grid[r][c] = 0
                    else:
                        # Check diagonal left
                        can_fall_left = (c > 0 and self.grid[r + 1][c - 1] == 0)
                        # Check diagonal right
                        can_fall_right = (c < self.width - 1 and self.grid[r + 1][c + 1] == 0)

                        if can_fall_left and can_fall_right:
                            # If both diagonal paths are open, choose one randomly
                            if random.choice([True, False]):
                                self.grid[r + 1][c - 1] = current_cell
                                self.grid[r][c] = 0
                            else:
                                self.grid[r + 1][c + 1] = current_cell
                                self.grid[r][c] = 0
                        elif can_fall_left:
                            self.grid[r + 1][c - 1] = current_cell
                            self.grid[r][c] = 0
                        elif can_fall_right:
                            self.grid[r + 1][c + 1] = current_cell
                            self.grid[r][c] = 0
                        # If none of the above, sand stays put (it's settled)

    def run_simulation(self, steps=100, drop_interval=5, drop_count=1):
        """
        Runs the sand falling simulation for a specified number of steps.

        Args:
            steps (int): The total number of simulation steps to run.
            drop_interval (int): How often (in steps) new sand is dropped.
            drop_count (int): How many sand particles to drop at each interval.
        """
        print("Starting simulation... Press Ctrl+C to stop.")
        try:
            for i in range(steps):
                # Drop new sand periodically
                if i % drop_interval == 0:
                    for _ in range(drop_count):
                        # Drop random sand type in a random column
                        self.add_sand(random.randint(0, self.width - 1), random.choice(list(self.sand_types.keys())))

                self._update_sand()
        except KeyboardInterrupt:
            print("\nSimulation stopped by user.")
        finally:
            print("Simulation finished.")


