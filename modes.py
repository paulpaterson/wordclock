"""Some modes of operation of the clock"""

import datetime
import asyncio
import ssl
import aiohttp
from omnilogic import OmniLogic


class Mode:
    """An abstract mode"""

    def __init__(self, parameters):
        self.parameters = parameters

    def update(self, board):
        """Update the board according to the mode"""

    def set_edge_light_by_index(self, board, index, color):
        if index < 16:
            row, col = 0, index
        elif index < 16 + 15:
            row, col = index - 16 + 1, 15
        elif index < 16 + 15 + 15:
            row, col = 15, 15 - (index - 16 - 15) - 1
        else:
            row, col = 60 - index, 0
        board.edge_lights[(row, col)] = color


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
        self.set_edge_light_by_index(board, s, (255, 255, 255))


class EdgeLightColor(Mode):
    """Set the edge lights to be red, white and blue"""

    colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
    ]

    def __init__(self, parameters):
        super().__init__(parameters)
        self.offset = 0

    def update(self, board):
        """Update the edge lights"""
        board.edge_lights = {}
        for idx in range(61):
            color = self.colors[(self.offset + idx) % len(self.colors)]
            self.set_edge_light_by_index(board, idx, color)
        self.offset += 1


class EdgeLightRWB(EdgeLightColor):
    colors = [
        (255, 0, 0),
        (255, 255, 255),
        (0, 0, 255),
    ]

class EdgeLightGW(EdgeLightColor):
    colors = [
        (255, 255, 255),
        (0, 255, 0),
    ]


class TestEdge(Mode):
    """Test all the edge lights"""

    def __init__(self, parameters):
        super().__init__(parameters)
        self.on = True
        self.color = (255, 255, 255)

    def update(self, board):
        """Update the edge lights"""
        board.edge_lights = {}
        rows, cols = board.get_dimensions()
        if self.on:
            for row in range(rows):
                board.edge_lights[(row, 0)] = self.color
                board.edge_lights[(row, cols - 1)] = self.color
            for col in range(cols):
                board.edge_lights[(0, col)] = self.color
                board.edge_lights[(rows - 1, col)] = self.color

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


async def get_pool_data(store):
    """Get data on the pool telemetry"""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    conn = aiohttp.TCPConnector(ssl_context=ssl_context)

    with open("../haywardlogin.py", "r") as f:
        text = f.read()
        vals = eval(text)
        username = vals['username']
        password = vals['password']

    omni = OmniLogic(username, password, aiohttp.ClientSession(connector=conn))
    status = await omni.get_telemetry_data()
    store.status = status


class EdgeLightPool(Mode):
    """Set the edge lights to be based on the pool air and water temp"""

    def __init__(self, parameters):
        super().__init__(parameters)
        self.target_air = 80
        self.target_pool = 85
        self.frequency = 10 * 60.0
        self.min = 70
        self.max = 86
        self.next_time = datetime.datetime.now()
        self.status = None

    def update(self, board):
        """Update the edge lights"""
        if datetime.datetime.now() >= self.next_time:
            asyncio.run(get_pool_data(self))
            self.next_time += datetime.timedelta(seconds=self.frequency)
        #
        if self.status:
            water = float(self.status[0]['BOWS'][0]['waterTemp'])
            air = float(self.status[0]['airTemp'])
            water_frac = float(water - self.min) / (self.max - self.min) * 16.0
            air_frac = float(air - self.min) / (self.max - self.min) * 16.0
            print(f'Got air {air} and water {water} and {air_frac}, {water_frac}')
            #
            water_colour = (0, 255, 0) if water > self.target_pool else (255, 0, 0)
            air_colour = (0, 255, 0) if air > self.target_air else (255, 0, 0)
            #
            for i in range(16):
                if i < water_frac:
                    board.edge_lights[(0, i)] = water_colour
                else:
                    board.edge_lights[(0, i)] = None
                if i < air_frac:
                    board.edge_lights[(15, i)] = air_colour
                else:
                    board.edge_lights[(15, i)] = None


modes = {
    'Normal': Normal,
    'EdgeLightSeconds': EdgeLightSeconds,
    'TestEdge': TestEdge,
    'TestWords': TestWords,
    'FlashWords': FlashWords,
    'EdgeLightRWB': EdgeLightRWB,
    'EdgeLightGW': EdgeLightGW,
    'EdgeLightPool': EdgeLightPool,
}
