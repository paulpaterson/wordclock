import unittest
import timesayer
import datetime

hour_words = [
    'midnight', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
    'nine', 'ten', 'eleven', 'noon',
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
    'nine', 'ten', 'eleven',

]

class TestSayer(unittest.TestCase):

    def test_on_the_hour(self):
        for hour in range(0, 24):
            t = datetime.time(hour)
            s = timesayer.convert_to_text(t)
            hour_name = hour_words[hour]
            am_pm = '' if (hour_name == 'midnight' or hour_name == 'noon') else ' AM' if hour < 12 else ' PM'
            self.assertEqual(e := f'{hour_name}{am_pm}', s,
                             f'Failed on {t}, expected {e}, got {s}')

    def test_on_the_half_hour(self):
        for minute in range(28, 33):
            t = datetime.time(5, minute)
            s = timesayer.convert_to_text(t)
            self.assertEqual(e :='half past five', s,
                             f'Failed on {t}, expected {e}, got {s}')

    def test_quarter_past(self):
        for minute in range(13, 18):
            t = datetime.time(5, minute)
            s = timesayer.convert_to_text(t)
            self.assertEqual(e := 'quarter past five', s,
                             f'Failed on {t}, expected {e}, got {s}')

    def test_quarter_to(self):
        for minute in range(43, 48):
            t = datetime.time(5, minute)
            s = timesayer.convert_to_text(t)
            self.assertEqual(e := 'quarter to six', s,
                             f'Failed on {t}, expected {e}, got {s}')

    def test_all_times(self):
        for hour in range(0, 24):
            for minute in range(0, 60):
                t = datetime.time(hour, minute)
                s = timesayer.convert_to_text(t)
                print(f'{t} -> {s}')

    def test_partials(self):
        T = datetime.time
        time_expect = [
            (T(5, 2), 'five AM'),
            (T(5, 3), 'five past five'),
            (T(5, 7), 'five past five'),
            (T(5, 8), 'ten past five'),
            (T(5, 12), 'ten past five'),
            (T(5, 13), 'quarter past five'),
            (T(5, 17), 'quarter past five'),
            (T(5, 18), 'twenty past five'),
            (T(5, 22), 'twenty past five'),
            (T(5, 23), 'twenty five past five'),
            (T(5, 27), 'twenty five past five'),
            (T(5, 28), 'half past five'),
            (T(5, 32), 'half past five'),
            (T(5, 33), 'twenty five to six'),
            (T(5, 37), 'twenty five to six'),
            (T(5, 38), 'twenty to six'),
            (T(5, 42), 'twenty to six'),
            (T(5, 43), 'quarter to six'),
            (T(5, 47), 'quarter to six'),
            (T(5, 48), 'ten to six'),
            (T(5, 52), 'ten to six'),
            (T(5, 53), 'five to six'),
            (T(5, 57), 'five to six'),
            (T(5, 58), 'six AM'),
        ]
        for t, expected in time_expect:
            s = timesayer.convert_to_text(t)
            self.assertEqual(expected, s,
                             f'Failed on {t}, expected {expected}, got {s}')

    def test_partials_adding_a(self):
        T = datetime.time
        time_expect = [
            (T(5, 2), 'five AM'),
            (T(5, 3), 'five past five'),
            (T(5, 7), 'five past five'),
            (T(5, 8), 'ten past five'),
            (T(5, 12), 'ten past five'),
            (T(5, 13), 'a quarter past five'),
            (T(5, 17), 'a quarter past five'),
            (T(5, 18), 'twenty past five'),
            (T(5, 22), 'twenty past five'),
            (T(5, 23), 'twenty five past five'),
            (T(5, 27), 'twenty five past five'),
            (T(5, 28), 'half past five'),
            (T(5, 32), 'half past five'),
            (T(5, 33), 'twenty five to six'),
            (T(5, 37), 'twenty five to six'),
            (T(5, 38), 'twenty to six'),
            (T(5, 42), 'twenty to six'),
            (T(5, 43), 'a quarter to six'),
            (T(5, 47), 'a quarter to six'),
            (T(5, 48), 'ten to six'),
            (T(5, 52), 'ten to six'),
            (T(5, 53), 'five to six'),
            (T(5, 57), 'five to six'),
            (T(5, 58), 'six AM'),
        ]
        for t, expected in time_expect:
            s = timesayer.convert_to_text(t, show_a=True)
            self.assertEqual(expected, s,
                             f'Failed on {t}, expected {expected}, got {s}')

    def test_partials_lower_granularity(self):
        T = datetime.time
        time_expect = [
            (T(5, 2), 'five AM'),
            (T(5, 3), 'five AM'),
            (T(5, 7), 'five AM'),
            (T(5, 8), 'quarter past five'),
            (T(5, 12), 'quarter past five'),
            (T(5, 13), 'quarter past five'),
            (T(5, 17), 'quarter past five'),
            (T(5, 18), 'quarter past five'),
            (T(5, 22), 'quarter past five'),
            (T(5, 23), 'half past five'),
            (T(5, 27), 'half past five'),
            (T(5, 28), 'half past five'),
            (T(5, 32), 'half past five'),
            (T(5, 33), 'half past five'),
            (T(5, 37), 'half past five'),
            (T(5, 38), 'quarter to six'),
            (T(5, 42), 'quarter to six'),
            (T(5, 43), 'quarter to six'),
            (T(5, 47), 'quarter to six'),
            (T(5, 48), 'quarter to six'),
            (T(5, 52), 'quarter to six'),
            (T(5, 53), 'six AM'),
            (T(5, 57), 'six AM'),
            (T(5, 58), 'six AM'),
        ]
        for t, expected in time_expect:
            s = timesayer.convert_to_text(t, simple=True)
            self.assertEqual(expected, s,
                             f'Failed on {t}, expected {expected}, got {s}')

    def test_hour_mode(self):
        self.assertEqual(
            'five AM',
            timesayer.convert_to_text(datetime.time(5,0))
        )
        self.assertEqual(
            'five oclock',
            timesayer.convert_to_text(datetime.time(5,0),
            mode=timesayer.Mode.oclock
        ))
        self.assertEqual(
            'five AM',
            timesayer.convert_to_text(datetime.time(5,0),
            mode=timesayer.Mode.am_pm
        ))
        self.assertEqual(
            'five',
            timesayer.convert_to_text(datetime.time(5,0),
            mode=timesayer.Mode.simple
        ))

    def test_mid_mode(self):
        self.assertEqual(
            'noon',
            timesayer.convert_to_text(datetime.time(12,0))
        )
        self.assertEqual(
            'midnight',
            timesayer.convert_to_text(datetime.time(23,59))
        )
        self.assertEqual(
            'noon',
            timesayer.convert_to_text(datetime.time(12,0),
            twelve_mode=timesayer.TwelveMode.name,
        ))
        self.assertEqual(
            'midnight',
            timesayer.convert_to_text(datetime.time(23,59),
            twelve_mode=timesayer.TwelveMode.name,
        ))
        self.assertEqual(
            'twelve PM',
            timesayer.convert_to_text(datetime.time(12,0),
            twelve_mode=timesayer.TwelveMode.number,
        ))
        self.assertEqual(
            'twelve AM',
            timesayer.convert_to_text(datetime.time(23,59),
            twelve_mode=timesayer.TwelveMode.number,
        ))

if __name__ == '__main__':
    unittest.main()
