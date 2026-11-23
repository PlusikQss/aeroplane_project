import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()

class DBManager:
    """Класс для работы с базой данных PostgreSQL."""

    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),  # Берем из .env
                dbname=os.getenv("DB_NAME")
            )
            self.conn.autocommit = True
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Ошибка подключения к БД. Проверь .env.\n{e}")

    def get_countries_and_aeroplanes_count(self):
        """Список стран и количество самолетов в их пространстве."""
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT c.name, COUNT(a.id) as count
                FROM countries c
                LEFT JOIN aeroplanes a ON c.id = a.country_id
                GROUP BY c.name
                ORDER BY count DESC;
            """)
            return cur.fetchall()

    def get_all_aeroplanes(self):
        """Список всех самолетов."""
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT a.callsign, a.velocity, a.altitude, c.name as country
                FROM aeroplanes a
                JOIN countries c ON a.country_id = c.id;
            """)
            return cur.fetchall()

    def get_avg_speed(self):
        """Средняя скорость."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT AVG(velocity) FROM aeroplanes WHERE velocity > 0;")
            result = cur.fetchone()[0]
            return result if result else 0.0

    def get_aeroplanes_with_higher_speed(self):
        """Самолеты со скоростью выше средней."""
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT a.callsign, a.velocity, c.name as country
                FROM aeroplanes a
                JOIN countries c ON a.country_id = c.id
                WHERE a.velocity > (SELECT AVG(velocity) FROM aeroplanes WHERE velocity > 0);
            """)
            return cur.fetchall()

    def get_aeroplanes_with_keyword(self, keyword: str):
        """Поиск самолетов по позывному (ILIKE)."""
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT a.callsign, a.velocity, c.name as country
                FROM aeroplanes a
                JOIN countries c ON a.country_id = c.id
                WHERE a.callsign ILIKE %s;
            """, (f"%{keyword}%",))
            return cur.fetchall()

    def insert_country(self, country_name: str) -> int:
        """Добавляет страну и возвращает её ID."""
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO countries (name) VALUES (%s) ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id;",
                (country_name,)
            )
            return cur.fetchone()[0]

    def insert_aeroplane(self, icao24, callsign, velocity, altitude, country_id):
        """Добавляет самолет в БД."""
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO aeroplanes (icao24, callsign, velocity, altitude, country_id) VALUES (%s, %s, %s, %s, %s);",
                (icao24, callsign, velocity, altitude, country_id)
            )

    def clear_aeroplanes(self):
        """Очищает таблицу самолетов перед новым сканированием."""
        with self.conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE aeroplanes RESTART IDENTITY;")

    def close(self):
        self.conn.close()