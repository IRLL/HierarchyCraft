from hcraft.examples.minicraft.fourrooms import _get_rooms_connections


def test_four_rooms_should_be_rightfully_connected():
    assert _get_rooms_connections([0, 1, 2, 3]) == {
        0: [3, 1],
        1: [0, 2],
        2: [1, 3],
        3: [2, 0],
    }
