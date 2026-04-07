from rnr_mapgen.hex import CubeCoord, HexCoord, cube_distance


def test_axial_to_cube_conversion() -> None:
    coord = HexCoord(q=2, r=-3)

    assert coord.to_cube() == CubeCoord(x=2, y=1, z=-3)


def test_neighbor_count() -> None:
    coord = HexCoord(q=0, r=0)

    assert len(coord.list_neighbors()) == 6


def test_specific_neighbor_offsets() -> None:
    coord = HexCoord(q=4, r=7)

    assert coord.neighbor(0) == HexCoord(q=5, r=7)
    assert coord.neighbor(1) == HexCoord(q=5, r=6)
    assert coord.neighbor(2) == HexCoord(q=4, r=6)
    assert coord.neighbor(3) == HexCoord(q=3, r=7)
    assert coord.neighbor(4) == HexCoord(q=3, r=8)
    assert coord.neighbor(5) == HexCoord(q=4, r=8)


def test_distance_symmetry() -> None:
    a = HexCoord(q=1, r=-2)
    b = HexCoord(q=-2, r=1)

    assert a.distance_to(b) == b.distance_to(a)
    assert a.distance_to(b) == cube_distance(a.to_cube(), b.to_cube())


def test_zero_distance_to_self() -> None:
    coord = HexCoord(q=-5, r=4)

    assert coord.distance_to(coord) == 0
