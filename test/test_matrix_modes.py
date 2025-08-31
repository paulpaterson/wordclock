import pytest

from matrix_common import LightCollection, GRID
from matrix_modes import Mode, COORD, COLOR


def test_mode_has_locations_that_are_coords() -> None:
    mode = Mode([
        COORD(0, 0), COORD(10, 10),
    ])
    assert mode.light_locations[0] == COORD(0, 0)
    assert mode.light_locations[1] == COORD(10, 10)

def test_mode_can_be_updated() -> None:
    mode = Mode([])
    mode.update(LightCollection(GRID(10, 10)))

