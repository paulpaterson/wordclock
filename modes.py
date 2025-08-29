"""Some modes of operation of the clock"""

import datetime
import enum
import json
import os
import subprocess
from collections import namedtuple
from typing import Any


class FaceModeType(enum.Enum):
    FACE = 0
    EDGE = 1
    BOTH = 2
    TEST = 3


# Get IP Address
result = subprocess.run(['./scripts/getip.sh'], capture_output=True)
IP_ADDRESS = result.stdout.decode('utf-8').strip()


class Mode:
    """An abstract mode"""

    type = FaceModeType.FACE
    include_as_dynamic = False

    def __init__(self, parameters: list[str]|None) -> None:
        self.parameters = parameters

    def update(self, board) -> list[str]:
        """Update the board according to the mode"""
        return []

    def set_edge_light_by_index(self, board, index, color=None) -> None:
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

    def update(self, board) -> list[str]:
        """Update the board to show the current time"""
        time_string = board.convert_time()
        time_words = time_string.split()
        possible_words = board.get_all_words()
        for word in time_words:
            the_word = board.find_next_word(word, possible_words)
            the_word.activate()
        return []


class ShowIPAddress(Mode):
    """Show the current IP address by flashing the numbers one by one"""

    words = [
        '0', 'one', 'two', 'three', 'four', 'five',
        'six', 'seven', 'eight', 'nine', 'ten',
    ]
    include_as_dynamic = True

    def __init__(self, parameters):
        """Initialise the mode"""
        super().__init__(parameters)
        self.character_idx = -1
        self.ip_address = IP_ADDRESS
        self.edge_mode = ConfigMode(None)
        self.edge_mode.color = (100, 100, 255)

    def update(self, board):
        """Update the board to show the IP address"""
        #
        # Get the index of the next character to display
        stripped_ip = self.ip_address.replace('.', '..') + '..'
        if self.character_idx >= len(stripped_ip):
            self.character_idx = -1
        #
        # Find all words in the face
        possible_words = board.get_all_words()
        #
        if self.character_idx == -1:
            # Start of the IP address
            board.find_next_word('IT', possible_words).activate()
            board.find_next_word('IS', possible_words).activate()
        else:
            # Showing the IP address
            current_character = stripped_ip[self.character_idx]
            if current_character != '.':
                word = self.words[int(current_character)]
            else:
                word = 's'
             #
            the_word = board.find_next_word(word, possible_words)
            the_word.activate()
             #
        self.character_idx += 1
        self.edge_mode.update(board)


class EdgeLightSeconds(Mode):
    """Show the number of seconds using the edge light"""

    type = FaceModeType.EDGE
    include_as_dynamic = True

    def update(self, board):
        """Update the edge lights"""

        board.edge_lights = {}
        s = datetime.datetime.now().second
        self.set_edge_light_by_index(board, s, (255, 255, 255))


class EdgeLightColor(Mode):
    """Set the edge lights to be red, white and blue"""

    type = FaceModeType.EDGE

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

class EdgeLightBlank(EdgeLightColor):
    """No lights on the edge"""

    colors = [
        (0, 0, 0)
    ]
    include_as_dynamic = True


class EdgeLightRWB(EdgeLightColor):
    colors = [
        (255, 0, 0),
        (255, 255, 255),
        (0, 0, 255),
    ]
    include_as_dynamic = True

class EdgeLightGW(EdgeLightColor):
    colors = [
        (255, 255, 255),
        (0, 255, 0),
    ]
    include_as_dynamic = True




class TestEdge(Mode):
    """Test all the edge lights"""

    color = (255, 255, 255)
    toggle = True
    type = FaceModeType.TEST

    def __init__(self, parameters):
        super().__init__(parameters)
        self.on = True
        self.top = self.right = self.bottom = self.left = True

    def update(self, board):
        """Update the edge lights"""
        board.edge_lights = {}
        rows, cols = board.get_dimensions()
        if self.on:
            for row in range(rows):
                if self.left:
                    board.edge_lights[(row, 0)] = self.color
                if self.right:
                    board.edge_lights[(row, cols - 1)] = self.color
            for col in range(cols):
                if self.top:
                    board.edge_lights[(0, col)] = self.color
                if self.bottom:
                    board.edge_lights[(rows - 1, col)] = self.color

        if self.toggle:
            self.on = not self.on

class ConfigMode(TestEdge):
    """Shows the phone in config mode"""

    color = (255, 0, 0)
    toggle = False


class TestWords(Mode):
    """Test all the words lighting up"""

    type = FaceModeType.TEST

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

    type = FaceModeType.TEST

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


class EdgeLightCustom(Mode):
    """A mode of the edge lights that reads the local config file and data"""

    type = FaceModeType.EDGE
    include_as_dynamic = True

    def __init__(self, parameters):
        super().__init__(parameters)
        #
        self.config_data = self.read_config()
        self.frequency = self.config_data['frequency']
        self.last_time = None
        self.last_data = None

    def read_config(self):
        """Read the configuration data"""
        with open('config/local_config.json', 'r') as f:
            config_data_text = f.read()
        return json.loads(config_data_text)

    def get_data(self):
        """Get the latest data to show"""
        #
        last_update = os.stat('config/local_data.json').st_mtime
        if self.last_time is None or last_update > self.last_time:
            with open('config/local_data.json', 'r') as f:
                data_text = f.read()
            try:
                data = json.loads(data_text)
            except json.decoder.JSONDecodeError:
                # Oops, something went wrong
                data = None
            self.last_time = last_update
            return data
        else:
            return None

    def update(self, board):
        """Update the display"""
        data = self.get_data()
        if data:
            self.update_display(board, data)
            self.last_data = data
            return [
                "Updated data!"
            ]
        elif self.last_data:
            self.update_display(board, self.last_data)
            return []

    def update_display(self, board, data):
        """Actually update the lights"""
        self.config_data = self.read_config()
        for item in self.config_data['items']:
            match t := item['type']:
                case 'bar':
                    self.show_bar(board, item, data)
                case 'boolean':
                    self.show_boolean(board, item, data)
                case 'text':
                    self.show_text(board, item, data)
                case _:
                    raise ValueError(f'Unknown type {t}')

    def show_bar(self, board, item, data):
        """Show lights as a bar"""
        light_start = item['light-start']
        light_end = item['light-end']
        value = data.get(item['variable'])
        ranges = item['ranges']
        reverse_it = item['reversed']
        last_color = color = (0, 0, 0)
        val_min, val_max = 0, 1
        for value_range in ranges:
            val_min = value_range['min']
            val_max = value_range['max']
            color = value_range['color']
            if val_min <= value <= val_max:
                break
            else:
                last_color = color
        #
        fraction = (value - val_min) / (val_max - val_min)
        num_lights = light_end - light_start + 1
        for idx in range(num_lights):
            light_frac = float(idx) / (num_lights - 1)
            if not reverse_it:
                light_num = idx
            else:
                light_num = num_lights - idx - 1
            #
            if fraction >= light_frac:
                self.set_edge_light_by_index(board, light_num + light_start, color)
            else:
                self.set_edge_light_by_index(board, light_num + light_start, last_color)

    def show_boolean(self, board, item, data):
        """Show lights as a bar"""
        light_start = item['light-start']
        light_end = item['light-end']
        value = data.get(item['variable'])
        on_color = item['on-color']
        off_color = item['off-color']
        #
        for idx in range(light_start, light_end + 1):
            color = on_color if value else off_color
            self.set_edge_light_by_index(board, idx, color)

    def show_text(self, board, item, data):
        """Show lights as a text mapping"""
        variable = item['variable']
        light_start = item['light-start']
        light_end = item['light-end']
        reversed = item.get('reversed', False)
        colors = item['colors']
        num_lights = light_end - light_start + 1
        for idx, text in zip(range(num_lights), data[variable]):
            if not reversed:
                light_num = idx
            else:
                light_num = num_lights - idx - 1
            color = colors.get(text, (0, 0, 0))
            self.set_edge_light_by_index(board, light_num + light_start, color)


modes: dict[str, type[Mode]] = {
    'Normal': Normal,
    'EdgeLightBlank': EdgeLightBlank,
    'EdgeLightSeconds': EdgeLightSeconds,
    'TestEdge': TestEdge,
    'TestWords': TestWords,
    'FlashWords': FlashWords,
    'EdgeLightRWB': EdgeLightRWB,
    'EdgeLightGW': EdgeLightGW,
    'EdgeLightCustom': EdgeLightCustom,
    'Config': ConfigMode,
    'ShowIPAddress': ShowIPAddress,
}

def get_valid_modes() -> list[str]:
    return sorted(list(modes.keys()))
