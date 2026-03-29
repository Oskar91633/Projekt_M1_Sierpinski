def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def collect_sierpinski_triangles(p1, p2, p3, level, triangles=None):
    if triangles is None:
        triangles = []

    if level == 0:
        triangles.append((p1, p2, p3))
    else:
        m12 = midpoint(p1, p2)
        m23 = midpoint(p2, p3)
        m31 = midpoint(p3, p1)

        collect_sierpinski_triangles(p1, m12, m31, level - 1, triangles)
        collect_sierpinski_triangles(m12, p2, m23, level - 1, triangles)
        collect_sierpinski_triangles(m31, m23, p3, level - 1, triangles)

    return triangles