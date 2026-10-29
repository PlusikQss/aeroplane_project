import pytest
from src.aeroplane import Aeroplane


def test_aeroplane_creation():
    a = Aeroplane("UAL1621", "United States", 268.79, 10203.18)
    assert a.callsign == "UAL1621"
    assert a.origin_country == "United States"
    assert a.velocity == 268.79
    assert a.altitude == 10203.18


def test_aeroplane_invalid_velocity():
    with pytest.raises(ValueError):
        Aeroplane("A", "B", -10, 1000)


def test_aeroplane_invalid_altitude():
    # Отрицательная высота — невалидна (см. форум: altitude >= 0)
    with pytest.raises(ValueError):
        Aeroplane("A", "B", 100, -2000)


def test_aeroplane_invalid_callsign():
    a = Aeroplane("", "B", 100, 2000)
    assert a.callsign == "Unknown"


def test_aeroplane_comparison_by_altitude():
    a1 = Aeroplane("A", "X", 100, 2000)   # ниже
    a2 = Aeroplane("B", "Y", 200, 3000)   # выше
    assert a1 < a2
    assert a2 > a1
    assert a1 != a2
    assert a1 == Aeroplane("A", "X", 100, 2000)


def test_compare_by_speed():
    slow = Aeroplane("A", "X", 100, 2000)
    fast = Aeroplane("B", "Y", 300, 2000)
    assert fast.compare_by_speed(slow) is True
    assert slow.compare_by_speed(fast) is False


def test_cast_to_object_list():
    states = [
        ["icao1", "CALL1", "Country1", 0, 0, 0, 0, 1000, False, 200, 0, 0, None, 1000, None, None, 0],
        ["icao2", "CALL2", "Country2", 0, 0, 0, 0, None, False, 300, 0, 0, None, 2000, None, None, 0],
    ]
    objs = Aeroplane.cast_to_object_list(states)
    assert len(objs) == 2
    assert objs[0].altitude == 1000
    assert objs[1].altitude == 2000


def test_cast_to_object_list_skips_invalid():
    # Второй самолёт с отрицательной высотой должен быть отброшен
    states = [
        ["icao1", "CALL1", "Country1", 0, 0, 0, 0, 1000, False, 200, 0, 0, None, 1000, None, None, 0],
        ["icao2", "CALL2", "Country2", 0, 0, 0, 0, -500, False, 300, 0, 0, None, -500, None, None, 0],
    ]
    objs = Aeroplane.cast_to_object_list(states)
    assert len(objs) == 1
    assert objs[0].callsign == "CALL1"