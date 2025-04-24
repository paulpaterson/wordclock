"""Mock interface for lights to allow testing"""

import time
import blessed


class MockLEDColor:
    """Represents an RGB color for the NeoPixels"""
    def __init__(self, red=0, green=0, blue=0):
        self.red = red
        self.green = green
        self.blue = blue

    def is_set(self):
        return not(self.red == 0 and self.green == 0 and self.blue == 0)


class MockLights:

    def __init__(self, spi_device, num_leds, spi_speed_khz=800):
        self.spi_device = blessed.Terminal()
        self.num_leds = num_leds
        self.temp_state = [MockLEDColor()] * num_leds
        self.led_state = None

    def clear_strip(self):
        self.fill_strip(0, 0, 0)

    def fill_strip(self, red=0, green=0, blue=0):
        color = MockLEDColor(red, green, blue)
        self.temp_state = [color] * self.num_leds

    def set_led_color(self, index, red, green, blue):
        if 0 <= index < self.num_leds:
            self.temp_state[index] = MockLEDColor(red, green, blue)
            return True
        return False

    def update_strip(self, sleep_duration=0.1):
        self.led_state = self.temp_state[:]
        print(self.spi_device.green('Lights on: '), end='')
        for idx, color in enumerate(self.led_state):
            if self.led_state[idx].is_set():
                print(self.spi_device.green(str(idx)), end=' ')
        print()
        time.sleep(sleep_duration)

