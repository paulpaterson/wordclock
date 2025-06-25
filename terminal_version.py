import enum
import random
import signal
import sys
import os
import datetime
import time

import blessed
import blessed.sequences
import timesayer
import click
import mocklights
import faces
import modes


RUN_MODES = ['NORMAL', 'CALCSIZE', 'SHOWLETTERS']

class Board:
    """Represents of the words arranged in a board"""

    def __init__(self, term, time, simple=False, show_it_is=False, lights=None, light_color=None,
                 replace_blanks=False, blank_character=' ', edge_character=' ', show_a=False, display=None):
        self.term = term
        self.time = time
        self.rows = None
        self.simple = simple
        self.show_it_is = show_it_is
        self.total_lights = 0
        self.lights = None
        self.lights_fn = lights
        self.light_color = light_color
        self.fill_character = blank_character
        self.edge_character = edge_character
        self.replace_blanks = replace_blanks
        self.show_a = show_a
        self.edge_lights = {}
        self.modes = display or [modes.Normal(None)]

    def add_word(self, word):
        if word.word and word.word[0] == 'x':
            word.word = self.get_fill_character(len(word.word))
        self.rows[word.line].append(word)

    def add_words(self, words):
        current_line = 0
        self.rows = [[]]
        for word in words:
            if word.new_line:
                current_line += 1
                self.rows.append([])
            else:
                word.line = current_line
                self.add_word(word)

        cols, rows = self.get_dimensions()
        self.total_lights = cols * rows
        if self.lights_fn:
            self.lights = self.lights_fn(self.total_lights)

    def get_fill_character(self, number=1):
        """Returns a new character to use as a fill character"""
        blanks = ''
        for _ in range(number):
            if not self.replace_blanks:
                blanks += self.fill_character
            else:
                blanks += random.choice('ACEFILSTU')
        return blanks

    def get_board_text(self, terminal_mode=True):
        text = []
        width, height = self.get_dimensions()
        for idx, row in enumerate(self.rows):
            text.append('')
            for word in row:
                text[-1] += f'{word.show(self.term, terminal_mode)}'
            text[-1] = text[-1] + self.get_fill_character(width - len(text[-1]))
        return text

    def get_outer_edge(self):
        """Generate the view of the outer edge lights"""
        text = []
        width, height = self.get_dimensions()

        for row in range(height):
            for col in range(width):
                if self.edge_lights.get((row, col)):
                    light = self.term.move_xy(col, row + 1) + self.term.color_rgb(*self.edge_lights[(row, col)]) + '*'
                    text.append(light)

        text.append(self.term.move_xy(0, height + 2))

        return text

    def show_board(self, logs):
        print(self.term.home + self.term.clear)
        text_lines = self.get_board_text(terminal_mode=self.lights is None)
        print('\n'.join(text_lines))
        print('\n'.join(self.get_outer_edge()))
        print()
        print(self.term.green(f"Time = {self.time.strftime('%H:%M')}, {timesayer.convert_to_text(self.time, show_a=self.show_a)}"))
        print(self.term.green(f'Board {self.get_dimensions()}'))
        #
        if self.lights:
            self.do_lights(text_lines)
        #
        if logs:
            print(self.term.red('\nLogs\n'))
            for line in logs:
                print(self.term.red(line))


    def do_lights(self, text):
        self.lights.clear_strip()
        #
        # Lights go down from 0 in the top left and then at the end of each row they
        # bounce back up
        idx = 0
        rows, cols = self.get_dimensions()
        for col in range(cols):
            if col % 2 == 0:
                row_range = range(rows)
            else:
                row_range = range(rows -1, -1, -1)
            for row in row_range:
                letter = text[row][col]
                if letter != ' ':
                    self.lights.set_led_color(idx, *self.light_color)

                # Check edge lights
                if col == 0 or col == cols - 1 or row == 0 or row == rows - 1:
                    try:
                        edge_color = self.edge_lights[(row, col)]
                    except KeyError:
                        pass # OK, not lit
                    else:
                        if edge_color:
                            self.lights.set_led_color(idx, *edge_color)
                        else:
                            self.lights.set_led_color(idx, 0, 0, 0)

                idx += 1
        try:
            self.lights.update_strip()
        except OSError as err:
            raise Exception(f'Failed to send SPI data - is SPI interface turned on?: {err}')


    def clear_board(self):
        for row in self.rows:
            for word in row:
                word.clear()

    def get_all_words(self):
        words = []
        for row in self.rows:
            for word in row:
                words.append(word)
        return words

    def find_next_word(self, word, possible_words):
        while possible_words:
            possible_word = possible_words.pop(0)
            if possible_word.word.lower() == word.lower():
                return possible_word
        raise ValueError(f'Could not find {word} in {self.time.time()}')

    def update_board(self):
        self.clear_board()
        logs = []
        for mode in self.modes:
            results = mode.update(self)
            if results:
                logs.extend(results)

        return logs

    def convert_time(self):
        it_is = 'It is ' if self.show_it_is else ''
        return it_is + timesayer.convert_to_text(self.time, simple=self.simple,
                                         mode=timesayer.Mode.oclock,
                                         twelve_mode=timesayer.TwelveMode.number,
                                         show_a=self.show_a
        )

    def get_dimensions(self):
        rows = len(self.rows)
        cols = sum(len(word.word) for word in self.rows[int(rows / 2)])
        return (cols, rows)


@click.command()
@click.option('--offset', default=0, help='Minutes to offset from current time')
@click.option('--time', type=str, default='', help='Fix the time')
@click.option('--interval', type=float, default=10, help='Time between updates in seconds')
@click.option('--simulation-update', default=0, help='Number of minutes to advance per interval')
@click.option('--face-mode', type=click.Choice(list(faces.get_valid_faces())), required=True, help='Select which face mode')
@click.option('--run-mode', default=RUN_MODES[0], type=click.Choice(RUN_MODES), help='Mode for running this command line')
@click.option('--show-it-is', default=False, is_flag=True, help='Whether to show "it is" wording')
@click.option('--light-mode', type=click.Choice(['off', 'simulate', 'real', 'detect']), default='off',
              help='Set how to handle lights')
@click.option('--light-color', type=str, default="#0A0A0A",
              help='The color for the lights when they are on')
@click.option('--replace-blanks', default=False, is_flag=True, help='Replace blanks in the face with random letters')
@click.option('--blank-character', type=str, default=' ', help='Blank character to use')
@click.option('--edge-character', type=str, default='■', help='Character to use for the edge')
@click.option('--array-format', default=False, is_flag=True, help='When showing grid format it as python array')
@click.option('--baud-rate', default=800, type=int, help='Baud rate for SPI communication')
@click.option('--button-key', default='b', type=str, help='Keyboard key to use to simulate the hardware button')
@click.option('--show-a', default=False, is_flag=True, help='Whether to show "a" in "a quarter to ..."')
@click.option('--mode', type=click.Choice(modes.get_valid_modes()),
              multiple=True, default=['Normal'], help='Select which display modes to use, can have multiple')
@click.option('--mode-parameters', type=str, multiple=True, default=[], help='Parameters for the display mode')
def main(offset, time, interval, simulation_update, face_mode, run_mode, show_it_is, light_mode, light_color,
         replace_blanks, blank_character, edge_character, array_format, button_key, baud_rate, show_a, mode, mode_parameters):

    term = blessed.Terminal()
    if time:
        the_time = datetime.datetime.strptime(time, '%H:%M').time()
        absolute_time = datetime.datetime.now().replace(hour=the_time.hour, minute=the_time.minute)
        current_offset = absolute_time - datetime.datetime.now()
    else:
        current_offset = datetime.timedelta(minutes=offset)
    simulation_offset = datetime.timedelta(minutes=simulation_update)

    if light_mode == 'simulate':
        lights = lambda n: mocklights.MockLights(term, n)
    elif light_mode in ('real', 'detect'):
        try:
            from pi5neo import Pi5Neo
        except ImportError:
            lights = None
        else:
            lights = lambda n: Pi5Neo('/dev/spidev0.0', n, baud_rate)
    else:
        lights = None

    display_modes = [modes.modes[name](mode_parameters) for name in mode]

    if light_color.startswith('#'):
        light_color = hex_to_rgb(light_color)

    b = Board(term, datetime.datetime.now(),
              simple=face_mode=='14x5', show_it_is=show_it_is,
              lights=lights, light_color=light_color,
              replace_blanks=replace_blanks, blank_character=blank_character,
              edge_character=edge_character,
              show_a=show_a, display=display_modes
    )

    b.add_words(faces.faces[face_mode])

    def signal_handler(sig, frame):
        """Handle the SIGTERM from SystemD"""
        print(f'Caught SIGTERM {sig}')
        if lights:
            b.lights.clear_strip()
            b.lights.update_strip()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)

    if run_mode == 'CALCSIZE':
        print('\nCalculation of board size ...\n')
        print(f'Board rows = {len(b.rows)}')
        print(f'Lights = {b.total_lights}')
        print('\n\n')
        if not array_format:
            print('\n'.join(b.get_board_text(True)))
        else:
            lines = [term.strip(line) for line in b.get_board_text(True)]
            lines[0] = edge_character * len(lines[0])
            lines[-1] = edge_character * len(lines[-1])
            for idx in range(1, len(lines)):
                lines[idx] = edge_character + lines[idx][1:-1] + edge_character
            print('\n'.join([f'"{line}",' for line in lines]))
    elif run_mode == 'SHOWLETTERS':
        missing = []
        for letter in 'abcdefghijklmnopqrstuvwxyz0123456789':
            found = False
            for row in b.rows:
                for item in row:
                    if letter in item.word:
                        found = True
            if not found:
                missing.append(letter)
        #
        print(f'The following {len(missing)} letters are missing: {", ".join(missing)}\n')
    else:
        updater = Updater(b, current_offset, term, interval, simulation_offset, lights, button_key)
        updater.update()


class UpdateModes(enum.Enum):
    NORMAL = 'normal'
    CONFIG = 'config'


class Updater:
    """A class to manage updating the clcck"""
    
    def __init__(self, board, current_offset, term, interval, simulation_offset, lights, button_key):
        self.mode = UpdateModes.NORMAL
        self.board = board
        self.current_offset = current_offset
        self.term = term
        self.interval = interval
        self.simulation_offset = simulation_offset
        self.lights = lights
        self.button_key = button_key
        self.old_modes = board.modes
        self.config_mode = modes.ConfigMode(None)
        self.config_modes = [self.config_mode, modes.Normal(None)]
        self.last_key_press = time.time()
        self.button_reset_interval = 5

    def update(self):
        last_config_time = os.path.getmtime('config.sh')
        while True:
            try:
                t = datetime.datetime.now()
                self.board.time = t + self.current_offset

                logs = self.board.update_board()
                self.board.show_board(logs)
                with self.term.cbreak():
                    if pressed := self.term.inkey(timeout=self.interval):
                        if pressed == self.button_key:
                            self.button_up()
                        else:
                            break
                self.current_offset += self.simulation_offset
                if time.time() - self.last_key_press > self.button_reset_interval:
                    self.reset_config()
            except KeyboardInterrupt:
                print('CTRL-C detected')
                break
            if os.path.getmtime('config.sh') != last_config_time:
                sys.exit(2)

        if self.lights:
            self.board.lights.clear_strip()
            self.board.lights.update_strip()

    def reset_config(self):
        """Reset back to normal mode"""
        self.mode = UpdateModes.NORMAL
        self.board.modes = self.old_modes
        if self.config_mode.on:
            # If it was on then turn it off to clear the config display
            self.config_mode.color = (0, 0, 0)
            self.config_mode.update(self.board)
            self.config_mode.color = (255, 0, 0)

    def button_up(self):
        """The button was released"""
        self.last_key_press = time.time()
        if self.mode == UpdateModes.NORMAL:
            self.mode = UpdateModes.CONFIG
            self.board.modes = self.config_modes
        else:
            self.current_offset += datetime.timedelta(hours=1)

def hex_to_rgb(hex_color):
    """
    Converts a hex color code (e.g., "#14944c") to a tuple of RGB integers.

    Args:
        hex_color: A string representing the hex color code, including the '#' symbol.

    Returns:
        A tuple of three integers (r, g, b) representing the RGB values,
        or None if the input is invalid.
    """
    if not isinstance(hex_color, str) or not hex_color.startswith('#'):
        return None  # Input must be a string starting with '#'

    hex_color = hex_color[1:]  # Remove the '#'
    if len(hex_color) != 6:
        return None  # Input must be 6 characters long (excluding '#')

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
    except ValueError:
        return None  # Handle cases where the hex string is invalid


if __name__ == '__main__':
    while True:
        result = main(auto_envvar_prefix='CLOCK')
        import pdb; pdb.set_trace()
        if not result:
            print('Closing down clock')
            break
        print('Config changed - restarting')


