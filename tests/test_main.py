from unittest.mock import patch
import main
from main import (filter_aeroplanes, get_aeroplanes_by_altitude,
                  sort_aeroplanes, get_top_aeroplanes)
from src.aeroplane import Aeroplane


def test_filter_aeroplanes():
    a1 = Aeroplane("A", "USA", 100, 2000)
    a2 = Aeroplane("B", "Canada", 200, 3000)
    result = filter_aeroplanes([a1, a2], ["USA"])
    assert len(result) == 1
    assert result[0].callsign == "A"


def test_filter_aeroplanes_multiword_country():
    # United States передаётся одной строкой (через запятую)
    a1 = Aeroplane("A", "United States", 100, 2000)
    a2 = Aeroplane("B", "Germany", 200, 3000)
    a3 = Aeroplane("C", "United Kingdom", 300, 4000)
    result = filter_aeroplanes([a1, a2, a3], ["United States"])
    assert len(result) == 1
    assert result[0].callsign == "A"


def test_get_aeroplanes_by_altitude():
    a1 = Aeroplane("A", "USA", 100, 2000)
    a2 = Aeroplane("B", "Canada", 200, 3000)
    result = get_aeroplanes_by_altitude([a1, a2], "2500-3500")
    assert len(result) == 1
    assert result[0].callsign == "B"


def test_sort_aeroplanes():
    a1 = Aeroplane("A", "USA", 100, 2000)
    a2 = Aeroplane("B", "Canada", 200, 3000)
    sorted_list = sort_aeroplanes([a1, a2])
    assert sorted_list[0].callsign == "B"
    assert sorted_list[1].callsign == "A"


def test_get_top_aeroplanes():
    a1 = Aeroplane("A", "USA", 100, 2000)
    a2 = Aeroplane("B", "Canada", 200, 3000)
    top = get_top_aeroplanes([a1, a2], 1)
    assert len(top) == 1
    assert top[0].callsign == "A"


def test_filter_aeroplanes_empty_countries():
    a1 = Aeroplane("A", "USA", 100, 2000)
    assert filter_aeroplanes([a1], []) == [a1]


def test_filter_aeroplanes_no_match():
    a1 = Aeroplane("A", "USA", 100, 2000)
    assert filter_aeroplanes([a1], ["Germany"]) == []


def test_get_aeroplanes_by_altitude_invalid_range():
    a1 = Aeroplane("A", "USA", 100, 2000)
    assert get_aeroplanes_by_altitude([a1], "abc") == [a1]
    assert get_aeroplanes_by_altitude([a1], "") == [a1]


def test_get_aeroplanes_by_altitude_non_numeric_with_dash():
    a1 = Aeroplane("A", "USA", 100, 2000)
    # "-" есть, но float("abc") упадёт → except → возврат исходного списка
    assert get_aeroplanes_by_altitude([a1], "abc-def") == [a1]


def test_get_aeroplanes_by_altitude_reversed_range():
    # Высота 3000 попадает в нормализованный диапазон 2500..3500
    a1 = Aeroplane("A", "USA", 100, 3000)
    a2 = Aeroplane("B", "Canada", 200, 2000)  # ниже диапазона
    result = get_aeroplanes_by_altitude([a1, a2], "3500-2500")
    assert len(result) == 1
    assert result[0].callsign == "A"


def test_get_top_aeroplanes_more_than_list():
    a1 = Aeroplane("A", "USA", 100, 2000)
    assert get_top_aeroplanes([a1], 10) == [a1]


def test_user_interaction_full_flow(capsys):
    # Мокаем API, чтобы не делать реальных запросов в сеть
    mock_states = [
        ["icao1", "CALL1", "Country1", 0, 0, 0, 0, 1000, False, 200, 0, 0, None, 1000, None, None, 0]
    ]

    # Эмулируем ввод пользователя:
    # 1 - загрузить страну (TestCountry) -> 2 - топ 1 -> 3 - фильтр (Country1) -> 4 - высота (500-1500) ->
    # 5 - сохранить -> 6 - показать -> 7 - удалить (CALL1) -> 9 - неверный ввод -> 0 - выход
    inputs = [
        "1", "TestCountry",
        "2", "1",
        "3", "Country1",
        "4", "500-1500",
        "5",
        "6",
        "7", "CALL1",
        "9",
        "0"
    ]

    with patch("builtins.input", side_effect=inputs), \
            patch("main.OpenSkyAPI.get_aeroplanes", return_value=mock_states), \
            patch("main.JSONSaver.add_aeroplane") as mock_add, \
            patch("main.JSONSaver.get_aeroplanes", return_value=[{"callsign": "CALL1"}]), \
            patch("main.JSONSaver.delete_aeroplane") as mock_delete:
        # Сбрасываем глобальную переменную перед тестом
        main.current_aeroplanes = []

        # Запускаем меню
        main.user_interaction()

    # Перехватываем всё, что программа вывела в консоль
    captured = capsys.readouterr()

    # Проверяем, что программа прошла по всем веткам
    assert "Загружено 1 самолетов." in captured.out
    assert "Самолет CALL1" in captured.out
    assert "Сохранено" in captured.out
    assert "Удалено" in captured.out
    assert "Неверный выбор." in captured.out

    # Проверяем, что методы файла вызывались
    mock_add.assert_called_once()
    mock_delete.assert_called_once()