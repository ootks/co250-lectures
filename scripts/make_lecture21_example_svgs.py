#!/usr/bin/env python3
"""Generate the example pictures for lecture 21.

  cp21_example_cut.svg - the SEF cutting-plane example, drawn in the plane of
                         the nonbasic variables (x3, x4):
        x1 = 13/3 + (1/3) x3 - (7/3) x4 >= 0
        x2 = 10/3 - (5/3) x3 + (2/3) x4 >= 0
      The LP optimum x* is the origin and the cut x1 - x3 + 2 x4 <= 4 reads
      2 x3 + x4 >= 1.
  convex_x_squared.svg - f(x) = x^2 with a chord above the graph
  convex_exp.svg       - f(x) = e^x with a chord above the graph
  lasso_constrained.svg - level curves of a least squares objective touching
                          the l1 ball at a corner
"""

import math
import os
from fractions import Fraction as F
from itertools import product

INK = "#073642"
GRID = "#d8d0bb"
BLUE = "#268bd2"
GREEN = "#859900"
RED = "#dc322f"
ORANGE = "#cb4b16"
FAINT = "#93a1a1"
POLY_FILL = "rgba(38,139,210,0.12)"
RED_FILL = "rgba(220,50,47,0.18)"

IMAGES = os.path.join(os.path.dirname(__file__), "..", "images")


def write(name, body, w, h):
    path = os.path.join(IMAGES, name)
    with open(path, "w") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
                 f'width="{w}" height="{h}" font-family="Georgia, serif">\n'
                 + "\n".join(body) + "\n</svg>\n")
    print("wrote", os.path.normpath(path))


# ------------------------------------------------------------ cutting plane example
def cp21_example_cut():
    W, H = 480, 390
    OX, OY, UX, UY = 70, 340, 120, 120

    def px(a, b):
        return (OX + float(a) * UX, OY - float(b) * UY)

    def pts(corners):
        return " ".join(f"{px(a, b)[0]:.2f},{px(a, b)[1]:.2f}" for a, b in corners)

    def x1(x3, x4):
        return F(13, 3) + F(1, 3) * x3 - F(7, 3) * x4

    def x2(x3, x4):
        return F(10, 3) - F(5, 3) * x3 + F(2, 3) * x4

    poly = [(0, 0), (2, 0), (F(32, 11), F(25, 11)), (0, F(13, 7))]
    assert x2(2, 0) == 0 and x1(0, F(13, 7)) == 0
    assert x1(*poly[2]) == 0 and x2(*poly[2]) == 0

    int_pts = [(a, b) for a, b in product(range(4), range(4))
               if x1(a, b) >= 0 and x2(a, b) >= 0
               and x1(a, b).denominator == 1 and x2(a, b).denominator == 1]
    assert sorted(int_pts) == [(0, 1), (1, 2), (2, 0)]
    # the cut holds at every integer feasible point and fails at x* = origin
    for a, b in int_pts:
        assert x1(a, b) - a + 2 * b <= 4 and 2 * a + b >= 1
    assert x1(0, 0) > 4

    s = []
    for a in range(0, 4):
        for b in range(0, 3):
            x, y = px(a, b)
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="{GRID}"/>')
    x0, y0 = px(0, 0)
    xend, _ = px(3.3, 0)
    _, yend = px(0, 2.65)
    s.append(f'<line x1="{x0}" y1="{y0}" x2="{xend:.1f}" y2="{y0}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{yend:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{xend:.1f}" y="{y0-10}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">x&#8323;</text>')
    s.append(f'<text x="{x0-14}" y="{yend+6:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">x&#8324;</text>')
    for a in range(1, 4):
        x, y = px(a, 0)
        s.append(f'<text x="{x:.1f}" y="{y+20}" font-size="13" fill="{FAINT}" text-anchor="middle">{a}</text>')
    for b in range(1, 3):
        x, y = px(0, b)
        s.append(f'<text x="{x-12:.1f}" y="{y+4.5:.1f}" font-size="13" fill="{FAINT}" text-anchor="end">{b}</text>')

    s.append(f'<polygon points="{pts(poly)}" fill="{POLY_FILL}" stroke="{BLUE}" stroke-width="2.5"/>')
    s.append(f'<polygon points="{pts([(0, 0), (F(1, 2), 0), (0, 1)])}" fill="{RED_FILL}" stroke="{RED}" stroke-width="1.5"/>')
    for a, b in int_pts:
        x, y = px(a, b)
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{BLUE}"/>')

    # the cut 2 x3 + x4 = 1, extended a little past the polytope
    (ax, ay), (bx, by) = px(-0.12, 1.24), px(0.62, -0.24)
    s.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{GREEN}" stroke-width="3.5" stroke-linecap="round"/>')
    lx, ly = px(0.42, 0.62)
    s.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="14" fill="{GREEN}">x&#8321; &#8722; x&#8323; + 2x&#8324; &#8804; 4</text>')

    x, y = px(0, 0)
    s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{ORANGE}" stroke="#fff" stroke-width="1.5"/>')
    s.append(f'<text x="{x-10:.1f}" y="{y+20:.1f}" font-size="14" fill="{ORANGE}" text-anchor="end">x*</text>')
    write("cp21_example_cut.svg", s, W, H)


# ------------------------------------------------------------ chord pictures
def chord_picture(name, f, lo, hi, X, Y, lam, vmax, label, label_at, ticks):
    W, H = 420, 340
    ML, MR, MT, MB = 30, 20, 20, 40
    UX = (W - ML - MR) / (hi - lo)
    UY = (H - MT - MB) / vmax

    def px(t, v):
        return (ML + (t - lo) * UX, H - MB - v * UY)

    Z = lam * X + (1 - lam) * Y
    chord_z = lam * f(X) + (1 - lam) * f(Y)
    assert f(Z) <= chord_z

    s = []
    a, b = px(lo, 0), px(hi, 0)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    a, b = px(0, 0), px(0, vmax)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    for t in ticks:
        p = px(t, 0)
        s.append(f'<line x1="{p[0]:.1f}" y1="{p[1]-4:.1f}" x2="{p[0]:.1f}" y2="{p[1]+4:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
        s.append(f'<text x="{p[0]:.1f}" y="{p[1]+20:.1f}" font-size="13" fill="{FAINT}" text-anchor="middle">{str(t).replace("-", "&#8722;")}</text>')

    for t, top in ((X, f(X)), (Y, f(Y)), (Z, chord_z)):
        a, b = px(t, 0), px(t, top)
        s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                 f'stroke="{FAINT}" stroke-width="1.2" stroke-dasharray="4 5"/>')

    N = 160
    ts = [lo + i * (hi - lo) / N for i in range(N + 1)]
    curve = " ".join(f"{px(t, f(t))[0]:.1f},{px(t, f(t))[1]:.1f}" for t in ts if f(t) <= vmax)
    s.append(f'<polyline points="{curve}" fill="none" stroke="{BLUE}" stroke-width="3"/>')
    p = px(*label_at)
    s.append(f'<text x="{p[0]:.1f}" y="{p[1]:.1f}" font-size="17" font-style="italic" fill="{BLUE}" text-anchor="middle">{label}</text>')

    a, b = px(X, f(X)), px(Y, f(Y))
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GREEN}" stroke-width="3" stroke-linecap="round"/>')
    for p in (a, b):
        s.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="5" fill="{BLUE}"/>')
    c, g = px(Z, chord_z), px(Z, f(Z))
    s.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="6" fill="{GREEN}" stroke="#fff" stroke-width="1.5"/>')
    s.append(f'<circle cx="{g[0]:.1f}" cy="{g[1]:.1f}" r="6" fill="{ORANGE}" stroke="#fff" stroke-width="1.5"/>')
    write(name, s, W, H)


# ------------------------------------------------------------ constrained LASSO
def lasso_constrained():
    VIOLET = "#6c71c4"
    W, H = 400, 470
    LO1, HI1, LO2, HI2 = -1.7, 2.3, -1.5, 3.3
    U = 92
    MX = (W - (HI1 - LO1) * U) / 2
    MY = (H - (HI2 - LO2) * U) / 2

    def px(a, b):
        return (MX + (a - LO1) * U, H - MY - (b - LO2) * U)

    # f(theta) = (theta - c)^T Q (theta - c), Q positive definite
    q11, q12, q22 = 1.5, -0.5, 1.0
    c = (0.6, 2.2)

    def f(a, b):
        da, db = a - c[0], b - c[1]
        return q11 * da * da + 2 * q12 * da * db + q22 * db * db

    # the corner (0, 1) of the l1 ball minimizes f over the ball
    opt = (0.0, 1.0)
    N = 4000
    for i in range(N):
        t = 4 * i / N
        k, r = int(t), t - int(t)
        corners = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 0)]
        a = corners[k][0] * (1 - r) + corners[k + 1][0] * r
        b = corners[k][1] * (1 - r) + corners[k + 1][1] * r
        assert f(a, b) >= f(*opt) - 1e-12

    # eigen-decomposition of Q for drawing the level ellipses
    tr, det = q11 + q22, q11 * q22 - q12 * q12
    l1 = tr / 2 + math.sqrt(tr * tr / 4 - det)
    l2 = tr / 2 - math.sqrt(tr * tr / 4 - det)
    ang = math.atan2(l1 - q11, q12)  # direction of the eigenvector for l1

    s = []
    a, b = px(LO1, 0), px(HI1, 0)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{b[0]-4:.1f}" y="{b[1]+20:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">&#952;&#8321;</text>')
    a, b = px(0, LO2), px(0, HI2)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{b[0]-10:.1f}" y="{b[1]+16:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">&#952;&#8322;</text>')

    diamond = " ".join(f"{px(a, b)[0]:.1f},{px(a, b)[1]:.1f}" for a, b in [(1, 0), (0, 1), (-1, 0), (0, -1)])
    s.append(f'<polygon points="{diamond}" fill="{POLY_FILL}" stroke="{BLUE}" stroke-width="2.5"/>')
    p = px(-0.28, -0.22)
    s.append(f'<text x="{p[0]:.1f}" y="{p[1]:.1f}" font-size="15" fill="{BLUE}" text-anchor="middle">&#8214;&#952;&#8214;&#8321; &#8804; k</text>')

    cx, cy = px(*c)
    for v, wdt in ((0.25, 1.6), (0.65, 1.6), (f(*opt), 2.6), (2.1, 1.6)):
        rx, ry = math.sqrt(v / l1) * U, math.sqrt(v / l2) * U
        s.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none" stroke="{VIOLET}" '
                 f'stroke-width="{wdt}" transform="rotate({-math.degrees(ang):.2f} {cx:.1f} {cy:.1f})"/>')
    s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="{VIOLET}"/>')
    s.append(f'<text x="{cx+10:.1f}" y="{cy+5:.1f}" font-size="14" fill="{VIOLET}">least squares solution</text>')

    x, y = px(*opt)
    s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{ORANGE}" stroke="#fff" stroke-width="1.5"/>')
    s.append(f'<text x="{x-12:.1f}" y="{y-8:.1f}" font-size="14" fill="{ORANGE}" text-anchor="end">&#952;* = (0, k)</text>')
    write("lasso_constrained.svg", s, W, H)


# ------------------------------------------------------------ squared norm bowl
def squared_norm_bowl():
    """f(x) = x1^2 + x2^2 drawn as a bowl: a parabola profile with elliptical
    cross-sections (the level curves lifted to their heights)."""
    W, H = 420, 395
    CX, BASE = 210, 335          # screen position of the bottom of the bowl
    UR, UZ, SQ = 78, 62, 0.28    # radius scale, height scale, ellipse squash

    def px(r, z):
        return (CX + r * UR, BASE - z * UZ)

    s = []
    # axes: x1 to the right, x2 into the page (drawn obliquely), value upward
    o = px(0, 0)
    e1, e2, e3 = px(2.45, 0), (CX - 120, BASE + 44), px(0, 4.0)
    for e in (e1, e2, e3):
        s.append(f'<line x1="{o[0]:.1f}" y1="{o[1]:.1f}" x2="{e[0]:.1f}" y2="{e[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{e1[0]:.1f}" y="{e1[1]+20:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">x&#8321;</text>')
    s.append(f'<text x="{e2[0]+4:.1f}" y="{e2[1]-8:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">x&#8322;</text>')

    # back halves of the cross-sections, then the profile, then the front halves
    levels = [0.5, 1.0, 1.5, 2.0]
    for r in levels:
        c = px(0, r * r)
        s.append(f'<path d="M {c[0]-r*UR:.1f} {c[1]:.1f} A {r*UR:.1f} {r*UR*SQ:.1f} 0 0 1 {c[0]+r*UR:.1f} {c[1]:.1f}" '
                 f'fill="none" stroke="{BLUE}" stroke-width="1.3" stroke-opacity="0.45"/>')
    top = levels[-1]
    c = px(0, top * top)
    s.append(f'<ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="{top*UR:.1f}" ry="{top*UR*SQ:.1f}" fill="{BLUE}" fill-opacity="0.10"/>')
    N = 120
    prof = " ".join(f"{px(-top + 2 * top * i / N, (-top + 2 * top * i / N) ** 2)[0]:.1f},"
                    f"{px(-top + 2 * top * i / N, (-top + 2 * top * i / N) ** 2)[1]:.1f}" for i in range(N + 1))
    s.append(f'<polyline points="{prof}" fill="none" stroke="{BLUE}" stroke-width="3"/>')
    for r in levels:
        c = px(0, r * r)
        wdt = 3 if r == top else 1.8
        s.append(f'<path d="M {c[0]-r*UR:.1f} {c[1]:.1f} A {r*UR:.1f} {r*UR*SQ:.1f} 0 0 0 {c[0]+r*UR:.1f} {c[1]:.1f}" '
                 f'fill="none" stroke="{BLUE}" stroke-width="{wdt}"/>')
    s.append(f'<text x="{CX}" y="22" font-size="17" font-style="italic" fill="{BLUE}" text-anchor="middle">f(x) = x&#8321;&#178; + x&#8322;&#178;</text>')
    write("squared_norm_bowl.svg", s, W, H)


# ------------------------------------------------------------ subgradient
def subgradient_picture():
    """A convex function with a kink at xbar and an affine lower bound that
    touches the graph there."""
    W, H = 440, 340
    OX, OY, UX, UY = 40, 300, 90, 95

    def px(t, v):
        return (OX + t * UX, OY - v * UY)

    XB = 2.0

    def f(t):  # convex, with a kink at XB (slopes 0.2 on the left, 1.3 on the right there)
        return 0.9 + (0.25 * (t - XB) ** 2 + 0.2 * (t - XB) if t <= XB else 0.3 * (t - XB) ** 2 + 1.3 * (t - XB))

    SLOPE = 0.7

    def h(t):
        return f(XB) + SLOPE * (t - XB)

    lo, hi, N = 0.1, 3.75, 200
    ts = [lo + i * (hi - lo) / N for i in range(N + 1)] + [XB]
    ts.sort()
    assert all(f(t) >= h(t) - 1e-12 for t in ts)

    s = []
    a, b = px(0, 0), px(4.3, 0)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    a, b = px(XB, 0), px(XB, f(XB))
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.2" stroke-dasharray="4 5"/>')
    s.append(f'<text x="{a[0]:.1f}" y="{a[1]+22:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="middle">x&#8320;</text>')

    a, b = px(0.75, h(0.75)), px(4.1, h(4.1))
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GREEN}" stroke-width="3" stroke-linecap="round"/>')
    lp = px(2.3, 0.6)
    s.append(f'<text x="{lp[0]:.1f}" y="{lp[1]:.1f}" font-size="16" font-style="italic" fill="{GREEN}">h(x) = f(x&#8320;) + s&#7488;(x &#8722; x&#8320;)</text>')

    curve = " ".join(f"{px(t, f(t))[0]:.1f},{px(t, f(t))[1]:.1f}" for t in ts)
    s.append(f'<polyline points="{curve}" fill="none" stroke="{BLUE}" stroke-width="3" stroke-linejoin="round"/>')
    p = px(2.9, f(2.9))
    s.append(f'<text x="{p[0]-14:.1f}" y="{p[1]:.1f}" font-size="17" font-style="italic" fill="{BLUE}" text-anchor="end">f</text>')

    p = px(XB, f(XB))
    s.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="6" fill="{ORANGE}" stroke="#fff" stroke-width="1.5"/>')
    write("subgradient_definition.svg", s, W, H)


# ------------------------------------------------------------ gradient example
def gradient_example():
    """Level curves of f(x, y) = x^2 + y^2 with the gradient (2, 2) at (1, 1)."""
    W, H = 450, 400
    LO, HI = -2.3, 3.5
    U = (H - 40) / (HI - LO)

    def px(a, b):
        return (20 + (a - LO) * U, H - 20 - (b - LO) * U)

    s = ['<defs><marker id="arr" markerUnits="userSpaceOnUse" markerWidth="16" markerHeight="12" refX="13" refY="6" orient="auto">'
         f'<path d="M0,0 L16,6 L0,12 z" fill="{ORANGE}"/></marker></defs>']
    a, b = px(LO, 0), px(HI + 0.7, 0)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{b[0]-2:.1f}" y="{b[1]+20:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">x</text>')
    a, b = px(0, LO), px(0, HI)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{b[0]-10:.1f}" y="{b[1]+14:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">y</text>')
    for k in (1, 2, 3):
        p = px(k, 0)
        s.append(f'<text x="{p[0]:.1f}" y="{p[1]+18:.1f}" font-size="13" fill="{FAINT}" text-anchor="middle">{k}</text>')
        p = px(0, k)
        s.append(f'<text x="{p[0]-8:.1f}" y="{p[1]+4.5:.1f}" font-size="13" fill="{FAINT}" text-anchor="end">{k}</text>')

    c = px(0, 0)
    for v in (0.5, 1.0, 2.0):
        wdt = 2.6 if v == 2.0 else 1.5
        s.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{math.sqrt(v)*U:.1f}" fill="none" stroke="{BLUE}" stroke-width="{wdt}"/>')
    p = px(-1.0, -1.0)
    s.append(f'<text x="{p[0]-8:.1f}" y="{p[1]+18:.1f}" font-size="14" fill="{BLUE}" text-anchor="end">x&#178; + y&#178; = 2</text>')

    a, b = px(1, 1), px(3, 3)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{ORANGE}" stroke-width="3" marker-end="url(#arr)"/>')
    s.append(f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="5.5" fill="{ORANGE}" stroke="#fff" stroke-width="1.5"/>')
    s.append(f'<text x="{a[0]+10:.1f}" y="{a[1]+16:.1f}" font-size="14" fill="{ORANGE}">(1, 1)</text>')
    m = px(2.2, 1.6)
    s.append(f'<text x="{m[0]:.1f}" y="{m[1]:.1f}" font-size="15" fill="{ORANGE}">&#8711;f(1, 1) = (2, 2)</text>')
    write("gradient_example.svg", s, W, H)


# ------------------------------------------------------------ subgradients of |x| at 0
def abs_pictures():
    """abs_subgradient_zero.svg: |x| with the affine lower bound h = 0 at x = 0.
    abs_normal_cone.svg: epi(|x|) with its normal cone at the vertex (0, 0);
    the vectors (c, -1) with -1 <= c <= 1 lie in that cone."""
    W, H = 440, 400
    LO1, HI1, LO2, HI2 = -2.6, 2.6, -2.3, 2.5
    UX, UY = (W - 30) / (HI1 - LO1), (H - 30) / (HI2 - LO2)

    def px(a, b):
        return (15 + (a - LO1) * UX, H - 15 - (b - LO2) * UY)

    def axes(xlab, ylab):
        s = []
        a, b = px(LO1, 0), px(HI1, 0)
        s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
        s.append(f'<text x="{b[0]-2:.1f}" y="{b[1]+20:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">{xlab}</text>')
        a, b = px(0, LO2), px(0, HI2)
        s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
        if ylab:
            s.append(f'<text x="{b[0]-10:.1f}" y="{b[1]+14:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">{ylab}</text>')
        return s

    def graph():
        pts = " ".join(f"{px(a, abs(a))[0]:.1f},{px(a, abs(a))[1]:.1f}" for a in (-HI2, 0, HI2))
        return f'<polyline points="{pts}" fill="none" stroke="{BLUE}" stroke-width="3" stroke-linejoin="round"/>'

    o = px(0, 0)
    dot = f'<circle cx="{o[0]:.1f}" cy="{o[1]:.1f}" r="6" fill="{ORANGE}" stroke="#fff" stroke-width="1.5"/>'

    # --- 0 is a subgradient at 0
    s = axes("x", "")
    a, b = px(LO1 + 0.15, 0), px(HI1 - 0.15, 0)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GREEN}" stroke-width="3.5" stroke-linecap="round"/>')
    p = px(-2.4, 0)
    s.append(f'<text x="{p[0]:.1f}" y="{p[1]+24:.1f}" font-size="16" font-style="italic" fill="{GREEN}">h(x) = 0</text>')
    s.append(graph())
    p = px(1.5, 1.5)
    s.append(f'<text x="{p[0]-14:.1f}" y="{p[1]-8:.1f}" font-size="17" font-style="italic" fill="{BLUE}" text-anchor="end">f(x) = |x|</text>')
    s.append(dot)
    write("abs_subgradient_zero.svg", s, W, H)

    # --- the normal cone of epi(|x|) at its vertex
    s = ['<defs><marker id="arrc" markerUnits="userSpaceOnUse" markerWidth="16" markerHeight="12" refX="13" refY="6" orient="auto">'
         f'<path d="M0,0 L16,6 L0,12 z" fill="{ORANGE}"/></marker></defs>']
    epi = " ".join(f"{px(a, b)[0]:.1f},{px(a, b)[1]:.1f}" for a, b in [(-HI2, HI2), (0, 0), (HI2, HI2)])
    s.append(f'<polygon points="{epi}" fill="{BLUE}" fill-opacity="0.16"/>')
    R = -LO2
    cone = " ".join(f"{px(a, b)[0]:.1f},{px(a, b)[1]:.1f}" for a, b in [(-R, -R), (0, 0), (R, -R)])
    s.append(f'<polygon points="{cone}" fill="{GREEN}" fill-opacity="0.20"/>')
    s += axes("x", "t")
    for sign in (-1, 1):
        a, b = px(0, 0), px(sign * R, -R)
        s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GREEN}" stroke-width="2.5"/>')
    s.append(graph())
    p = px(0, 1.9)
    s.append(f'<text x="{p[0]+12:.1f}" y="{p[1]:.1f}" font-size="17" fill="{BLUE}">epi(<tspan font-style="italic">f</tspan>)</text>')
    p = px(0, -2.0)
    s.append(f'<text x="{p[0]+12:.1f}" y="{p[1]:.1f}" font-size="16" fill="{GREEN}">normal cone</text>')
    # the level t = -1, where the cone is the segment of subgradients [-1, 1]
    a, b = px(-1, -1), px(1, -1)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{ORANGE}" stroke-width="4" stroke-linecap="round"/>')
    for c in (-1, 1):
        q = px(c, -1)
        s.append(f'<text x="{q[0] + (14 if c > 0 else -14):.1f}" y="{q[1]+5:.1f}" font-size="14" fill="{ORANGE}" text-anchor="{"start" if c > 0 else "end"}">({str(c).replace("-", "&#8722;")}, &#8722;1)</text>')
    C = 0.45
    a, b = px(0, 0), px(C, -1)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{ORANGE}" stroke-width="3" marker-end="url(#arrc)"/>')
    s.append(f'<text x="{b[0]-4:.1f}" y="{b[1]+22:.1f}" font-size="14" fill="{ORANGE}" text-anchor="middle">(c, &#8722;1)</text>')
    s.append(dot)
    write("abs_normal_cone.svg", s, W, H)


# ------------------------------------------------------------ subgradient of e^x at 0
def exp_subgradient():
    """e^x with its affine lower bound h(x) = 1 + x at x = 0."""
    W, H = 440, 380
    LO1, HI1, LO2, HI2 = -2.6, 2.1, -1.4, 5.6

    UX, UY = (W - 30) / (HI1 - LO1), (H - 30) / (HI2 - LO2)

    def px(a, b):
        return (15 + (a - LO1) * UX, H - 15 - (b - LO2) * UY)

    N = 200
    ts = [LO1 + i * (HI1 - LO1) / N for i in range(N + 1)]
    assert all(math.exp(t) >= 1 + t - 1e-12 for t in ts)

    s = []
    a, b = px(LO1, 0), px(HI1, 0)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{b[0]-2:.1f}" y="{b[1]+20:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">x</text>')
    a, b = px(0, LO2), px(0, HI2)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    for k in (-2, -1, 1):
        p = px(k, 0)
        s.append(f'<line x1="{p[0]:.1f}" y1="{p[1]-4:.1f}" x2="{p[0]:.1f}" y2="{p[1]+4:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
        s.append(f'<text x="{p[0]:.1f}" y="{p[1]+20:.1f}" font-size="13" fill="{FAINT}" text-anchor="middle">{str(k).replace("-", "&#8722;")}</text>')

    # the affine lower bound h(x) = 1 + x, clipped to the window
    x_lo, x_hi = LO2 - 1, HI1
    a, b = px(x_lo, 1 + x_lo), px(x_hi, 1 + x_hi)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GREEN}" stroke-width="3" stroke-linecap="round"/>')
    p = px(0.75, 0.95)
    s.append(f'<text x="{p[0]:.1f}" y="{p[1]:.1f}" font-size="16" font-style="italic" fill="{GREEN}">h(x) = 1 + x</text>')

    curve = " ".join(f"{px(t, math.exp(t))[0]:.1f},{px(t, math.exp(t))[1]:.1f}" for t in ts if math.exp(t) <= HI2)
    s.append(f'<polyline points="{curve}" fill="none" stroke="{BLUE}" stroke-width="3"/>')
    p = px(1.25, 4.6)
    s.append(f'<text x="{p[0]-14:.1f}" y="{p[1]:.1f}" font-size="17" font-style="italic" fill="{BLUE}" text-anchor="end">f(x) = e&#739;</text>')

    p = px(0, 1)
    s.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="6" fill="{ORANGE}" stroke="#fff" stroke-width="1.5"/>')
    s.append(f'<text x="{p[0]-12:.1f}" y="{p[1]-10:.1f}" font-size="14" fill="{ORANGE}" text-anchor="end">(0, 1)</text>')
    write("exp_subgradient.svg", s, W, H)


# ------------------------------------------------------------ subgradients of e^x at many points
def exp_subgradients_many():
    """e^x with its affine lower bounds h(x) = e^{x0} + e^{x0} (x - x0) at the
    regularly spaced points x0 = -2, -1.5, ..., 1.5."""
    W, H = 520, 420
    LO1, HI1, LO2, HI2 = -2.7, 2.1, -1.2, 6.2
    UX, UY = (W - 30) / (HI1 - LO1), (H - 30) / (HI2 - LO2)
    POINTS = [-2 + 0.5 * k for k in range(8)]

    def px(a, b):
        return (15 + (a - LO1) * UX, H - 15 - (b - LO2) * UY)

    N = 240
    ts = [LO1 + i * (HI1 - LO1) / N for i in range(N + 1)]
    for x0 in POINTS:
        assert all(math.exp(t) >= math.exp(x0) * (1 + t - x0) - 1e-12 for t in ts)

    s = [f'<clipPath id="expwin"><rect x="15" y="15" width="{W-30}" height="{H-30}"/></clipPath>']
    a, b = px(LO1, 0), px(HI1, 0)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{b[0]-2:.1f}" y="{b[1]+20:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">x</text>')
    a, b = px(0, LO2), px(0, HI2)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    for k in (-2, -1, 1):
        p = px(k, 0)
        s.append(f'<line x1="{p[0]:.1f}" y1="{p[1]-4:.1f}" x2="{p[0]:.1f}" y2="{p[1]+4:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
        s.append(f'<text x="{p[0]:.1f}" y="{p[1]+20:.1f}" font-size="13" fill="{FAINT}" text-anchor="middle">{str(k).replace("-", "&#8722;")}</text>')

    # the affine lower bounds, clipped to the window
    for x0 in POINTS:
        m = math.exp(x0)
        a, b = px(LO1, m * (1 + LO1 - x0)), px(HI1, m * (1 + HI1 - x0))
        s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GREEN}" stroke-width="1.8" '
                 f'stroke-opacity="0.85" clip-path="url(#expwin)"/>')

    curve = " ".join(f"{px(t, math.exp(t))[0]:.1f},{px(t, math.exp(t))[1]:.1f}" for t in ts if math.exp(t) <= HI2)
    s.append(f'<polyline points="{curve}" fill="none" stroke="{BLUE}" stroke-width="3"/>')
    p = px(1.35, 5.3)
    s.append(f'<text x="{p[0]-14:.1f}" y="{p[1]:.1f}" font-size="17" font-style="italic" fill="{BLUE}" text-anchor="end">f(x) = e&#739;</text>')

    for x0 in POINTS:
        p = px(x0, math.exp(x0))
        s.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4.5" fill="{ORANGE}" stroke="#fff" stroke-width="1.2"/>')
    write("exp_subgradients_many.svg", s, W, H)


# ------------------------------------------------------------ e^x + |x|
def exp_plus_abs(name="exp_plus_abs.svg", show_min=False):
    """The graph of f(x) = e^x + |x|, which has a kink at x = 0. With show_min,
    also the affine lower bound h(y) = 1 (the subgradient 0 at x = 0) and the
    minimizer."""
    W, H = 440, 380
    LO1, HI1, LO2, HI2 = -2.6, 2.0, -0.7, 5.2
    UX, UY = (W - 30) / (HI1 - LO1), (H - 30) / (HI2 - LO2)

    def f(t):
        return math.exp(t) + abs(t)

    def px(a, b):
        return (15 + (a - LO1) * UX, H - 15 - (b - LO2) * UY)

    s = []
    a, b = px(LO1, 0), px(HI1, 0)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{b[0]-2:.1f}" y="{b[1]+20:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">x</text>')
    a, b = px(0, LO2), px(0, HI2)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    for k in (-2, -1, 1):
        p = px(k, 0)
        s.append(f'<line x1="{p[0]:.1f}" y1="{p[1]-4:.1f}" x2="{p[0]:.1f}" y2="{p[1]+4:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
        s.append(f'<text x="{p[0]:.1f}" y="{p[1]+20:.1f}" font-size="13" fill="{FAINT}" text-anchor="middle">{str(k).replace("-", "&#8722;")}</text>')
    for k in (1, 2, 3, 4, 5):
        p = px(0, k)
        s.append(f'<line x1="{p[0]-4:.1f}" y1="{p[1]:.1f}" x2="{p[0]+4:.1f}" y2="{p[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
        s.append(f'<text x="{p[0]+10:.1f}" y="{p[1]+4.5:.1f}" font-size="13" fill="{FAINT}">{k}</text>')

    N = 240
    ts = sorted([LO1 + i * (HI1 - LO1) / N for i in range(N + 1)] + [0.0])
    curve = " ".join(f"{px(t, f(t))[0]:.1f},{px(t, f(t))[1]:.1f}" for t in ts if f(t) <= HI2)
    s.append(f'<polyline points="{curve}" fill="none" stroke="{BLUE}" stroke-width="3" stroke-linejoin="round"/>')
    p = px(-1.2, 3.6)
    s.append(f'<text x="{p[0]:.1f}" y="{p[1]:.1f}" font-size="17" font-style="italic" fill="{BLUE}" text-anchor="middle">f(x) = e&#739; + |x|</text>')
    if show_min:
        a, b = px(LO1 + 0.1, 1), px(HI1 - 0.1, 1)
        s.insert(len(s) - 2, f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GREEN}" stroke-width="3" stroke-linecap="round"/>')
        p = px(-2.45, 1)
        s.append(f'<text x="{p[0]:.1f}" y="{p[1]+22:.1f}" font-size="16" font-style="italic" fill="{GREEN}">h(x) = 1</text>')
        p = px(0, 1)
        s.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="6" fill="{ORANGE}" stroke="#fff" stroke-width="1.5"/>')
        s.append(f'<text x="{p[0]+12:.1f}" y="{p[1]+22:.1f}" font-size="14" fill="{ORANGE}">minimizer x&#8320; = 0</text>')
    write(name, s, W, H)


# ------------------------------------------------------------ a smooth convex function of two variables
def quadratic_two_variables():
    """Level curves of f(x, y) = x^2 + xy + y^2 - 3x, whose gradient
    (2x + y - 3, x + 2y) vanishes at the minimizer (2, -1), where f = -3."""
    W, H = 440, 400
    LO1, HI1, LO2, HI2 = -1.2, 5.0, -3.9, 1.9
    U = (W - 30) / (HI1 - LO1)

    def f(a, b):
        return a * a + a * b + b * b - 3 * a

    def px(a, b):
        return (15 + (a - LO1) * U, 15 + (HI2 - b) * U)

    C = (2.0, -1.0)
    assert abs(2 * C[0] + C[1] - 3) < 1e-12 and abs(C[0] + 2 * C[1]) < 1e-12 and abs(f(*C) + 3) < 1e-12
    # f(x, y) - f(2, -1) = u^2 + uv + v^2 with (u, v) = (x - 2, y + 1): eigenvalues 3/2 along (1, 1), 1/2 along (1, -1)
    for a, b in ((0.3, 1.1), (4.0, -2.5), (-1.0, 0.0)):
        u, v = a - C[0], b - C[1]
        assert abs(f(a, b) - f(*C) - (u * u + u * v + v * v)) < 1e-12

    s = []
    a, b = px(LO1, 0), px(HI1, 0)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{b[0]-2:.1f}" y="{b[1]-8:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">x</text>')
    a, b = px(0, LO2), px(0, HI2)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{b[0]-10:.1f}" y="{b[1]+14:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">y</text>')
    for k in (1, 2, 3, 4):
        p = px(k, 0)
        s.append(f'<line x1="{p[0]:.1f}" y1="{p[1]-4:.1f}" x2="{p[0]:.1f}" y2="{p[1]+4:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
        s.append(f'<text x="{p[0]:.1f}" y="{p[1]-9:.1f}" font-size="13" fill="{FAINT}" text-anchor="middle">{k}</text>')
    for k in (-3, -2, -1, 1):
        p = px(0, k)
        s.append(f'<line x1="{p[0]-4:.1f}" y1="{p[1]:.1f}" x2="{p[0]+4:.1f}" y2="{p[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
        s.append(f'<text x="{p[0]-10:.1f}" y="{p[1]+4.5:.1f}" font-size="13" fill="{FAINT}" text-anchor="end">{str(k).replace("-", "&#8722;")}</text>')

    c = px(*C)
    for level in (0.25, 1.0, 2.25, 4.0):
        r_long, r_short = math.sqrt(level / 0.5) * U, math.sqrt(level / 1.5) * U
        # the long axis is along (1, -1), which points down-right on screen: rotate by +45 degrees
        s.append(f'<ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="{r_long:.1f}" ry="{r_short:.1f}" fill="none" stroke="{BLUE}" '
                 f'stroke-width="1.8" transform="rotate(45 {c[0]:.1f} {c[1]:.1f})"/>')
    p = px(3.55, 0.75)
    s.append(f'<text x="{p[0]:.1f}" y="{p[1]:.1f}" font-size="15" fill="{BLUE}" text-anchor="middle">level curves of f</text>')

    s.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="6" fill="{ORANGE}" stroke="#fff" stroke-width="1.5"/>')
    s.append(f'<text x="{c[0]:.1f}" y="{c[1]-11:.1f}" font-size="14" fill="{ORANGE}" text-anchor="middle">(2, &#8722;1)</text>')
    write("quadratic_two_variables.svg", s, W, H)


# ------------------------------------------------------------ subgradients of e^x + |x| away from 0
def exp_plus_abs_subgradients():
    """The subgradient of f(x) = e^x + |x| at each x != 0, as a function of x:
    e^x - 1 for x < 0 and e^x + 1 for x > 0."""
    W, H = 440, 380
    LO1, HI1, LO2, HI2 = -2.6, 1.7, -1.6, 5.4
    UX, UY = (W - 30) / (HI1 - LO1), (H - 30) / (HI2 - LO2)
    RED = "#dc322f"

    def px(a, b):
        return (15 + (a - LO1) * UX, H - 15 - (b - LO2) * UY)

    s = []
    a, b = px(LO1, 0), px(HI1, 0)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{b[0]-2:.1f}" y="{b[1]+20:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">x&#8320;</text>')
    a, b = px(0, LO2), px(0, HI2)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    for k in (-2, -1, 1):
        p = px(k, 0)
        s.append(f'<line x1="{p[0]:.1f}" y1="{p[1]-4:.1f}" x2="{p[0]:.1f}" y2="{p[1]+4:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
        s.append(f'<text x="{p[0]:.1f}" y="{p[1]+20:.1f}" font-size="13" fill="{FAINT}" text-anchor="middle">{str(k).replace("-", "&#8722;")}</text>')
    for k in (-1, 1, 2, 3, 4, 5):
        p = px(0, k)
        s.append(f'<line x1="{p[0]-4:.1f}" y1="{p[1]:.1f}" x2="{p[0]+4:.1f}" y2="{p[1]:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
        s.append(f'<text x="{p[0]-10:.1f}" y="{p[1]+4.5:.1f}" font-size="13" fill="{FAINT}" text-anchor="end">{str(k).replace("-", "&#8722;")}</text>')

    N = 120
    left = [LO1 + i * (0 - LO1) / N for i in range(N + 1)]
    right = [i * HI1 / N for i in range(N + 1)]
    assert all(math.exp(t) - 1 < 0 for t in left[:-1]) and all(math.exp(t) + 1 > 0 for t in right)
    c1 = " ".join(f"{px(t, math.exp(t) - 1)[0]:.1f},{px(t, math.exp(t) - 1)[1]:.1f}" for t in left)
    c2 = " ".join(f"{px(t, math.exp(t) + 1)[0]:.1f},{px(t, math.exp(t) + 1)[1]:.1f}" for t in right if math.exp(t) + 1 <= HI2)
    s.append(f'<polyline points="{c1}" fill="none" stroke="{RED}" stroke-width="3"/>')
    s.append(f'<polyline points="{c2}" fill="none" stroke="{RED}" stroke-width="3"/>')
    for v in (0, 2):
        p = px(0, v)
        s.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="5.5" fill="#fdf6e3" stroke="{RED}" stroke-width="2.5"/>')
    p = px(-1.3, -0.73)
    s.append(f'<text x="{p[0]:.1f}" y="{p[1]+26:.1f}" font-size="16" font-style="italic" fill="{RED}" text-anchor="middle">s = e<tspan dy="-7" font-size="11">x&#8320;</tspan><tspan dy="7"> &#8722; 1 &lt; 0</tspan></text>')
    p = px(0.5, 1.45)
    s.append(f'<text x="{p[0]:.1f}" y="{p[1]:.1f}" font-size="16" font-style="italic" fill="{RED}">s = e<tspan dy="-7" font-size="11">x&#8320;</tspan><tspan dy="7"> + 1 &gt; 0</tspan></text>')
    p = px((LO1 + HI1) / 2, HI2)
    s.append(f'<text x="{px(-1.4, 0)[0]:.1f}" y="{p[1]+14:.1f}" font-size="16" fill="{RED}" text-anchor="middle">subgradient of f at x&#8320;</text>')
    write("exp_plus_abs_subgradients.svg", s, W, H)


# ------------------------------------------------------------ a non-convex function
def nonconvex_function_chord():
    """A function that is not convex: a chord that dips below the graph.
    Same layout as convex_function_chord.svg."""
    W, H = 480, 340
    OX, OY, UX, UY = 50, 300, 95, 120
    RED = "#dc322f"

    def f(t):
        return ((t - 2.3) ** 2 - 1) ** 2 + 0.5

    def px(t, v):
        return (OX + t * UX, OY - v * UY)

    X, Y, LAM = 1.3, 3.3, 0.5
    Z = LAM * X + (1 - LAM) * Y
    CHORD_Z = LAM * f(X) + (1 - LAM) * f(Y)
    assert f(Z) > CHORD_Z   # the convexity inequality fails

    s = []
    x0, y0 = px(0, 0)
    s.append(f'<line x1="{x0}" y1="{y0}" x2="{px(4.4, 0)[0]:.1f}" y2="{y0}" stroke="{FAINT}" stroke-width="1.5"/>')
    for t, top in ((X, f(X)), (Y, f(Y)), (Z, f(Z))):
        a, b = px(t, 0), px(t, top)
        s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                 f'stroke="{FAINT}" stroke-width="1.2" stroke-dasharray="4 5"/>')

    lo, hi, N = 0.82, 3.78, 160
    pts = " ".join(f"{px(lo + i * (hi - lo) / N, f(lo + i * (hi - lo) / N))[0]:.1f},"
                   f"{px(lo + i * (hi - lo) / N, f(lo + i * (hi - lo) / N))[1]:.1f}" for i in range(N + 1))
    s.append(f'<polyline points="{pts}" fill="none" stroke="{BLUE}" stroke-width="3"/>')
    gx, gy = px(hi, f(hi))
    s.append(f'<text x="{gx+10:.1f}" y="{gy+6:.1f}" font-size="16" font-style="italic" fill="{BLUE}">f</text>')

    a, b = px(X, f(X)), px(Y, f(Y))
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{RED}" stroke-width="3" stroke-linecap="round"/>')
    for p in (a, b):
        s.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="5" fill="{BLUE}"/>')

    c, g = px(Z, CHORD_Z), px(Z, f(Z))
    s.append(f'<circle cx="{g[0]:.1f}" cy="{g[1]:.1f}" r="6" fill="{ORANGE}" stroke="#fff" stroke-width="1.5"/>')
    s.append(f'<text x="{g[0]:.1f}" y="{g[1]-16:.1f}" font-size="15" fill="{ORANGE}" text-anchor="middle">f(&#955;x + (1 &#8722; &#955;)y)</text>')
    s.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="6" fill="{RED}" stroke="#fff" stroke-width="1.5"/>')
    s.append(f'<text x="{c[0]:.1f}" y="{c[1]+26:.1f}" font-size="15" fill="{RED}" text-anchor="middle">&#955;f(x) + (1 &#8722; &#955;)f(y)</text>')

    for t, lab in ((X, "x"), (Y, "y")):
        p = px(t, 0)
        s.append(f'<line x1="{p[0]:.1f}" y1="{p[1]-4}" x2="{p[0]:.1f}" y2="{p[1]+4}" stroke="{FAINT}" stroke-width="1.5"/>')
        s.append(f'<text x="{p[0]:.1f}" y="{p[1]+22}" font-size="15" font-style="italic" fill="{INK}" text-anchor="middle">{lab}</text>')
    write("nonconvex_function_chord.svg", s, W, H)


cp21_example_cut()
lasso_constrained()
nonconvex_function_chord()
exp_plus_abs_subgradients()
quadratic_two_variables()
exp_plus_abs()
exp_plus_abs("exp_plus_abs_min.svg", show_min=True)
exp_subgradients_many()
exp_subgradient()
abs_pictures()
gradient_example()
subgradient_picture()
squared_norm_bowl()
chord_picture("convex_x_squared.svg", lambda t: t * t, -2.05, 2.05, -1.2, 1.8, 0.45, 4.2,
              "f(x) = x&#178;", (-1.25, 3.7), [-2, -1, 1, 2])
chord_picture("convex_exp.svg", math.exp, -2.6, 1.55, -1.6, 1.3, 0.62, 4.4,
              "f(x) = e&#739;", (0.55, 3.9), [-2, -1, 1])
