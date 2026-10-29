import json
import os
from abc import ABC, abstractmethod


class Saver(ABC):
    """Абстрактный класс для сохранения информации о самолетах."""

    @abstractmethod
    def add_aeroplane(self, aeroplane):
        pass

    @abstractmethod
    def get_aeroplanes(self, criteria: dict = None):
        pass

    @abstractmethod
    def delete_aeroplane(self, aeroplane):
        pass


class JSONSaver(Saver):
    """Класс для сохранения информации о самолетах в JSON-файл."""

    def __init__(self, filename: str = "data/aeroplanes.json"):
        self.filename = filename

    def _load(self) -> list:
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, data: list) -> None:
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_aeroplane(self, aeroplane) -> None:
        data = self._load()
        # Защита от дублей по уникальному icao24 (см. форум)
        for item in data:
            if item.get("icao24") and item["icao24"] == aeroplane.icao24:
                return
        data.append({
            "callsign": aeroplane.callsign,
            "origin_country": aeroplane.origin_country,
            "velocity": aeroplane.velocity,
            "altitude": aeroplane.altitude,
            "on_ground": aeroplane.on_ground,
            "icao24": aeroplane.icao24
        })
        self._save(data)

    def get_aeroplanes(self, criteria: dict = None) -> list:
        data = self._load()
        if not criteria:
            return data
        filtered = []
        for item in data:
            match = True
            for key, value in criteria.items():
                if key in item:
                    if isinstance(value, (int, float)):
                        if item[key] != value:
                            match = False
                            break
                    elif isinstance(value, str):
                        if value.lower() not in str(item[key]).lower():
                            match = False
                            break
            if match:
                filtered.append(item)
        return filtered

    def delete_aeroplane(self, aeroplane) -> None:
        data = self._load()
        new_data = [item for item in data if not (
            item["callsign"] == aeroplane.callsign and
            item["origin_country"] == aeroplane.origin_country and
            item["velocity"] == aeroplane.velocity and
            item["altitude"] == aeroplane.altitude
        )]
        self._save(new_data)