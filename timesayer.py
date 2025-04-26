import datetime
import enum


class Mode(enum.Enum):
    simple = 0
    am_pm = 1
    oclock = 2

class TwelveMode(enum.Enum):
    number = 0
    name = 1


class TargetTime:
    def __init__(self, mins: int, format: str) -> None:
        self.mins = mins
        self.format = format

    def get_text(self, hour_name: str, next_hour_name: str, am_pm: str, show_a: bool = False) -> str:
        a = 'a ' if show_a else ''
        text = self.format.format(hour_name=hour_name, next_hour_name=next_hour_name, am_pm=am_pm, a=a)
        if 'midnight' in text or 'noon' in text:
            # Strip out AM/PM indicator for noon and midnight
            return self.format.format(hour_name=hour_name, next_hour_name=next_hour_name, am_pm='', a=a)
        else:
            return text

    def get_hour_offset(self) -> int:
        if 'next_hour_name' in self.format:
            return +1
        else:
            return 0


simple_times = [
    TargetTime(0, '{hour_name}{am_pm}'),
    TargetTime(15, '{a}quarter past {hour_name}'),
    TargetTime(30, 'half past {hour_name}'),
    TargetTime(45, '{a}quarter to {next_hour_name}'),
    TargetTime(60, '{next_hour_name}{am_pm}'),
]

complex_times = simple_times + [
    TargetTime(5, 'five past {hour_name}'),
    TargetTime(10, 'ten past {hour_name}'),
    TargetTime(20, 'twenty past {hour_name}'),
    TargetTime(25, 'twenty five past {hour_name}'),
    TargetTime(35, 'twenty five to {next_hour_name}'),
    TargetTime(40, 'twenty to {next_hour_name}'),
    TargetTime(50, 'ten to {next_hour_name}'),
    TargetTime(55, 'five to {next_hour_name}'),
]


def convert_to_text(t: datetime.time, simple: bool = False,
                    mode: Mode = Mode.am_pm, twelve_mode: TwelveMode = TwelveMode.name,
                    show_a=False) -> str:
    """Return a text representation of the time"""
    hour_words = [
        'midnight' if twelve_mode == TwelveMode.name else 'twelve',
        'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
        'nine', 'ten', 'eleven',
        'noon' if twelve_mode == TwelveMode.name else 'twelve',
        'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
        'nine', 'ten', 'eleven'
    ]

    hour = hour_words[t.hour]
    next_hour = hour_words[(t.hour + 1) % 24]

    options = simple_times if simple else complex_times
    options_scored = sorted(options, key=lambda o: abs(t.minute - o.mins))
    best_option = options_scored[0]

    if mode == Mode.simple:
        am_pm = ''
    elif mode == Mode.oclock:
        am_pm = ' oclock'
    else:
        actual_reported_hour = t.hour + best_option.get_hour_offset()
        match actual_reported_hour:
            case h if h < 12 or h > 23:
                am_pm = ' AM'
            case _:
                am_pm = ' PM'

    return best_option.get_text(hour, next_hour, am_pm, show_a)



