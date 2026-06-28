"""Represents the faces of the clock"""
import blessed


class Word:
    """Represents a single word on the screen"""
    new_line = False
    is_used = True

    def __init__(self, word: str, is_on: bool=False) -> None:
        self.line: int|None = None
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


class _NewLine(Word):
    new_line = True
    is_used = False

NewLine = _NewLine('', False)


FaceDefinition = list[Word]

full_words: FaceDefinition = [
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

simple_words: FaceDefinition = [
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

square_words: FaceDefinition = [
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

new_square_words: FaceDefinition = [
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

full_square_words: FaceDefinition = [
    NewLine,
    NewLine,
    NewLine,
    Unused('xx'),

    Unused('j'),
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
    Unused('2'),
    Unused('zero'),

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
    Unused('34'),
    Word('ten'),
    Unused('5'),
    Word('to'),

    Unused('xx'),
    NewLine,
    Unused('xx'),

    Word('past'),
    Unused('e'),
    Word('dot'),
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

short_date: FaceDefinition = [
    NewLine,
    NewLine,
    NewLine,

    Unused('xx'),
    Word('Mon'),
    Word('Tue'),
    Word('Wed'),
    Word('Thu'),
    Unused('xx'),
    NewLine,

    Unused('xx'),
    Word('Fri'),
    Word('Sat'),
    Word('Sun'),
    Unused('k'),
    Word('1'),
    Word('2'),
    Unused('xx'),
    NewLine,

    Unused('xx'),
    Word('3'),
    Word('4'),
    Word('5'),
    Word('6'),
    Word('7'),
    Word('8'),
    Word('9'),
    Word('10'),
    Word('11'),
    Unused('k'),
    Unused('xx'),
    NewLine,

    Unused('xx'),
    Word('12'),
    Word('13'),
    Word('14'),
    Word('15'),
    Word('16'),
    Word('17'),
    Unused('xx'),
    NewLine,

    Unused('xx'),
    Word('18'),
    Word('19'),
    Word('20'),
    Word('21'),
    Word('22'),
    Word('23'),
    Unused('xx'),
    NewLine,

    Unused('xx'),
    Word('24'),
    Word('25'),
    Word('26'),

    Word('27'),
    Word('28'),
    Word('29'),
    Unused('xx'),
    NewLine,

    Unused('xx'),
    Word('30'),
    Word('31'),
    Unused('k'),
    Word('Jan'),
    Word('Feb'),
    Unused('k'),
    Unused('xx'),
    NewLine,

    Unused('xx'),
    Word('Mar'),
    Word('Apr'),
    Word('May'),
    Word('Jun'),
    Unused('xx'),
    NewLine,

    Unused('xx'),
    Word('Jul'),
    Word('Aug'),
    Word('Sep'),
    Word('Oct'),
    Unused('xx'),
    NewLine,

    Unused('xx'),
    Word('Nov'),
    Word('Dec'),
    Unused('kfghab'),
    Unused('xx'),
    NewLine,

    NewLine,
    NewLine,
    NewLine,
    NewLine,
]

faces: dict[str, FaceDefinition] = {
    '10x11': full_words,
    '14x5': simple_words,
    '16x16': square_words,
    '16x16new': new_square_words,
    '16x16full': full_square_words,
    'date': short_date,
}

def get_valid_faces() -> list[str]:
    """Return the valid face types"""
    return list(sorted(faces.keys()))

