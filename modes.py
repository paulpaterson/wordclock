"""Some modes of operation of the clock"""

import datetime


class Mode:
    """An abstract mode"""

    def __init__(self, parameters):
        self.parameters = parameters

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

    def __init__(self, parameters):
        super().__init__(parameters)
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


class TestWords(Mode):
    """Test all the words lighting up"""

    def __init__(self, parameters):
        super().__init__(parameters)
        self.idx = None

    def update(self, board):
        """Update each word"""
        possible_words = [word for word in board.get_all_words() if word.is_used]
        if self.idx is None:
            self.idx = -1
        else:
            possible_words[self.idx].clear()

        self.idx += 1
        if self.idx >= len(possible_words):
            self.idx = 0
        possible_words[self.idx].activate()


class FlashWords(Mode):
    """Alternately flash all the words"""

    def __init__(self, parameters):
        super().__init__(parameters)
        self.on = True

    def update(self, board):
        """Update each word"""
        possible_words = [word for word in board.get_all_words() if word.is_used]
        if self.parameters:
            possible_words = [word for word in possible_words if word.word.lower() in self.parameters]

        for word in possible_words:
            if self.on:
                word.activate()
            else:
                word.clear()
        self.on = not self.on


modes = {
    'Normal': Normal,
    'EdgeSeconds': EdgeLightSeconds,
    'TestEdge': TestEdge,
    'TestWords': TestWords,
    'FlashWords': FlashWords,
}
