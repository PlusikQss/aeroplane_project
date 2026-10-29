import pytest
import requests
from unittest.mock import patch, Mock
from src.api import OpenSkyAPI


@patch("src.api.requests.get")
def test_get_country_coordinates(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"boundingbox": ["40.0", "50.0", "-10.0", "10.0"]}
    ]
    mock_get.return_value = mock_response

    api = OpenSkyAPI()
    bbox = api.get_country_coordinates("Test")
    assert bbox == (40.0, 50.0, -10.0, 10.0)


@patch("src.api.requests.get")
def test_get_country_coordinates_error(mock_get):
    # api.py ловит именно requests.RequestException
    mock_get.side_effect = requests.RequestException("Network error")
    api = OpenSkyAPI()
    with pytest.raises(ConnectionError):
        api.get_country_coordinates("Test")


@patch("src.api.requests.get")
def test_get_aeroplanes(mock_get):
    mock_nominatim = Mock()
    mock_nominatim.status_code = 200
    mock_nominatim.json.return_value = [
        {"boundingbox": ["40.0", "50.0", "-10.0", "10.0"]}
    ]
    mock_opensky = Mock()
    mock_opensky.status_code = 200
    mock_opensky.json.return_value = {
        "states": [
            ["icao", "CALL", "Country", 0, 0, 0, 0, 1000, False, 200, 0, 0, None, 1000, None, None, 0]
        ]
    }
    mock_get.side_effect = [mock_nominatim, mock_opensky]

    api = OpenSkyAPI()
    states = api.get_aeroplanes("Test")
    assert len(states) == 1
    assert states[0][0] == "icao"


@patch("src.api.requests.get")
def test_get_aeroplanes_empty(mock_get):
    mock_nominatim = Mock()
    mock_nominatim.status_code = 200
    mock_nominatim.json.return_value = [
        {"boundingbox": ["40.0", "50.0", "-10.0", "10.0"]}
    ]
    mock_opensky = Mock()
    mock_opensky.status_code = 200
    mock_opensky.json.return_value = {"states": None}
    mock_get.side_effect = [mock_nominatim, mock_opensky]

    api = OpenSkyAPI()
    states = api.get_aeroplanes("Test")
    assert states == []