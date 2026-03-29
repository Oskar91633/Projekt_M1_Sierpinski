from spiral import animate_spiral, draw_spiral
from sierpinski import animate_sierpinski, draw_sierpinski


def get_float(prompt, default):
    value = input(f"{prompt} [domyślnie: {default}]: ").strip()
    if value == "":
        return default
    try:
        return float(value)
    except ValueError:
        print("Niepoprawna wartość. Użyto wartości domyślnej.")
        return default


def get_int(prompt, default):
    value = input(f"{prompt} [domyślnie: {default}]: ").strip()
    if value == "":
        return default
    try:
        return int(value)
    except ValueError:
        print("Niepoprawna wartość. Użyto wartości domyślnej.")
        return default


def main():
    while True:
        print("\n=== Projekt M1 ===")
        print("1 - Statyczna spirala")
        print("2 - Animacja spirali")
        print("3 - Statyczny Trójkąt Sierpińskiego")
        print("4 - Animacja Trójkąta Sierpińskiego")
        print("0 - Wyjście")

        choice = input("Wybierz opcję (0/1/2/3/4): ").strip()

        if choice == "1":
            a = get_float("Podaj skalę spirali a", 0.2)
            t_max = get_float("Podaj maksymalne t", 10 * 3.14159)
            num_points = get_int("Podaj liczbę punktów", 1000)

            if num_points < 10:
                num_points = 10

            draw_spiral(a=a, t_max=t_max, num_points=num_points)

        elif choice == "2":
            a = get_float("Podaj skalę spirali a", 0.2)
            t_max = get_float("Podaj maksymalne t", 10 * 3.14159)
            num_points = get_int("Podaj liczbę punktów", 1000)

            if num_points < 10:
                num_points = 10

            animate_spiral(a=a, t_max=t_max, num_points=num_points)

        elif choice == "3":
            level = get_int("Podaj poziom rekurencji", 4)

            if level < 0:
                level = 0
            if level > 7:
                level = 7

            draw_sierpinski(level=level)

        elif choice == "4":
            level = get_int("Podaj maksymalny poziom rekurencji", 5)

            if level < 0:
                level = 0
            if level > 7:
                level = 7

            animate_sierpinski(max_level=level)

        elif choice == "0":
            print("Zamknięto program.")
            break

        else:
            print("Niepoprawny wybór.")


if __name__ == "__main__":
    main()