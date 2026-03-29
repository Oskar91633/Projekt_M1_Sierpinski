import numpy as np
import matplotlib.pyplot as plt

def generate_spiral(a, t_max, num_points):
    t = np.linspace(0, t_max, num_points)
    x = a * t * np.cos(t)
    y = a * t * np.sin(t)
    return x, y

def draw_spiral(a=0.2, t_max=10 * np.pi, num_points=1000):
    x, y = generate_spiral(a, t_max, num_points)

    plt.figure(figsize=(8, 8))
    plt.plot(x, y)
    plt.title("Spirala Archimedesa")
    plt.axis("equal")
    plt.grid(True)
    plt.show()