from spiral import draw_spiral
from sierpinski import draw_sierpinski


def main():
    while True:
        print("\n=== Projekt M1 ===")
        print("1 - Spirala Archimedesa")
        print("2 - Trójkąt Sierpińskiego")
        print("0 - Wyjście")

        choice = input("Wybierz opcję (0/1/2): ").strip()

        if choice == "1":
            draw_spiral()
        elif choice == "2":
            draw_sierpinski()
        elif choice == "0":
            print("Zamknięto program.")
            break
        else:
            print("Niepoprawny wybór. Spróbuj ponownie.")


if __name__ == "__main__":
    main()