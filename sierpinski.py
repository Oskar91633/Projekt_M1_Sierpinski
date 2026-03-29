import matplotlib.pyplot as plt


def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def draw_triangle(ax, p1, p2, p3):
    x = [p1[0], p2[0], p3[0], p1[0]]
    y = [p1[1], p2[1], p3[1], p1[1]]
    ax.fill(x, y, color="black")


def sierpinski(ax, p1, p2, p3, level):
    if level == 0:
        draw_triangle(ax, p1, p2, p3)
    else:
        m12 = midpoint(p1, p2)
        m23 = midpoint(p2, p3)
        m31 = midpoint(p3, p1)

        sierpinski(ax, p1, m12, m31, level - 1)
        sierpinski(ax, m12, p2, m23, level - 1)
        sierpinski(ax, m31, m23, p3, level - 1)


def draw_sierpinski(level=4):
    fig, ax = plt.subplots(figsize=(8, 8))

    p1 = (0, 0)
    p2 = (1, 0)
    p3 = (0.5, 0.86602540378)

    sierpinski(ax, p1, p2, p3, level)

    ax.set_aspect("equal")
    ax.axis("off")
    plt.title(f"Trójkąt Sierpińskiego - poziom {level}")
    plt.show()