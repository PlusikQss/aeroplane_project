class Aeroplane:
    """Класс для работы с информацией о самолете."""

    def __init__(self, callsign: str, origin_country: str, velocity: float,
                 altitude: float, on_ground: bool = False, icao24: str = ""):
        self.callsign = self._validate_str(callsign)
        self.origin_country = self._validate_str(origin_country)
        self.velocity = self._validate_float(velocity, "velocity")
        self.altitude = self._validate_float(altitude, "altitude")
        self.on_ground = bool(on_ground)
        self.icao24 = str(icao24)

    @staticmethod
    def _validate_str(value):
        if not isinstance(value, str) or not value.strip():
            return "Unknown"
        return value.strip()

    @staticmethod
    def _validate_float(value, name):
        """Строгая валидация: значение должно быть числом >= 0."""
        try:
            val = float(value)
            if val < 0:
                raise ValueError(f"{name} не может быть отрицательным")
            return val
        except (TypeError, ValueError):
            raise ValueError(f"Некорректное значение {name}: {value}")

    @classmethod
    def cast_to_object_list(cls, states: list) -> list:
        """Преобразует список состояний OpenSky в список объектов Aeroplane.

        Невалидные записи (None, отрицательные значения, обрезанные строки)
        пропускаются — см. обсуждение на форуме.
        """
        aeroplanes = []
        for state in states:
            try:
                icao24 = state[0] or "Unknown"
                callsign = state[1].strip() if state[1] else "Unknown"
                origin_country = state[2] or "Unknown"

                # Приоритет: baro_altitude (7), иначе geo_altitude (13)
                altitude = state[7] if state[7] is not None else state[13]
                velocity = state[9] if state[9] is not None else 0.0
                on_ground = bool(state[8]) if state[8] is not None else False

                aeroplanes.append(
                    cls(callsign, origin_country, velocity, altitude, on_ground, icao24)
                )
            except (IndexError, TypeError, ValueError):
                # Отбрасываем самолёт с невалидными данными
                continue
        return aeroplanes

    # --- Магические методы: сравнение по ВЫСОТЕ (основной параметр) ---
    def __eq__(self, other):
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.altitude == other.altitude

    def __lt__(self, other):
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.altitude < other.altitude

    def __gt__(self, other):
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.altitude > other.altitude

    def __le__(self, other):
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.altitude <= other.altitude

    def __ge__(self, other):
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.altitude >= other.altitude

    # --- Обычный метод: сравнение по СКОРОСТИ (как просил наставник) ---
    def compare_by_speed(self, other) -> bool:
        """True, если текущий самолёт быстрее другого."""
        if not isinstance(other, Aeroplane):
            return False
        return self.velocity > other.velocity

    def __str__(self):
        return (f"Самолет {self.callsign} ({self.origin_country}): "
                f"скорость {self.velocity:.1f} м/с, высота {self.altitude:.1f} м, "
                f"на земле: {self.on_ground}")

    def __repr__(self):
        return (f"Aeroplane({self.callsign!r}, {self.origin_country!r}, "
                f"{self.velocity}, {self.altitude})")