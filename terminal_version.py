import random
import signal
import sys
import os

import blessed
import datetime
import timesayer
import click
import mocklights
import faces
import modes


class Board:
    """Represents of the words arranged in a board"""

    def __init__(self, term, time, simple=False, show_it_is=False, lights=None, light_color=None,
                 replace_blanks=False, blank_character=' ', show_a=False, display=None):
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
        self.replace_blanks = replace_blanks
        self.show_a = show_a
        self.edge_lights = {}
        self.modes = display or [modes.Normal()]

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
        for row in self.rows:
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

    def show_board(self):
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
                        self.lights.set_led_color(idx, *edge_color)

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
        for mode in self.modes:
            mode.update(self)

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
@click.option('--face-mode', type=click.Choice(list(faces.faces.keys())), required=True, help='Select which face mode')
@click.option('--calc-size', default=False, is_flag=True, help='Just calculate the size')
@click.option('--show-it-is', default=False, is_flag=True, help='Whether to show "it is" wording')
@click.option('--light-mode', type=click.Choice(['off', 'simulate', 'real', 'detect']), default='off',
              help='Set how to handle lights')
@click.option('--light-color', type=str, default="#0A0A0A",
              help='The color for the lights when they are on')
@click.option('--replace-blanks', default=False, is_flag=True, help='Replace blanks in the face with random letters')
@click.option('--blank-character', type=str, default=' ', help='Blank character to use')
@click.option('--array-format', default=False, is_flag=True, help='When showing grid format it as python array')
@click.option('--baud-rate', default=800, type=int, help='Baud rate for SPI communication')
@click.option('--show-a', default=False, is_flag=True, help='Whether to show "a" in "a quarter to ..."')
@click.option('--mode', type=click.Choice(modes.modes.keys()),
              multiple=True, default=['Normal'], help='Select which display modes to use, can have multiple')
@click.option('--mode-parameters', type=str, multiple=True, default=[], help='Parameters for the display mode')
def main(offset, time, interval, simulation_update, face_mode, calc_size, show_it_is, light_mode, light_color,
         replace_blanks, blank_character, array_format, baud_rate, show_a, mode, mode_parameters):

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

    if calc_size:
        print('\nCalculation of board size ...\n')
        print(f'Board rows = {len(b.rows)}')
        print(f'Lights = {b.total_lights}')
        print('\n\n')
        if not array_format:
            print('\n'.join(b.get_board_text(True)))
        else:
            print('\n'.join([f'"{line}",' for line in b.get_board_text(True)]))
    else:
        last_config_time = os.path.getmtime('config.sh')
        while True:
            try:
                t = datetime.datetime.now()
                b.time = t + current_offset

                b.update_board()
                b.show_board()
                if term.inkey(timeout=interval):
                    break
                current_offset += simulation_offset
            except KeyboardInterrupt:
                print('CTRL-C detected')
                break
            if os.path.getmtime('config.sh') != last_config_time:
                sys.exit(2)

        if lights:
            b.lights.clear_strip()
            b.lights.update_strip()


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


