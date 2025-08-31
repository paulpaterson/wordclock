import pytest
from unittest.mock import patch, Mock

import matrix_display
import matrix_modes
from matrix_display import DisplayMatrix
from matrix_common import GRID, COORD, WHITE, RED, BLUE
from matrix_modes import CycleColors


@pytest.fixture
def matrix_no_led() -> DisplayMatrix:
    matrix_display.pi5neo = None  # type: ignore
    return DisplayMatrix(GRID(10, 12), [
        matrix_modes.CycleColors(
            [COORD(1,1)], [RED, WHITE, BLUE]
        )
    ])

@pytest.fixture
def matrix_with_led() -> DisplayMatrix:
    matrix_display.pi5neo = pi5neo = Mock()  # type: ignore
    pi5neo.Pi5Neo.return_value = Mock()
    return DisplayMatrix(GRID(10, 12), [
        matrix_modes.CycleColors(
            [COORD(1,1)], [RED, WHITE, BLUE]
        )
    ])


class TestDisplayMatrix:

    def test_display_matrix_initializes_leds(self, matrix_with_led: DisplayMatrix) -> None:
        matrix_display.pi5neo.Pi5Neo.assert_called_once()   # type: ignore
        matrix_display.pi5neo.Pi5Neo.assert_called_with('/dev/spidev0.0', 10*12, matrix_display.baud_rate)  # type: ignore
        assert isinstance(matrix_with_led.matrix_leds, Mock)

    def test_display_with_no_pi5neo_should_have_no_matrix(self, matrix_no_led: DisplayMatrix) -> None:
        assert matrix_no_led.matrix_leds is None

    def test_display_matrix_should_have_lights(self, matrix_no_led: DisplayMatrix) -> None:
        assert matrix_no_led.lights.size == GRID(10, 12)

    def test_display_matrix_should_have_modes(self, matrix_no_led: DisplayMatrix) -> None:
        assert len(matrix_no_led.modes) == 1

    def test_display_leds_with_no_pi5neo_fails(self, matrix_no_led: DisplayMatrix) -> None:
        with pytest.raises(ImportError):
            matrix_no_led.display_leds()

    def test_display_leds_sets_all_lights(self, matrix_with_led: DisplayMatrix) -> None:
        for color in (WHITE, RED):
            for light in matrix_with_led.lights:
                light.set_color(color, on=True)
            #
            matrix_with_led.matrix_leds = Mock()
            matrix_with_led.display_leds()
            idx = 0
            for row in range(matrix_with_led.size.rows):
                for col in range(matrix_with_led.size.cols):
                    matrix_with_led.matrix_leds.set_led_color.assert_any_call(idx, *color)
                    idx += 1

    def test_display_leds_updates_the_strip(self, matrix_with_led: DisplayMatrix) -> None:
        matrix_with_led.display_leds()
        matrix_with_led.matrix_leds.update_strip.assert_called_once()

    def test_display_update_board_updates_all_modes(self, matrix_with_led: DisplayMatrix) -> None:
        matrix_with_led.modes = [
            m1 := Mock(),
            m2 := Mock(),
        ]
        matrix_with_led.update_board()
        m1.update.assert_called_once()
        m2.update.assert_called_once()

