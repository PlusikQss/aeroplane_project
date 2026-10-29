import pytest
from src.file_saver import JSONSaver
from src.aeroplane import Aeroplane


@pytest.fixture
def temp_file(tmp_path):
    return str(tmp_path / "test.json")


def test_add_and_get(temp_file):
    saver = JSONSaver(temp_file)
    a = Aeroplane("A", "B", 100, 2000, icao24="abc123")
    saver.add_aeroplane(a)
    data = saver.get_aeroplanes()
    assert len(data) == 1
    assert data[0]["callsign"] == "A"


def test_add_duplicate_skipped(temp_file):
    saver = JSONSaver(temp_file)
    a = Aeroplane("A", "B", 100, 2000, icao24="abc123")
    saver.add_aeroplane(a)
    saver.add_aeroplane(a)  # дубликат по icao24
    data = saver.get_aeroplanes()
    assert len(data) == 1


def test_delete(temp_file):
    saver = JSONSaver(temp_file)
    a = Aeroplane("A", "B", 100, 2000)
    saver.add_aeroplane(a)
    saver.delete_aeroplane(a)
    data = saver.get_aeroplanes()
    assert len(data) == 0


def test_get_with_criteria(temp_file):
    saver = JSONSaver(temp_file)
    a1 = Aeroplane("A", "B", 100, 2000)
    a2 = Aeroplane("C", "D", 200, 3000)
    saver.add_aeroplane(a1)
    saver.add_aeroplane(a2)
    data = saver.get_aeroplanes({"origin_country": "B"})
    assert len(data) == 1
    assert data[0]["callsign"] == "A"