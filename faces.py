"""Represents the faces of the clock"""
import blessed


class Word:
    """Represents a single word on the screen"""
    new_line = False
    is_used = True

    def __init__(self, word: str, is_on: bool=False) -> None:
        self.line = None
        self.word = word
        self.on = is_on

    def clear(self) -> None:
        self.on = False

    def activate(self) -> None:
        self.on = True

    def show(self, term: blessed.Terminal, terminal_mode: bool=True) -> str:
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

new_square_words = [
    NewLine,
    NewLine,
    NewLine,
    Unused('xx'),

    Unused('s'),
    Word('It', True),
    Unused('l'),
    Word('is', True),
    Unused('y'),
    Word('AM'),
    Word('a'),
    Word('PM'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('quarter'),
    Unused('yac'),
    Unused('dc'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Unused('r'),
    Word('twenty'),
    Unused('y'),
    Word('five', True),

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

full_square_words = [
    NewLine,
    NewLine,
    NewLine,
    Unused('xx'),

    Unused('s'),
    Word('It', True),
    Unused('0'),
    Word('is', True),
    Unused('1'),
    Word('AM'),
    Word('a'),
    Word('PM'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('quarter'),
    Unused('y2c'),
    Unused('d3'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Unused('r'),
    Word('twenty'),
    Unused('y'),
    Word('five', True),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('half'),
    Unused('s4'),
    Word('ten'),
    Unused('5'),
    Word('to'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('past'),
    Unused('ejuy'),
    Word('nine'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('one'),
    Word('six'),
    Unused('6'),
    Word('three'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('four'),
    Word('five'),
    Unused('7'),
    Word('two'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('eight'),
    Unused('8'),
    Word('eleven'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('seven'),
    Unused('z'),
    Word('twelve'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('ten'),
    Unused('9m'),
    Word('oclock', True),
    Unused('b'),

    Unused('xx'),
    NewLine,
    NewLine,
    NewLine,
]

faces = {
    '10x11': full_words,
    '14x5': simple_words,
    '16x16': square_words,
    '16x16new': new_square_words,
    '16x16full': full_square_words,
}

def get_valid_faces() -> list[str]:
    """Return the valid face types"""
    return list(sorted(faces.keys()))

