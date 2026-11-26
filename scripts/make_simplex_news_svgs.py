#!/usr/bin/env python3
"""Generate the pictures for the "Simplex Method News" slides of lecture 21.

  news_polytope_walk.svg        - a walk along the edges of a polytope towards
                                  better objective values
  news_polytope_directions.svg  - the edges leaving one vertex: the choices a
                                  pivot rule has to pick from
  news_long_path.svg            - a very long path to the optimum: the
                                  Klee-Minty cube, where the path visits every vertex
  news_long_vs_short.svg        - the same polytope with the long path and a
                                  one-edge path between the same two vertices
"""

import math
import os

INK = "#073642"
BLUE = "#268bd2"
GREEN = "#859900"
RED = "#dc322f"
ORANGE = "#cb4b16"
FAINT = "#93a1a1"
IMAGES = os.path.join(os.path.dirname(__file__), "..", "images")


def write(name, body, w, h):
    path = os.path.join(IMAGES, name)
    defs = ('<defs>'
            + "".join(f'<marker id="arr-{k}" markerUnits="userSpaceOnUse" markerWidth="15" markerHeight="12" refX="12" refY="6" orient="auto">'
                      f'<path d="M0,0 L15,6 L0,12 z" fill="{col}"/></marker>'
                      for k, col in (("red", RED), ("green", GREEN), ("orange", ORANGE), ("faint", FAINT), ("ink", INK)))
            + '</defs>')
    with open(path, "w") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
                 f'font-family="Georgia, serif">\n{defs}\n' + "\n".join(body) + "\n</svg>\n")
    print("wrote", os.path.normpath(path))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


class Polytope:
    """A 3-dimensional polytope drawn in a parallel projection with rows r1
    (screen right) and r2 (screen up)."""

    def __init__(self, verts, faces, r1, r2, scale, origin):
        self.V, self.F = verts, faces
        self.r1, self.r2, self.scale, self.origin = r1, r2, scale, origin
        self.view = cross(r1, r2)  # points towards the viewer
        cen = tuple(sum(v[i] for v in verts) / len(verts) for i in range(3))
        self.front = []
        for f in faces:
            n = cross(sub(verts[f[1]], verts[f[0]]), sub(verts[f[2]], verts[f[0]]))
            if dot(n, sub(verts[f[0]], cen)) < 0:
                n = tuple(-x for x in n)
            self.front.append(dot(n, self.view) > 1e-9)
        self.edges = {}
        for fi, f in enumerate(faces):
            for a, b in zip(f, f[1:] + f[:1]):
                self.edges.setdefault(frozenset((a, b)), []).append(fi)
        assert all(len(fs) == 2 for fs in self.edges.values())
        self.nbrs = {i: sorted(j for e in self.edges for j in e if i in e and j != i) for i in range(len(verts))}

    def px(self, i):
        v = self.V[i] if isinstance(i, int) else i
        return (self.origin[0] + self.scale * dot(self.r1, v), self.origin[1] - self.scale * dot(self.r2, v))

    def visible(self, a, b):
        return any(self.front[fi] for fi in self.edges[frozenset((a, b))])

    def draw(self):
        s = []
        for fi, f in enumerate(self.F):
            if self.front[fi]:
                pts = " ".join(f"{self.px(i)[0]:.1f},{self.px(i)[1]:.1f}" for i in f)
                s.append(f'<polygon points="{pts}" fill="{BLUE}" fill-opacity="0.10"/>')
        for hidden in (True, False):
            for e in self.edges:
                a, b = sorted(e)
                if self.visible(a, b) == hidden:
                    continue
                p, q = self.px(a), self.px(b)
                style = (f'stroke="{BLUE}" stroke-width="1.2" stroke-opacity="0.45" stroke-dasharray="4 4"' if hidden
                         else f'stroke="{BLUE}" stroke-width="2"')
                s.append(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" {style}/>')
        return s

    def dots(self, color=BLUE, r=3.5):
        return [f'<circle cx="{self.px(i)[0]:.1f}" cy="{self.px(i)[1]:.1f}" r="{r}" fill="{color}"/>' for i in range(len(self.V))]

    def arrow(self, a, b, color, key, width=4, shorten=9.0, start_gap=0.0, opacity=1.0):
        p, q = self.px(a), self.px(b)
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L
        return (f'<line x1="{p[0]+ux*start_gap:.1f}" y1="{p[1]+uy*start_gap:.1f}" x2="{q[0]-ux*shorten:.1f}" y2="{q[1]-uy*shorten:.1f}" '
                f'stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-opacity="{opacity}" marker-end="url(#arr-{key})"/>')

    def mark(self, i, color, label=None, dx=12, dy=5, anchor="start", r=7):
        p = self.px(i)
        s = [f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{r}" fill="{color}" stroke="#fff" stroke-width="1.5"/>']
        if label:
            s.append(f'<text x="{p[0]+dx:.1f}" y="{p[1]+dy:.1f}" font-size="16" fill="{color}" text-anchor="{anchor}">{label}</text>')
        return s


def objective_arrow(x, y_bottom, y_top, label="better objective value"):
    return [f'<line x1="{x}" y1="{y_bottom}" x2="{x}" y2="{y_top+10}" stroke="{INK}" stroke-width="2" marker-end="url(#arr-ink)"/>',
            f'<text x="{x+10}" y="{(y_bottom+y_top)/2:.1f}" font-size="15" fill="{INK}" '
            f'transform="rotate(-90 {x+10} {(y_bottom+y_top)/2:.1f})" text-anchor="middle" dy="14">{label}</text>']


# ------------------------------------------------------------ an icosahedron
def icosahedron():
    rad, z = 2 / math.sqrt(5), 1 / math.sqrt(5)
    V = [(0.0, 0.0, 1.0)]
    V += [(rad * math.cos(math.radians(72 * k)), rad * math.sin(math.radians(72 * k)), z) for k in range(5)]        # 1..5
    V += [(rad * math.cos(math.radians(36 + 72 * k)), rad * math.sin(math.radians(36 + 72 * k)), -z) for k in range(5)]  # 6..10
    V += [(0.0, 0.0, -1.0)]                                                                                         # 11
    U = lambda k: 1 + k % 5
    Lw = lambda k: 6 + k % 5
    F = []
    for k in range(5):
        F += [[0, U(k), U(k + 1)], [U(k), Lw(k), U(k + 1)], [Lw(k), Lw(k + 1), U(k + 1)], [11, Lw(k + 1), Lw(k)]]
    al, be = math.radians(-100), math.radians(17)
    r1 = (math.cos(al), math.sin(al), 0.0)
    r2 = (-math.sin(al) * math.sin(be), math.cos(al) * math.sin(be), math.cos(be))
    return V, F, r1, r2


C_OBJ = (0.22, -0.13, 1.0)  # the objective: mostly "up", tilted a little so that no two vertices tie


def polytope_walk():
    W, H = 460, 400
    V, F, r1, r2 = icosahedron()
    P = Polytope(V, F, r1, r2, 165, (215, 205))
    val = lambda i: dot(C_OBJ, V[i])
    assert len({round(val(i), 9) for i in range(len(V))}) == len(V)
    best = max(range(len(V)), key=val)
    worst = min(range(len(V)), key=val)
    # walk: at each vertex move to a neighbour with a better value (the least improving visible-friendly choice
    # would be arbitrary; take the neighbour with the smallest improvement to get a walk of a few steps)
    path = [worst]
    while path[-1] != best:
        cur = path[-1]
        better = [j for j in P.nbrs[cur] if val(j) > val(cur)]
        seen = [j for j in better if P.visible(cur, j)] or better
        path.append(min(seen, key=val))
    assert all(val(b) > val(a) for a, b in zip(path, path[1:]))
    s = P.draw() + P.dots()
    for a, b in zip(path, path[1:]):
        s.append(P.arrow(a, b, ORANGE, "orange"))
    s += P.mark(path[0], ORANGE, "start", dx=0, dy=24, anchor="middle")
    s += P.mark(path[-1], GREEN, "optimal", dx=0, dy=-14, anchor="middle")
    s += objective_arrow(425, 330, 70)
    write("news_polytope_walk.svg", s, W, H)
    return path


def polytope_directions():
    W, H = 460, 440
    V, F, r1, r2 = icosahedron()
    P = Polytope(V, F, r1, r2, 165, (215, 195))
    val = lambda i: dot(C_OBJ, V[i])
    # the front-most vertex that is not the top or the bottom, with all of its edges visible
    cand = [i for i in range(1, 11) if all(P.visible(i, j) for j in P.nbrs[i])]
    v = max(cand, key=lambda i: dot(P.view, V[i]))
    assert len(P.nbrs[v]) == 5
    better = [j for j in P.nbrs[v] if val(j) > val(v)]
    worse = [j for j in P.nbrs[v] if val(j) < val(v)]
    assert len(better) >= 2 and worse
    s = P.draw() + P.dots()
    for j in worse:
        s.append(P.arrow(v, j, FAINT, "faint", width=3.5))
    for j in better:
        s.append(P.arrow(v, j, GREEN, "green", width=4.5))
    s += P.mark(v, ORANGE, r=8)
    s.append(f'<text x="18" y="{H-34}" font-size="15" fill="{GREEN}">improving edges: which one do we take?</text>')
    s.append(f'<text x="18" y="{H-14}" font-size="15" fill="{FAINT}">edges that make the objective worse</text>')
    s += objective_arrow(425, 320, 60)
    write("news_polytope_directions.svg", s, W, H)


# ------------------------------------------------------------ the Klee-Minty cube
def klee_minty(eps=0.3):
    """0 <= x1 <= 1, eps x1 <= x2 <= 1 - eps x1, eps x2 <= x3 <= 1 - eps x2; maximize x3."""
    def vert(b1, b2, b3):
        x1 = float(b1)
        x2 = 1 - eps * x1 if b2 else eps * x1
        x3 = 1 - eps * x2 if b3 else eps * x2
        return (x1, x2, x3)
    bits = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    V = [vert(*b) for b in bits]
    idx = {b: i for i, b in enumerate(bits)}
    F = []
    for axis in range(3):
        for side in (0, 1):
            o1, o2 = [a for a in range(3) if a != axis]
            cyc = []
            for u, w in ((0, 0), (1, 0), (1, 1), (0, 1)):
                b = [0, 0, 0]
                b[axis], b[o1], b[o2] = side, u, w
                cyc.append(idx[tuple(b)])
            F.append(cyc)
    # the simplex path that visits every vertex: a Gray code in which x3 increases at every step
    order = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)]
    path = [idx[b] for b in order]
    for a, b in zip(path, path[1:]):
        assert V[b][2] > V[a][2] + 1e-9
        assert sum(x != y for x, y in zip(bits[a], bits[b])) == 1
    al, be = math.radians(-118), math.radians(20)
    r1 = (math.cos(al), math.sin(al), 0.0)
    r2 = (-math.sin(al) * math.sin(be), math.cos(al) * math.sin(be), math.cos(be))
    return V, F, r1, r2, path


def cube_pictures():
    W, H = 460, 430
    V, F, r1, r2, path = klee_minty()
    P = Polytope(V, F, r1, r2, 215, (395, 330))
    assert frozenset((path[0], path[-1])) in P.edges  # start and optimum are joined by a single edge

    def base():
        return P.draw() + P.dots()

    def long_path(color, key):
        return [P.arrow(a, b, color, key, width=4) for a, b in zip(path, path[1:])]

    def numbers(color):
        out = []
        for k, i in enumerate(path[1:-1], start=1):
            p = P.px(i)
            out.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="10" fill="#fdf6e3" stroke="{color}" stroke-width="2"/>')
            out.append(f'<text x="{p[0]:.1f}" y="{p[1]+4.5:.1f}" font-size="13" fill="{color}" text-anchor="middle">{k}</text>')
        return out

    s = base() + long_path(RED, "red") + numbers(RED)
    s += P.mark(path[0], ORANGE, "start", dx=0, dy=26, anchor="middle")
    s += P.mark(path[-1], GREEN, "optimal", dx=0, dy=-14, anchor="middle")
    s.append(f'<text x="70" y="{H-16}" font-size="15" fill="{RED}">7 steps: every vertex is visited</text>')
    s += objective_arrow(22, 330, 70)
    write("news_long_path.svg", s, W, H)

    s = base() + long_path(RED, "red") + numbers(RED)
    s.append(P.arrow(path[0], path[-1], GREEN, "green", width=6, start_gap=9))
    s += P.mark(path[0], ORANGE, "start", dx=0, dy=26, anchor="middle")
    s += P.mark(path[-1], GREEN, "optimal", dx=0, dy=-14, anchor="middle")
    s.append(f'<text x="70" y="{H-36}" font-size="15" fill="{RED}">long path: 7 steps</text>')
    s.append(f'<text x="70" y="{H-14}" font-size="15" fill="{GREEN}">short path: 1 step</text>')
    s += objective_arrow(22, 330, 70)
    write("news_long_vs_short.svg", s, W, H)


polytope_walk()
polytope_directions()
cube_pictures()
