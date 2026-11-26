#!/usr/bin/env python3
"""Generate the epigraph pictures for the convex functions section (lecture 21):
  epigraph_convex.svg  - epigraph of a convex function with a segment inside it
  pwl_function.svg     - f(x) = max{-x, x/2, 2x - 3} as a maximum of three lines
  pwl_epigraph.svg     - its epigraph as an intersection of three halfspaces
"""

import os

INK = "#073642"
BLUE = "#268bd2"
GREEN = "#859900"
ORANGE = "#cb4b16"
VIOLET = "#6c71c4"
FAINT = "#93a1a1"

IMAGES = os.path.join(os.path.dirname(__file__), "..", "images")


def write(name, body, w, h):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
         f'width="{w}" height="{h}" font-family="Georgia, serif">'] + body + ["</svg>"]
    path = os.path.join(IMAGES, name)
    with open(path, "w") as fh:
        fh.write("\n".join(s) + "\n")
    print("wrote", os.path.normpath(path))


def fmt(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


# ---------------------------------------------------------------- epigraph_convex
def epigraph_convex():
    W, H = 480, 340
    OX, OY, UX, UY = 50, 300, 85, 110
    TOP = 2.55

    def f(t):
        return 0.35 * (t - 2.2) ** 2 + 0.6

    def px(t, v):
        return (OX + t * UX, OY - v * UY)

    lo, hi, N = 0.15, 4.45, 120
    xs = [lo + i * (hi - lo) / N for i in range(N + 1)]
    curve = [px(t, min(f(t), TOP)) for t in xs if f(t) <= TOP]
    # clip the curve at the top of the picture
    import math
    r = math.sqrt((TOP - 0.6) / 0.35)
    a, b = 2.2 - r, 2.2 + r
    a, b = max(a, lo), min(b, hi)
    xs = [a + i * (b - a) / N for i in range(N + 1)]
    curve = [px(t, f(t)) for t in xs]

    s = []
    region = [px(a, TOP)] + curve + [px(b, TOP)]
    s.append(f'<polygon points="{fmt(region)}" fill="{BLUE}" fill-opacity="0.16"/>')
    x0, y0 = px(0, 0)
    s.append(f'<line x1="{x0}" y1="{y0}" x2="{px(4.9, 0)[0]:.1f}" y2="{y0}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{px(0, 2.6)[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{px(4.9, 0)[0]-4:.1f}" y="{y0+22}" font-size="15" font-style="italic" fill="{INK}" text-anchor="end">x</text>')
    s.append(f'<text x="{x0-12}" y="{px(0, 2.5)[1]:.1f}" font-size="15" font-style="italic" fill="{INK}" text-anchor="end">t</text>')
    s.append(f'<polyline points="{fmt(curve)}" fill="none" stroke="{BLUE}" stroke-width="3"/>')
    gx, gy = px(3.35, f(3.35))
    s.append(f'<text x="{gx+14:.1f}" y="{gy+14:.1f}" font-size="16" font-style="italic" fill="{BLUE}">t = f(x)</text>')
    s.append(f'<text x="{px(2.2, 2.25)[0]:.1f}" y="{px(2.2, 2.25)[1]:.1f}" font-size="17" fill="{BLUE}" text-anchor="middle">epi(<tspan font-style="italic">f</tspan>)</text>')

    # two points of the epigraph and the segment between them
    P, Q = (1.0, 1.75), (3.3, 1.5)
    assert P[1] >= f(P[0]) and Q[1] >= f(Q[0])
    p, q = px(*P), px(*Q)
    s.append(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" stroke="{GREEN}" stroke-width="3" stroke-linecap="round"/>')
    for (c, lab, dx, dy, anchor) in ((p, "(x, s)", -10, -10, "end"), (q, "(y, t)", 0, 24, "middle")):
        s.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="5.5" fill="{GREEN}" stroke="#fff" stroke-width="1.5"/>')
        s.append(f'<text x="{c[0]+dx:.1f}" y="{c[1]+dy:.1f}" font-size="15" font-style="italic" fill="{GREEN}" text-anchor="{anchor}">{lab}</text>')
    write("epigraph_convex.svg", s, W, H)


# ---------------------------------------------------------------- piecewise linear
LINES = [  # (slope, intercept, colour, label)
    (-1.0, 0.0, ORANGE, "t = &#8722;x"),
    (0.5, 0.0, GREEN, "t = &#189;x"),
    (2.0, -3.0, VIOLET, "t = 2x &#8722; 3"),
]
W2, H2 = 480, 360
XLO, XHI, TLO, THI = -2.3, 3.2, -0.9, 3.2
MX, MY = 30, 24
UX2 = (W2 - 2 * MX) / (XHI - XLO)
UY2 = (H2 - 2 * MY) / (THI - TLO)


def px2(x, t):
    return (MX + (x - XLO) * UX2, H2 - MY - (t - TLO) * UY2)


def fpwl(x):
    return max(m * x + c for m, c, _, _ in LINES)


def clip_line(m, c):
    """Endpoints of t = m x + c inside the plotting window."""
    pts = []
    for x in (XLO, XHI):
        t = m * x + c
        if TLO <= t <= THI:
            pts.append((x, t))
    for t in (TLO, THI):
        x = (t - c) / m
        if XLO < x < XHI:
            pts.append((x, t))
    pts.sort()
    return pts[0], pts[-1]


def axes():
    s = []
    a, b = px2(XLO, 0), px2(XHI, 0)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    a, b = px2(0, TLO), px2(0, THI)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    for k in range(-2, 4):
        if k == 0:
            continue
        p = px2(k, 0)
        s.append(f'<line x1="{p[0]:.1f}" y1="{p[1]-4:.1f}" x2="{p[0]:.1f}" y2="{p[1]+4:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
        s.append(f'<text x="{p[0]:.1f}" y="{p[1]+20:.1f}" font-size="13" fill="{INK}" text-anchor="middle">{str(k).replace("-", "&#8722;")}</text>')
    for k in range(1, 4):
        p = px2(0, k)
        s.append(f'<line x1="{p[0]-4:.1f}" y1="{p[1]:.1f}" x2="{p[0]+4:.1f}" y2="{p[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
        s.append(f'<text x="{p[0]-10:.1f}" y="{p[1]+5:.1f}" font-size="13" fill="{INK}" text-anchor="end">{k}</text>')
    p = px2(XHI, 0)
    s.append(f'<text x="{p[0]-2:.1f}" y="{p[1]-8:.1f}" font-size="15" font-style="italic" fill="{INK}" text-anchor="end">x</text>')
    p = px2(0, THI)
    s.append(f'<text x="{p[0]+10:.1f}" y="{p[1]+12:.1f}" font-size="15" font-style="italic" fill="{INK}">t</text>')
    return s


def dashed_lines():
    s = []
    for m, c, col, _ in LINES:
        a, b = clip_line(m, c)
        a, b = px2(*a), px2(*b)
        s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{col}" stroke-width="2" stroke-dasharray="6 5"/>')
    return s


# label positions (x, t, anchor) chosen clear of the graph
LABELS = [(-1.65, 1.05, "end"), (-1.05, -0.72, "start"), (1.62, -0.55, "start")]


def line_labels():
    s = []
    for (m, c, col, lab), (x, t, anchor) in zip(LINES, LABELS):
        p = px2(x, t)
        s.append(f'<text x="{p[0]:.1f}" y="{p[1]:.1f}" font-size="15" font-style="italic" fill="{col}" text-anchor="{anchor}">{lab}</text>')
    return s


def graph_points():
    # breakpoints at x = 0 and x = 2; ends where the graph leaves the window
    left = ((-THI), THI) if -THI >= XLO else (XLO, -XLO)
    right = ((THI + 3) / 2, THI) if (THI + 3) / 2 <= XHI else (XHI, 2 * XHI - 3)
    pts = [left, (0, 0), (2, 1), right]
    for x, t in pts:
        assert abs(fpwl(x) - t) < 1e-9
    return pts


def pwl_function():
    s = axes() + dashed_lines() + line_labels()
    g = [px2(*p) for p in graph_points()]
    s.append(f'<polyline points="{fmt(g)}" fill="none" stroke="{BLUE}" stroke-width="3.5" stroke-linejoin="round"/>')
    for bp in ((0, 0), (2, 1)):
        p = px2(*bp)
        s.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4.5" fill="{BLUE}"/>')
    p = px2(1.0, 1.25)
    s.append(f'<text x="{p[0]:.1f}" y="{p[1]:.1f}" font-size="17" font-style="italic" fill="{BLUE}" text-anchor="middle">f</text>')
    write("pwl_function.svg", s, W2, H2)


def pwl_epigraph():
    gp = graph_points()
    region = [px2(*p) for p in gp]
    # close the region along the top of the window
    closed = [px2(gp[0][0], THI)] + region + [px2(gp[-1][0], THI)]
    s = [f'<polygon points="{fmt(closed)}" fill="{BLUE}" fill-opacity="0.18"/>']
    s += axes() + dashed_lines() + line_labels()
    s.append(f'<polyline points="{fmt(region)}" fill="none" stroke="{BLUE}" stroke-width="3.5" stroke-linejoin="round"/>')
    p = px2(0.75, 2.2)
    s.append(f'<text x="{p[0]:.1f}" y="{p[1]:.1f}" font-size="17" fill="{BLUE}" text-anchor="middle">epi(<tspan font-style="italic">f</tspan>)</text>')
    write("pwl_epigraph.svg", s, W2, H2)


epigraph_convex()
pwl_function()
pwl_epigraph()
