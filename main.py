from src.api import OpenSkyAPI
from src.aeroplane import Aeroplane
from src.file_saver import JSONSaver
# Глобальное состояние для текущих самолетов
current_aeroplanes = []


def filter_aeroplanes(aeroplanes, countries):
    """Фильтрация по стране регистрации."""
    if not countries:
        return aeroplanes
    return [a for a in aeroplanes
            if any(c.lower() in a.origin_country.lower() for c in countries)]


def get_aeroplanes_by_altitude(aeroplanes, altitude_range: str):
    """Фильтрация по диапазону высот. altitude_range: 'min-max'."""
    try:
        if not altitude_range or "-" not in altitude_range:
            return aeroplanes
        low, high = map(float, altitude_range.split("-"))
        if low > high:
            low, high = high, low
        return [a for a in aeroplanes if low <= a.altitude <= high]
    except ValueError:
        print("Некорректный диапазон высот. Пропускаем фильтрацию.")
        return aeroplanes


def sort_aeroplanes(aeroplanes):
    """Сортировка по высоте по убыванию."""
    return sorted(aeroplanes, key=lambda a: a.altitude, reverse=True)


def get_top_aeroplanes(aeroplanes, n: int):
    return aeroplanes[:n]


def print_aeroplanes(aeroplanes):
    if not aeroplanes:
        print("Самолеты не найдены.")
        return
    for a in aeroplanes:
        print(a)


def user_interaction():
    global current_aeroplanes
    api = OpenSkyAPI()
    json_saver = JSONSaver()

    while True:
        print("\n--- Меню ---")
        print("1. Загрузить самолеты по стране")
        print("2. Показать топ N самолетов по высоте")
        print("3. Фильтр по стране регистрации")
        print("4. Фильтр по диапазону высот")
        print("5. Сохранить текущие самолеты в JSON")
        print("6. Показать сохраненные самолеты")
        print("7. Удалить самолет из файла")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "0":
            break

        if choice == "1":
            country = input("Введите название страны: ").strip()
            try:
                states = api.get_aeroplanes(country)
                if not states:
                    print("Самолеты не найдены.")
                    continue
                current_aeroplanes = Aeroplane.cast_to_object_list(states)
                print(f"Загружено {len(current_aeroplanes)} самолетов.")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "2":
            if not current_aeroplanes:
                print("Сначала загрузите самолеты (пункт 1).")
                continue
            try:
                n = int(input("Введите N: "))
                top = get_top_aeroplanes(sort_aeroplanes(current_aeroplanes), n)
                print_aeroplanes(top)
            except ValueError:
                print("N должно быть целым числом.")

        elif choice == "3":
            if not current_aeroplanes:
                print("Сначала загрузите самолеты (пункт 1).")
                continue
            raw = input("Введите страны регистрации через запятую "
                        "(например: United States, Germany): ")
            countries = [c.strip() for c in raw.split(",") if c.strip()]
            filtered = filter_aeroplanes(current_aeroplanes, countries)
            print_aeroplanes(filtered)

        elif choice == "4":
            if not current_aeroplanes:
                print("Сначала загрузите самолеты (пункт 1).")
                continue
            alt_range = input("Введите диапазон высот (например, 1000-10000): ").strip()
            filtered = get_aeroplanes_by_altitude(current_aeroplanes, alt_range)
            print_aeroplanes(filtered)

        elif choice == "5":
            if not current_aeroplanes:
                print("Сначала загрузите самолеты (пункт 1).")
                continue
            for a in current_aeroplanes:
                json_saver.add_aeroplane(a)
            print("Сохранено (дубликаты пропущены).")

        elif choice == "6":
            data = json_saver.get_aeroplanes()
            if not data:
                print("Файл пуст.")
            else:
                for item in data:
                    print(item)

        elif choice == "7":
            if not current_aeroplanes:
                print("Сначала загрузите самолеты (пункт 1).")
                continue
            callsign = input("Введите позывной для удаления: ").strip()
            to_delete = [a for a in current_aeroplanes
                         if a.callsign.lower() == callsign.lower()]
            if not to_delete:
                print("Самолет не найден.")
            else:
                for a in to_delete:
                    json_saver.delete_aeroplane(a)
                print("Удалено.")

        else:
            print("Неверный выбор.")


if __name__ == "__main__":
    user_interaction()