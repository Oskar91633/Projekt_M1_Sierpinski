import numpy as np


def generate_spiral(a, t_max, num_points):
    t = np.linspace(0, t_max, num_points)
    x = a * t * np.cos(t)
    y = a * t * np.sin(t)
    return x, y