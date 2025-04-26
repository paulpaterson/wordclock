import random
import signal
import sys

import blessed
import datetime
import timesayer
import click
import mocklights


class Word:
    """Represents a single word on the screen"""
    new_line = False
    
    def __init__(self, word, is_on=False):
        self.line = None
        self.word = word
        self.on = is_on

    def clear(self):
        self.on = False

    def activate(self):
        self.on = True

    def show(self, term, terminal_mode=True):
        if self.on:
            return term.red(self.word.upper()) if terminal_mode else self.word.upper()
        else:
            return term.grey(self.word.upper()) if terminal_mode else ' ' * len(self.word)


class NewLine:
    new_line = True
    
    
full_words = [
    Word('It', True),
    Word('l'),
    Word('is', True),
    Word('as'),
    Word('AM'),
    Word('PM'),
    NewLine,

    Word('a'),
    Word('c'),
    Word('quarter'),
    Word('dc'),
    NewLine,

    Word('twenty'),
    Word('five', True),
    Word('x'),
    NewLine,

    Word('half'),
    Word('s'),
    Word('ten'),
    Word('f'),
    Word('to'),
    NewLine,

    Word('past'),
    Word('eru'),
    Word('nine'),
    NewLine,

    Word('one'),
    Word('six'),
    Word('three'),
    NewLine,

    Word('four'),
    Word('five'),
    Word('two'),
    NewLine,

    Word('eight'),
    Word('eleven'),
    NewLine,

    Word('seven'),
    Word('twelve'),
    NewLine,

    Word('ten'),
    Word('s'),
    Word('oclock', True),
    Word('X'),
    #Word('AM'),
    #Word('PM'),
    #Word('YO'),
    NewLine,
]

simple_words = [
    Word('quarter'),
    Word('half'),
    Word('past'),
    NewLine,

    Word('to'),
    Word('x'),
    Word('nine'),
    Word('one'),
    Word('three'),
    NewLine,

    Word('two'),
    Word('eight'),
    Word('five'),
    Word('six'),
    NewLine,

    Word('seven'),
    Word('twelve'),
    Word('four'),
    NewLine,

    Word('eleven'),
    Word('ten'),
    Word('oclock'),
    NewLine,
]

square_words = [
    NewLine,
    NewLine,
    NewLine,
    Word('xx'),

    Word('It', True),
    Word('l'),
    Word('is', True),
    Word('as'),
    Word('AM'),
    Word('y'),
    Word('PM'),

    Word('xx'),
    NewLine,
    Word('xx'),

    Word('a'),
    Word('cy'),
    Word('quarter'),
    Word('dc'),

    Word('xx'),
    NewLine,
    Word('xx'),

    Word('twenty'),
    Word('y'),
    Word('five', True),
    Word('r'),

    Word('xx'),
    NewLine,
    Word('xx'),

    Word('half'),
    Word('sy'),
    Word('ten'),
    Word('f'),
    Word('to'),

    Word('xx'),
    NewLine,
    Word('xx'),

    Word('past'),
    Word('eruy'),
    Word('nine'),

    Word('xx'),
    NewLine,
    Word('xx'),

    Word('one'),
    Word('six'),
    Word('y'),
    Word('three'),

    Word('xx'),
    NewLine,
    Word('xx'),

    Word('four'),
    Word('five'),
    Word('y'),
    Word('two'),

    Word('xx'),
    NewLine,
    Word('xx'),

    Word('eight'),
    Word('y'),
    Word('eleven'),

    Word('xx'),
    NewLine,
    Word('xx'),

    Word('seven'),
    Word('y'),
    Word('twelve'),

    Word('xx'),
    NewLine,
    Word('xx'),

    Word('ten'),
    Word('sy'),
    Word('oclock', True),
    Word('X'),

    Word('xx'),
    NewLine,
    NewLine,
    NewLine,
]

faces = {
    '10x11': full_words,
    '14x5': simple_words,
    '16x16': square_words,
}


class Board:
    """Represents of the words arranged in a board"""

    def __init__(self, term, time, simple=False, show_it_is=False, lights=None, light_color=None,
                 replace_blanks=False, blank_character=' ', show_a=False):
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

    def show_board(self):
        print(self.term.home + self.term.clear)
        text_lines = self.get_board_text(terminal_mode=self.lights is None)
        print('\n'.join(text_lines))
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
        time_string = self.convert_time()
        time_words = time_string.split()
        possible_words = self.get_all_words()
        for word in time_words:
            the_word = self.find_next_word(word, possible_words)
            the_word.activate()

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
@click.option('--mode', type=click.Choice(list(faces.keys())),required=True, help='Select which mode')
@click.option('--calc-size', default=False, is_flag=True, help='Just calculate the size')
@click.option('--show-it-is', default=False, is_flag=True, help='Whether to show "it is" wording')
@click.option('--light-mode', type=click.Choice(['off', 'simulate', 'real']), default='off',
              help='Set how to handle lights')
@click.option('--light-color', type=click.Tuple([click.INT, click.INT, click.INT]), default=(10, 10, 10),
              help='The color for the lights when they are on')
@click.option('--replace-blanks', default=False, is_flag=True, help='Replace blanks in the face with random letters')
@click.option('--blank-character', type=str, default=' ', help='Blank character to use')
@click.option('--array-format', default=False, is_flag=True, help='When showing grid format it as python array')
@click.option('--baud-rate', default=800, type=int, help='Baud rate for SPI communication')
@click.option('--show-a', default=False, is_flag=True, help='Whether to show "a" in "a quarter to ..."')
def main(offset, time, interval, simulation_update, mode, calc_size, show_it_is, light_mode, light_color,
         replace_blanks, blank_character, array_format, baud_rate, show_a):
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
    elif light_mode == 'real':
        from pi5neo import Pi5Neo
        lights = lambda n: Pi5Neo('/dev/spidev0.0', n, baud_rate)
    else:
        lights = None

    b = Board(term, datetime.datetime.now(),
              simple=mode=='14x5', show_it_is=show_it_is,
              lights=lights, light_color=light_color,
              replace_blanks=replace_blanks, blank_character=blank_character,
              show_a=show_a
    )

    b.add_words(faces[mode])

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

        if lights:
            b.lights.clear_strip()
            b.lights.update_strip()




if __name__ == '__main__':
    main()
