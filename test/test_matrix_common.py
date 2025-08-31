import pytest
from matrix_common import Light, LightCollection, WHITE, RED, BLACK, GRID, COORD, NoSuchLight, OutOfGridRange


@pytest.fixture
def light() -> Light:
    return Light()


@pytest.fixture
def light_collection() -> LightCollection:
    return LightCollection(GRID(2, 3))


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


class TestLightCollection:

    def test_collection_creates_lights(self) -> None:
        lc = LightCollection(GRID(2, 3))
        assert lc.size == GRID(2, 3)
        assert len(lc.rows()) == 2
        assert len(lc.rows()[0]) == 3
        assert isinstance(lc.rows()[0][0], Light)

    def test_can_get_light_at(self, light_collection: LightCollection) -> None:
        lights: set[Light] = set()
        for row in range(2):
            for col in range(3):
                the_light = light_collection.get_light_at(COORD(row, col))
                assert isinstance(the_light, Light)
                lights.add(the_light)
        assert len(lights) == 2 * 3

    @pytest.mark.parametrize('row, col', [
        (-1, 0), (0, -1), (2, 1), (1, 3), (3, 3), (10, 10)
    ])
    def test_get_light_at_raises_exception_when_out_of_range(self, row:int, col:int, light_collection: LightCollection) -> None:
        with pytest.raises(NoSuchLight):
            light_collection.get_light_at(COORD(row, col))

    @pytest.mark.parametrize('row', [0, 1])
    def test_can_get_a_row_of_coordinates(self, row: int, light_collection: LightCollection) -> None:
        test_row = light_collection.get_row_coords(row)
        assert len(test_row) == 3
        for idx, the_coord in enumerate(test_row):
            assert idx == the_coord.col
            assert row == the_coord.row

    @pytest.mark.parametrize('row', [-1, 2])
    def test_getting_row_fails_if_out_of_range(self, row: int, light_collection: LightCollection) -> None:
        with pytest.raises(OutOfGridRange):
            test_row = light_collection.get_row_coords(row)

    @pytest.mark.parametrize('col', [0, 1])
    def test_can_get_a_col_of_coordinates(self, col: int, light_collection: LightCollection) -> None:
        test_col = light_collection.get_col_coords(col)
        assert len(test_col) == 2
        for idx, the_coord in enumerate(test_col):
            assert col == the_coord.col
            assert idx == the_coord.row

    @pytest.mark.parametrize('col', [-1, 3])
    def test_getting_col_fails_if_out_of_range(self, col: int, light_collection: LightCollection) -> None:
        with pytest.raises(OutOfGridRange):
            test_col = light_collection.get_col_coords(col)

    @pytest.mark.parametrize('distance, expected_number', [
        (0, 10+10+8+8), (1, 8+8+6+6), (2, 6+6+4+4), (3, 4+4+2+2), (4, 2+2+0+0), (5, 0)
    ])
    def test_can_get_a_ring_of_coords(self, distance: int, expected_number: int) -> None:
        light_collection = LightCollection(GRID(10, 10))
        ring = light_collection.get_ring_coords(distance)
        assert len(ring) == expected_number
        if ring:
            #
            assert min(coord.row for coord in ring) == distance
            assert min(coord.col for coord in ring) == distance
            #
            assert max(coord.row for coord in ring) == 9 - distance
            assert max(coord.col for coord in ring) == 9 - distance

    @pytest.mark.parametrize('distance, expected_number', [
        (0, 10+10+10+10), (1, 8+8+8+8), (2, 6+6+6+6), (3, 4+4+4+4), (4, 2+2+2+2), (5, 0)
    ])
    def test_can_get_rectangular_ring(self, distance: int, expected_number: int) -> None:
        light_collection = LightCollection(GRID(10, 12))
        ring = light_collection.get_ring_coords(distance)
        assert len(ring) == expected_number
        if ring:
            #
            assert min(coord.row for coord in ring) == distance
            assert min(coord.col for coord in ring) == distance
            #
            assert max(coord.row for coord in ring) == 9 - distance
            assert max(coord.col for coord in ring) == 11 - distance

    @pytest.mark.parametrize('distance', [-1, 11])
    def test_get_ring_fails_if_distance_is_out_of_range(self, distance: int) -> None:
        light_collection = LightCollection(GRID(10, 10))
        with pytest.raises(OutOfGridRange):
            ring = light_collection.get_ring_coords(distance)

    def test_can_get_edge_coords(self) -> None:
        light_collection = LightCollection(GRID(10, 10))
        assert light_collection.get_ring_coords(0) == light_collection.get_edge_coords()

    @pytest.mark.parametrize('top_left, size', [
        (COORD(0, 0), GRID(1, 1)), (COORD(3, 2), GRID(2, 3)),
        (COORD(8, 4), GRID(2, 5)), (COORD(2, 2), GRID(5, 3)),
    ])
    def test_can_get_box_coords(self, top_left: COORD, size: GRID) -> None:
        light_collection = LightCollection(GRID(10, 12))
        ring = light_collection.get_box_coords(top_left, size)
        expected_number = size.cols * size.rows
        assert len(ring) == expected_number
        if ring:
            #
            assert min(coord.row for coord in ring) == top_left.row
            assert min(coord.col for coord in ring) == top_left.col
            #
            assert max(coord.row for coord in ring) == top_left.row + size.rows - 1
            assert max(coord.col for coord in ring) == top_left.col + size.cols - 1


    @pytest.mark.parametrize('top_left, size', [
        (COORD(-1, 0), GRID(1, 1)),
        (COORD(0, -1), GRID(1, 1)),
        (COORD(10, 0), GRID(1, 1)),
        (COORD(0, 12), GRID(1, 1)),
        (COORD(0, 0), GRID(11, 10)),
        (COORD(0, 0), GRID(10, 13)),
    ])
    def test_get_box_coords_fails_when_out_of_range(self, top_left: COORD, size: GRID) -> None:
        light_collection = LightCollection(GRID(10, 12))
        with pytest.raises(OutOfGridRange):
            ring = light_collection.get_box_coords(top_left, size)

    def test_can_iterate_through_lights(self, light_collection: LightCollection) -> None:
        assert len(list(light_collection)) == 2*3

    def test_can_check_number_of_lights(self, light_collection: LightCollection) -> None:
        assert len(light_collection) == 2*3
