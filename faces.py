"""Represents the faces of the clock"""


class Word:
    """Represents a single word on the screen"""
    new_line = False
    is_used = True

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


class Unused(Word):
    is_used = False


class NewLine:
    new_line = True
    is_used = False



full_words = [
    Word('It', True),
    Unused('l'),
    Word('is', True),
    Unused('as'),
    Word('AM'),
    Word('PM'),
    NewLine,

    Unused('a'),
    Unused('c'),
    Word('quarter'),
    Unused('dc'),
    NewLine,

    Word('twenty'),
    Word('five', True),
    Unused('x'),
    NewLine,

    Word('half'),
    Unused('s'),
    Word('ten'),
    Unused('f'),
    Word('to'),
    NewLine,

    Word('past'),
    Unused('eru'),
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
    Unused('s'),
    Word('oclock', True),
    Unused('X'),
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
    Unused('x'),
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
    Unused('xx'),

    Word('It', True),
    Unused('l'),
    Word('is', True),
    Unused('as'),
    Word('AM'),
    Unused('y'),
    Word('PM'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Unused('y'),
    Word('a'),
    Unused('c'),
    Word('quarter'),
    Unused('dc'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('twenty'),
    Unused('y'),
    Word('five', True),
    Unused('r'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('half'),
    Unused('sy'),
    Word('ten'),
    Unused('f'),
    Word('to'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('past'),
    Unused('eruy'),
    Word('nine'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('one'),
    Word('six'),
    Unused('y'),
    Word('three'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('four'),
    Word('five'),
    Unused('y'),
    Word('two'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('eight'),
    Unused('y'),
    Word('eleven'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('seven'),
    Unused('y'),
    Word('twelve'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('ten'),
    Unused('sy'),
    Word('oclock', True),
    Unused('X'),

    Unused('xx'),
    NewLine,
    NewLine,
    NewLine,
]

faces = {
    '10x11': full_words,
    '14x5': simple_words,
    '16x16': square_words,
}