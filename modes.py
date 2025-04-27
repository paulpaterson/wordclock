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


class TestEdge(Mode):
    """Test all the edge lights"""

    def __init__(self):
        self.on = True

    def update(self, board):
        """Update the edge lights"""
        board.edge_lights = {}
        rows, cols = board.get_dimensions()
        for row in range(rows):
            board.edge_lights[(row, 0)] = self.on
            board.edge_lights[(row, cols - 1)] = self.on
        for col in range(cols):
            board.edge_lights[(0, col)] = self.on
            board.edge_lights[(rows - 1, col)] = self.on

        self.on = not self.on



modes = {
    'Normal': Normal(),
    'EdgeSeconds': EdgeLightSeconds(),
    'TestEdge': TestEdge(),
}
