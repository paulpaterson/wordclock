"""Represents the faces of the clock"""


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
    # Word('AM'),
    # Word('PM'),
    # Word('YO'),
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

    Word('y'),
    Word('a'),
    Word('c'),
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