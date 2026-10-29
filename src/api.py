import requests
from abc import ABC, abstractmethod


class AeroplanesAPI(ABC):
    """Абстрактный класс для работы с API сервисов самолетов."""

    @abstractmethod
    def get_country_coordinates(self, country: str) -> tuple:
        """Получает boundingbox страны (юг, север, запад, восток)."""
        pass

    @abstractmethod
    def get_aeroplanes(self, country: str) -> list:
        """Получает информацию о самолетах в воздушном пространстве страны."""
        pass


class OpenSkyAPI(AeroplanesAPI):
    """Класс для работы с API nominatim и opensky."""

    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.opensky_url = "https://opensky-network.org/api/states/all"
        self.headers = {"User-Agent": "AeroplaneTracker/1.0"}

    def get_country_coordinates(self, country: str) -> tuple:
        params = {
            "q": country,
            "format": "json",
            "limit": 1
        }
        try:
            response = requests.get(
                self.nominatim_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if not data:
                raise ValueError(f"Страна '{country}' не найдена")
            boundingbox = data[0]["boundingbox"]
            # boundingbox: [south, north, west, east] как строки
            return tuple(map(float, boundingbox))
        except requests.RequestException as e:
            raise ConnectionError(f"Ошибка при запросе координат: {e}")
        except (KeyError, IndexError, ValueError) as e:
            raise ValueError(f"Ошибка обработки ответа Nominatim: {e}")

    def get_aeroplanes(self, country: str) -> list:
        try:
            bbox = self.get_country_coordinates(country)
            params = {
                "lamin": bbox[0],
                "lamax": bbox[1],
                "lomin": bbox[2],
                "lomax": bbox[3]
            }
            response = requests.get(self.opensky_url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            if not data or "states" not in data or not data["states"]:
                return []
            return data["states"]
        except requests.RequestException as e:
            raise ConnectionError(f"Ошибка при запросе самолетов: {e}")
        except Exception as e:
            raise ValueError(f"Ошибка получения данных о самолетах: {e}")