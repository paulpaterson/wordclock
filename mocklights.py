"""Mock interface for lights to allow testing"""

import time
import blessed


class MockLEDColor:
    """Represents an RGB color for the NeoPixels"""
    def __init__(self, red: int=0, green: int=0, blue: int=0) -> None:
        self.red = red
        self.green = green
        self.blue = blue

    def is_set(self) -> bool:
        return not(self.red == 0 and self.green == 0 and self.blue == 0)


class MockLights:

    def __init__(self, spi_device: blessed.Terminal, num_leds: int, spi_speed_khz: int=800) -> None:
        self.spi_device = spi_device
        self.num_leds = num_leds
        self.temp_state = [MockLEDColor()] * num_leds
        self.led_state: list[MockLEDColor] = []

    def clear_strip(self) -> None:
        self.fill_strip(0, 0, 0)

    def fill_strip(self, red: int=0, green: int=0, blue: int=0) -> None:
        color = MockLEDColor(red, green, blue)
        self.temp_state = [color] * self.num_leds

    def set_led_color(self, index: int, red: int, green: int, blue: int) -> bool:
        if 0 <= index < self.num_leds:
            self.temp_state[index] = MockLEDColor(red, green, blue)
            return True
        return False

    def update_strip(self, sleep_duration: float=0.1) -> None:
        self.led_state = self.temp_state[:]
        print(self.spi_device.green('Lights on: '), end='')
        for idx, color in enumerate(self.led_state):
            if self.led_state[idx].is_set():
                print(self.spi_device.green(str(idx)), end=' ')
        print()
        time.sleep(sleep_duration)

