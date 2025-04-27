"""Some modes of operation of the clock"""

import datetime


class Mode:
    """An abstract mode"""

    def update(self, board):
        """Update the board according to the mode"""


class Normal(Mode):
    """Show the time"""

    def update(self, board):
        """Update the board to show the current time"""
        time_string = board.convert_time()
        time_words = time_string.split()
        possible_words = board.get_all_words()
        for word in time_words:
            the_word = board.find_next_word(word, possible_words)
            the_word.activate()


class EdgeLightSeconds(Mode):
    """Show the number of seconds using the edge light"""

    def update(self, board):
        """Update the edge lights"""

        board.edge_lights = {}
        s = datetime.datetime.now().second
        if s < 16:
            row, col = 0, s
        elif s < 16 + 15:
            row, col = s - 16, 15
        elif s < 16 + 15 + 16:
            row, col = 15, 15 - (s - 16 - 15)
        else:
            row, col = 61 - s, 0
        board.edge_lights[(row, col)] = True


modes = {
    'Normal': Normal(),
    'EdgeSeconds': EdgeLightSeconds(),
}
