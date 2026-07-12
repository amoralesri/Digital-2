from ws2812_studio.services.mapping import MatrixMapping


def test_linear_mapping_edges():
    mapping = MatrixMapping()
    assert mapping.logical_to_physical(0, 0) == 0
    assert mapping.logical_to_physical(7, 7) == 63


def test_serpentine_mapping():
    mapping = MatrixMapping(serpentine=True)
    assert mapping.logical_to_physical(0, 0) == 0
    assert mapping.logical_to_physical(0, 1) == 15
    assert mapping.logical_to_physical(7, 1) == 8


def test_bottom_right_origin():
    mapping = MatrixMapping(origin="bottom_right")
    assert mapping.logical_to_physical(0, 0) == 63
    assert mapping.logical_to_physical(7, 7) == 0


def test_rotation_90_stays_in_range():
    mapping = MatrixMapping(rotation=90)
    values = {mapping.logical_to_physical(x, y) for y in range(8) for x in range(8)}
    assert values == set(range(64))
