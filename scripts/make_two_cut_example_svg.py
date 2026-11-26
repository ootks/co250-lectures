#!/usr/bin/env python3
"""Figure for the lecture-20 'Review: Example' slide.

IP:  max x1 + x2
     s.t. 3 x1 +  x2 <= 5
           x1 + 3 x2 <= 4
          x1, x2 >= 0, integer
LP optimum (11/8, 7/8); after the cut x1 + x2 <= 2 the LP optimum is (3/2, 1/2);
after the second cut x1 <= 1 the LP optimum is the integer point (1, 1).

The figure shows the LP feasible region (blue), the integer feasible points,
the LP optimum, and the two cuts x1 + x2 <= 2 and x1 <= 1, with the final
convex-hull-trimmed region shaded green.
"""

import os
from fractions import Fraction as F

INK = "#073642"
GRID = "#d8d0bb"
BLUE = "#268bd2"
GREEN = "#859900"
RED = "#dc322f"
ORANGE = "#cb4b16"
FAINT = "#93a1a1"
POLY_FILL = "rgba(38,139,210,0.12)"
HULL_FILL = "rgba(133,153,0,0.16)"

VB_W, VB_H = 440, 400
OX, OY = 70, 330           # pixel location of data origin
UX, UY = 150, 150          # pixels per unit (region is small, 0..~1.7)
X1_AX, X2_AX = 2.0, 2.0


def px(a, b):
    return (OX + float(a) * UX, OY - float(b) * UY)


# LP feasible region corners (CCW): (0,0), (5/3,0), (11/8,7/8), (0,4/3)
LP_POLY = [(F(0), F(0)), (F(5, 3), F(0)), (F(11, 8), F(7, 8)), (F(0), F(4, 3))]
# final region after both cuts: intersect LP region with x1+x2<=2 (nonbinding
# here) and x1<=1. Corners: (0,0),(1,0),(1,1),(0,4/3)->(0,1.333) but x1+3x2<=4
# gives x2<=4/3 at x1=0; and at x1=1, x1+3x2<=4 -> x2<=1, 3x1+x2<=5 -> x2<=2, so
# (1,1). Final hull region corners:
FINAL_POLY = [(F(0), F(0)), (F(1), F(0)), (F(1), F(1)), (F(0), F(4, 3))]

LP_OPT = (F(11, 8), F(7, 8))
INT_PTS = [(0, 0), (0, 1), (1, 0), (1, 1)]


def poly_attr(corners):
    return " ".join(f"{x:.2f},{y:.2f}" for (x, y) in (px(a, b) for a, b in corners))


def header():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB_W} {VB_H}" '
            f'width="{VB_W}" height="{VB_H}" font-family="Georgia, serif">\n')


def grid_axes():
    s = []
    a = 0
    while a <= 2:
        b = 0
        while b <= 2:
            x, y = px(a, b)
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.3" fill="{GRID}"/>')
            b += 1
        a += 1
    x0, y0 = px(0, 0)
    xend, _ = px(X1_AX, 0)
    _, yend = px(0, X2_AX)
    s.append(f'<line x1="{x0}" y1="{y0}" x2="{xend:.1f}" y2="{y0}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{yend:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{xend:.1f}" y="{y0+20}" font-size="15" font-style="italic" fill="{INK}" text-anchor="end">x_1</text>')
    s.append(f'<text x="{x0-10}" y="{yend:.1f}" font-size="15" font-style="italic" fill="{INK}" text-anchor="end">x_2</text>')
    return "\n".join(s)


def line_seg(n1, n2, rhs, color, label, lx=0.5):
    # clip line n1 x1 + n2 x2 = rhs to the axis window [0,X1_AX]x[0,X2_AX]
    pts = []
    for xv in (F(0), F(X1_AX).limit_denominator()):
        if n2 != 0:
            yv = (rhs - n1 * xv) / n2
            if 0 <= yv <= X2_AX + F(1, 100):
                pts.append((xv, yv))
    for yv in (F(0), F(X2_AX).limit_denominator()):
        if n1 != 0:
            xv = (rhs - n2 * yv) / n1
            if 0 <= xv <= X1_AX + F(1, 100):
                pts.append((xv, yv))
    if len(pts) < 2:
        return ""
    (ax, ay), (bx, by) = pts[0], pts[1]
    p1, p2 = px(ax, ay), px(bx, by)
    mx = p1[0] + (p2[0] - p1[0]) * lx
    my = p1[1] + (p2[1] - p1[1]) * lx
    return (f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" '
            f'stroke="{color}" stroke-width="3" stroke-linecap="round" stroke-dasharray="7 5"/>\n'
            f'<text x="{mx+6:.1f}" y="{my-6:.1f}" font-size="13" fill="{color}">{label}</text>')


def dots():
    s = []
    for (a, b) in INT_PTS:
        x, y = px(a, b)
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{BLUE}"/>')
    return "\n".join(s)


def opt():
    x, y = px(*LP_OPT)
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{ORANGE}" stroke="#fff" stroke-width="1.5"/>'
            f'<text x="{x+9:.1f}" y="{y-7:.1f}" font-size="13" fill="{ORANGE}">x_LP</text>')


def footer():
    return "</svg>\n"


body = "\n".join([
    grid_axes(),
    f'<polygon points="{poly_attr(LP_POLY)}" fill="{POLY_FILL}" stroke="{BLUE}" stroke-width="2.5"/>',
    f'<polygon points="{poly_attr(FINAL_POLY)}" fill="{HULL_FILL}" stroke="{GREEN}" stroke-width="2"/>',
    line_seg(F(1), F(1), F(2), GREEN, "x_1 + x_2 &#8804; 2", lx=0.5),
    line_seg(F(1), F(0), F(1), GREEN, "x_1 &#8804; 1", lx=0.72),
    dots(),
    opt(),
])

path = os.path.join(os.path.dirname(__file__), "..", "images", "ip_two_cut_example.svg")
with open(path, "w") as f:
    f.write(header() + body + "\n" + footer())
print("wrote", os.path.normpath(path))
