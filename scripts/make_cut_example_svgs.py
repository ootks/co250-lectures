#!/usr/bin/env python3
"""Generate the SVGs for the explicit numerical cutting-plane example in lecture 20.

    max x1 + x2
    s.t. 2 x1 + 3 x2 <= 12
         4 x1 +   x2 <= 10
         x1, x2 >= 0, integer
LP optimum x* = (9/5, 14/5), value 23/5.

    x1 + x2 <= 4 : valid, removes x*          (a cutting plane for x*)
    x1      <= 2 : valid, does not remove x*  (not a cutting plane for x*)
"""

import os

INK = "#073642"
GRID = "#d8d0bb"
BLUE = "#268bd2"
GREEN = "#859900"
RED = "#dc322f"
ORANGE = "#cb4b16"
VIOLET = "#6c71c4"
FAINT = "#93a1a1"
POLY_FILL = "rgba(38,139,210,0.12)"
RED_FILL = "rgba(220,50,47,0.18)"
VIOLET_FILL = "rgba(108,113,196,0.20)"

VB_W, VB_H = 480, 390
OX, OY = 70, 340
UX, UY = 110, 65
X1_MAX_AX, X2_MAX_AX = 3.55, 4.45

POLY = [(0, 0), (5 / 2, 0), (9 / 5, 14 / 5), (0, 4)]
OPT = (9 / 5, 14 / 5)
INT_PTS = [(a, b) for a in range(4) for b in range(5)
           if 2 * a + 3 * b <= 12 and 4 * a + b <= 10]

# both inequalities hold at every integer feasible point
assert all(a + b <= 4 for a, b in INT_PTS)
assert all(a <= 2 for a, b in INT_PTS)
assert OPT[0] + OPT[1] > 4 and OPT[0] <= 2


def px(a, b):
    return (OX + a * UX, OY - b * UY)


def pts_attr(corners):
    return " ".join(f"{x:.2f},{y:.2f}" for (x, y) in (px(a, b) for a, b in corners))


def frame():
    s = []
    for a in range(0, 4):
        for b in range(0, 5):
            x, y = px(a, b)
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="{GRID}"/>')
    x0, y0 = px(0, 0)
    xend, _ = px(X1_MAX_AX, 0)
    _, yend = px(0, X2_MAX_AX)
    s.append(f'<line x1="{x0}" y1="{y0}" x2="{xend:.1f}" y2="{y0}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{yend:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{xend:.1f}" y="{y0+20}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">x_1</text>')
    s.append(f'<text x="{x0-12}" y="{yend:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">x_2</text>')
    for a in range(1, 4):
        x, y = px(a, 0)
        s.append(f'<text x="{x:.1f}" y="{y+20}" font-size="13" fill="{FAINT}" text-anchor="middle">{a}</text>')
    for b in range(1, 5):
        x, y = px(0, b)
        s.append(f'<text x="{x-12:.1f}" y="{y+4.5:.1f}" font-size="13" fill="{FAINT}" text-anchor="end">{b}</text>')
    return "\n".join(s)


def polytope():
    return f'<polygon points="{pts_attr(POLY)}" fill="{POLY_FILL}" stroke="{BLUE}" stroke-width="2.5"/>'


def region(corners, fill, stroke):
    return f'<polygon points="{pts_attr(corners)}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'


def int_points():
    return "\n".join(f'<circle cx="{px(a, b)[0]:.1f}" cy="{px(a, b)[1]:.1f}" r="5.5" fill="{BLUE}"/>'
                     for a, b in INT_PTS)


def opt_marker():
    x, y = px(*OPT)
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{ORANGE}" stroke="#fff" stroke-width="1.5"/>'
            f'<text x="{x-4:.1f}" y="{y-14:.1f}" font-size="14" fill="{ORANGE}" text-anchor="end">x*</text>')


def segment(p, q, color, label, label_at, anchor="start"):
    (x1, y1), (x2, y2) = px(*p), px(*q)
    lx, ly = px(*label_at)
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
            f'stroke-width="3.5" stroke-linecap="round"/>\n'
            f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="14" fill="{color}" text-anchor="{anchor}">{label}</text>')


def write(name, parts):
    path = os.path.join(os.path.dirname(__file__), "..", "images", name)
    with open(path, "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB_W} {VB_H}" '
                f'width="{VB_W}" height="{VB_H}" font-family="Georgia, serif">\n'
                + "\n".join(parts) + "\n</svg>\n")
    print("wrote", os.path.normpath(path))


# LP relaxation and its optimum
write("cp_example_base.svg", [frame(), polytope(), int_points(), opt_marker()])

# x1 + x2 <= 4 removes the sliver (0,4), x*, (2,2)
cut_sum = [
    region([(0, 4), OPT, (2, 2)], RED_FILL, RED),
]
line_sum = segment((0, 4), (3.2, 0.8), GREEN, "x_1 + x_2 &#8804; 4", (2.42, 1.72))
write("cp_example_cut.svg", [frame(), polytope()] + cut_sum + [int_points(), line_sum, opt_marker()])

# x1 <= 2 removes the triangle (2,0), (5/2,0), (2,2) but not x*
cut_x1 = [
    region([(2, 0), (5 / 2, 0), (2, 2)], VIOLET_FILL, VIOLET),
]
line_x1 = segment((2, -0.15), (2, 4.35), VIOLET, "x_1 &#8804; 2", (2.08, 4.2))
write("cp_example_both.svg", [frame(), polytope()] + cut_sum + cut_x1
      + [int_points(), line_sum, line_x1, opt_marker()])

# ---- branch and bound: split on x1 <= 1 or x1 >= 2 ----
LEFT = [(0, 0), (1, 0), (1, 10 / 3), (0, 4)]
RIGHT = [(2, 0), (5 / 2, 0), (2, 2)]
STRIP = [(1, 0), (2, 0), (2, 2), OPT, (1, 10 / 3)]
GREEN_FILL = "rgba(133,153,0,0.22)"
BLUE_FILL = "rgba(38,139,210,0.22)"


def sub_opt(a, b, label, dx, dy, anchor):
    x, y = px(a, b)
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" fill="none" stroke="{VIOLET}" stroke-width="2.5"/>'
            f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" font-size="14" fill="{VIOLET}" text-anchor="{anchor}">{label}</text>')


outline = f'<polygon points="{pts_attr(POLY)}" fill="none" stroke="{BLUE}" stroke-width="2.5"/>'
write("cp_example_branch.svg", [
    frame(),
    region(STRIP, RED_FILL, "none"),
    region(LEFT, BLUE_FILL, "none"),
    region(RIGHT, GREEN_FILL, "none"),
    outline,
    int_points(),
    segment((1, -0.15), (1, 4.35), BLUE, "x_1 &#8804; 1", (0.92, 4.2), anchor="end"),
    segment((2, -0.15), (2, 4.35), GREEN, "x_1 &#8805; 2", (2.08, 4.2)),
    sub_opt(1, 10 / 3, "(1, 10/3)", 12, -14, "start"),
    sub_opt(2, 2, "(2, 2)", 14, -6, "start"),
    opt_marker(),
])
