"""Some modes of operation of the clock"""

import datetime
import json
import os


class Mode:
    """An abstract mode"""

    def __init__(self, parameters):
        self.parameters = parameters

    def update(self, board):
        """Update the board according to the mode"""

    def set_edge_light_by_index(self, board, index, color=None):
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

class ConfigMode(TestEdge):
    """Shows the phone in config mode"""

    def __init__(self, parameters):
        super().__init__(parameters)
        self.color = (255, 0, 0)


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


class EdgeLightCustom(Mode):
    """A mode of the edge lights that reads the local config file and data"""

    def __init__(self, parameters):
        super().__init__(parameters)
        #
        self.config_data = self.read_config()
        self.frequency = self.config_data['frequency']
        self.last_time = None

    def read_config(self):
        """Read the configuration data"""
        with open('local_config.json', 'r') as f:
            config_data_text = f.read()
        return json.loads(config_data_text)

    def get_data(self):
        """Get the latest data to show"""
        #
        last_update = os.stat('local_data.json').st_mtime
        if self.last_time is None or last_update > self.last_time:
            with open('local_data.json', 'r') as f:
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
            return [
                "Updated data!"
            ]

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


modes = {
    'Normal': Normal,
    'EdgeLightSeconds': EdgeLightSeconds,
    'TestEdge': TestEdge,
    'TestWords': TestWords,
    'FlashWords': FlashWords,
    'EdgeLightRWB': EdgeLightRWB,
    'EdgeLightGW': EdgeLightGW,
    'EdgeLightCustom': EdgeLightCustom,
    'Config': ConfigMode,
}

def get_valid_modes():
    return sorted(list(modes.keys()))