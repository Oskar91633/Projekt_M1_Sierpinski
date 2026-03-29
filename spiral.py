import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

ANIMATION = None


def generate_spiral(a, t_max, num_points):
    t = np.linspace(0, t_max, num_points)
    x = a * t * np.cos(t)
    y = a * t * np.sin(t)
    return x, y


def draw_spiral(a=0.2, t_max=10 * np.pi, num_points=1000):
    x, y = generate_spiral(a, t_max, num_points)

    plt.figure(figsize=(8, 8))
    plt.plot(x, y, linewidth=2)
    plt.title(f"Spirala Archimedesa | a={a}, t_max={t_max:.2f}, punkty={num_points}")
    plt.axis("equal")
    plt.grid(True)
    plt.show()


def animate_spiral(a=0.2, t_max=10 * np.pi, num_points=1000):
    global ANIMATION

    x, y = generate_spiral(a, t_max, num_points)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_title("Animacja spirali Archimedesa")
    ax.set_aspect("equal")
    ax.grid(True)

    margin = 0.5
    ax.set_xlim(np.min(x) - margin, np.max(x) + margin)
    ax.set_ylim(np.min(y) - margin, np.max(y) + margin)

    line, = ax.plot([], [], linewidth=2)

    def init():
        line.set_data([], [])
        return (line,)

    def update(frame):
        line.set_data(x[:frame + 1], y[:frame + 1])
        return (line,)

    ANIMATION = FuncAnimation(
        fig,
        update,
        frames=len(x),
        init_func=init,
        interval=10,
        blit=True,
        repeat=False
    )

    plt.show()