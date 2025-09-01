"""Drives a Matrix Display with various display modes"""
import time
import pathlib
import importlib
from types import FrameType
from typing import Any

import click
import blessed
from matrix_modes import Mode, CycleColors, ShowImage
from matrix_common import *
import configurations
import signal
import sys


# Load LED control stuff if it is there
baud_rate = 1000 # 800 maybe for the RPI5
try:
    import pi5neo    # type: ignore
except ImportError:
    pi5neo = None

def get_matrix_leds(n: int) -> Any:
    if pi5neo:
        return pi5neo.Pi5Neo('/dev/spidev0.0', n, baud_rate)
    else:
        return None


class DisplayMatrix:
    """Represents the matrix being displayed"""

    def __init__(self, size: GRID, modes: list[Mode]) -> None:
        """Initialise the matrix"""
        self.term = blessed.Terminal()
        self.size = size
        self.lights = LightCollection(size)
        self.modes = modes
        #
        # Initialise the hardware lights if we have them
        self.matrix_leds = get_matrix_leds(size.rows * size.cols)

    def display_board(self) -> None:
        """Update the display of the board"""
        print(self.term.home + self.term.clear)
        for row in self.lights.rows():
            for light in row:
                color = light.get_shown_color()
                print(self.term.color_rgb(*color) + "■", end="")
            print('')

    def display_leds(self) -> None:
        """Update the LED board"""
        if not self.matrix_leds:
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
                self.matrix_leds.set_led_color(idx, *color)
                #
                idx += 1
        #
        self.matrix_leds.update_strip()

    def update_board(self) -> None:
        """Update the board"""
        for mode in self.modes:
            mode.update(self.lights)

@click.command()
@click.option('--screen', default=False, type=bool, is_flag=True, help="Whether to show the simulation on the screen")
@click.option('--leds', default=False, type=bool, is_flag=True, help="Whether to try to control the LED matrix")
@click.option('--interval', default=10, type=float, help="Refresh interval (s)")
@click.option('--config', required=True, type=str, help="File to use for config")
@click.argument('parameters', nargs=-1)
def main(screen: bool, leds: bool, interval: float, config: str, parameters: list[str]) -> None:
    def signal_handler(sig: int, frame: FrameType|None) -> None:
        """Handle the SIGTERM from SystemD"""
        print(f'Caught SIGTERM {sig}')
        if b.matrix_leds:
            print('Clearing strip')
            b.matrix_leds.clear_strip()
            b.matrix_leds.update_strip()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)

    b = DisplayMatrix(GRID(16, 16), [])

    config_module = importlib.import_module(config)
    modes = config_module.get_modes(b, *parameters)
    for mode in modes:
        b.modes.append(mode)

    try:
        while True:
            b.update_board()
            if screen:
                b.display_board()
            if leds and b.matrix_leds:
                b.display_leds()
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    #
    if b.matrix_leds:
        print('Clearing strip')
        b.matrix_leds.clear_strip()
        b.matrix_leds.update_strip()


if __name__ == "__main__":
    main()




