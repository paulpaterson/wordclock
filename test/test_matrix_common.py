import pytest
from matrix_common import Light, LightCollection, WHITE, RED, BLACK


@pytest.fixture
def light() -> Light:
    return Light()


class TestLight:

    def test_light_default_properties(self, light: Light) -> None:
        assert not light.on
        assert light.color == WHITE

    def test_light_can_be_on_or_off(self, light: Light) -> None:
        assert not light.on
        light.turn_on()
        assert light.on
        light.turn_off()
        assert not light.on

    def test_can_toggle_light(self, light: Light) -> None:
        assert not light.on
        light.toggle()
        assert light.on
        light.toggle()
        assert not light.on

    def test_can_set_light_color(self, light: Light) -> None:
        assert light.color == WHITE
        light.set_color(RED)
        assert light.color == RED

    def test_can_set_light_on_or_off_when_setting_color(self, light: Light) -> None:
        assert light.color == WHITE
        assert not light.on
        light.set_color(RED, True)
        assert light.color == RED
        assert light.on
        light.set_color(BLACK, False)
        assert light.color == BLACK
        assert not light.on

    def test_setting_light_color_doesnt_affect_on_off(self, light:Light) -> None:
        light.turn_on()
        light.set_color(RED)
        assert light.on

    def test_shown_color_is_light_color_when_on(self, light: Light) -> None:
        light.turn_on()
        light.set_color(WHITE)
        assert light.get_shown_color() == WHITE
        light.set_color(BLACK)
        assert light.get_shown_color() == BLACK

    def test_shown_color_is_black_if_off(self, light: Light) -> None:
        light.turn_on()
        assert light.get_shown_color() == WHITE
        light.turn_off()
        assert light.get_shown_color() == BLACK


