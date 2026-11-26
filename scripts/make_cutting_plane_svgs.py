#!/usr/bin/env python3
"""Generate the cutting-plane illustration SVGs used in lecture 20.

Shared example (the lecture's running IP):
    max x1 + x2
    s.t. x1 + 3 x2 <= 9
         3 x1 +  x2 <= 17
         x1, x2 >= 0
LP optimum x* = (21/4, 5/4) = (5.25, 1.25).

All figures share one coordinate frame so the polytope, lattice and optimum
line up across slides.
"""

import os

# ---- solarized palette ----
INK = "#073642"
GRID = "#d8d0bb"
BLUE = "#268bd2"
GREEN = "#859900"
RED = "#dc322f"
ORANGE = "#cb4b16"
FAINT = "#93a1a1"
POLY_FILL = "rgba(38,139,210,0.12)"
CUT_OK = "rgba(133,153,0,0.14)"
CUT_BAD = "rgba(220,50,47,0.16)"

# ---- coordinate frame ----
VB_W, VB_H = 480, 390
OX, OY = 70, 330          # pixel location of data origin (0,0)
UX, UY = 58, 70           # pixels per unit in x1, x2
X1_MAX_AX, X2_MAX_AX = 6.6, 3.8   # axis extents in data units


def px(a, b):
    return (OX + a * UX, OY - b * UY)


# polytope corners (data coords), counterclockwise
POLY = [(0, 0), (17 / 3, 0), (21 / 4, 5 / 4), (0, 3)]
OPT = (21 / 4, 5 / 4)

# the 17 integer feasible points
INT_PTS = []
for b in range(0, 4):
    for a in range(0, 7):
        if a + 3 * b <= 9 and 3 * a + b <= 17 and a >= 0 and b >= 0:
            INT_PTS.append((a, b))


def poly_points_attr(corners):
    return " ".join(f"{x:.2f},{y:.2f}" for (x, y) in (px(a, b) for a, b in corners))


def header():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB_W} {VB_H}" '
            f'width="{VB_W}" height="{VB_H}" font-family="Georgia, serif">\n')


def grid_and_axes():
    s = []
    # lattice dots
    for a in range(0, 8):
        for b in range(0, 5):
            x, y = px(a, b)
            if 0 <= x <= VB_W and 0 <= y <= VB_H:
                s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="{GRID}"/>')
    # axes
    x0, y0 = px(0, 0)
    xend, _ = px(X1_MAX_AX, 0)
    _, yend = px(0, X2_MAX_AX)
    s.append(f'<line x1="{x0}" y1="{y0}" x2="{xend:.1f}" y2="{y0}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{yend:.1f}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{xend:.1f}" y="{y0+20}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">x_1</text>')
    s.append(f'<text x="{x0-12}" y="{yend:.1f}" font-size="16" font-style="italic" fill="{INK}" text-anchor="end">x_2</text>')
    return "\n".join(s)


def polytope():
    return f'<polygon points="{poly_points_attr(POLY)}" fill="{POLY_FILL}" stroke="{BLUE}" stroke-width="2.5"/>'


def int_points(highlight_opt=False):
    s = []
    for (a, b) in INT_PTS:
        x, y = px(a, b)
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{BLUE}"/>')
    return "\n".join(s)


def opt_marker():
    x, y = px(*OPT)
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{ORANGE}" stroke="#fff" stroke-width="1.5"/>'
            f'<text x="{x+10:.1f}" y="{y-8:.1f}" font-size="14" fill="{ORANGE}">x*</text>')


def cut_line(n1, n2, rhs, color, label, removed=False, label_px=None, label_anchor="start", dashed=False):
    """Draw the line n1*x1 + n2*x2 = rhs, clipped to the drawing box, label it,
    and (optionally) shade the removed sliver on the > rhs side of the polytope."""
    s = []
    # find two points of the line within the axis window by intersecting with box edges
    pts = []
    # intersect with x1 in [0, X1_MAX_AX] and x2 in [0, X2_MAX_AX]
    xs = [0.0, X1_MAX_AX]
    for xv in xs:
        if n2 != 0:
            yv = (rhs - n1 * xv) / n2
            if -0.5 <= yv <= X2_MAX_AX + 0.5:
                pts.append((xv, yv))
    ys = [0.0, X2_MAX_AX]
    for yv in ys:
        if n1 != 0:
            xv = (rhs - n2 * yv) / n1
            if -0.5 <= xv <= X1_MAX_AX + 0.5:
                pts.append((xv, yv))
    if len(pts) >= 2:
        # use the two candidate points that are farthest apart
        (ax, ay), (bx, by) = max(((p, q) for p in pts for q in pts),
                                 key=lambda pq: (pq[0][0] - pq[1][0]) ** 2 + (pq[0][1] - pq[1][1]) ** 2)
        p1 = px(ax, ay)
        p2 = px(bx, by)
        style = ('stroke-width="2" stroke-dasharray="7 6"' if dashed
                 else 'stroke-width="3.5" stroke-linecap="round"')
        s.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" '
                 f'stroke="{color}" {style}/>')
        if label_px is None:
            lx = (p1[0] + p2[0]) / 2 + 6
            ly = (p1[1] + p2[1]) / 2 - 8
        else:
            lx, ly = label_px
        anchor = "" if label_anchor == "start" else f' text-anchor="{label_anchor}"'
        s.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="14" fill="{color}"{anchor}>{label}</text>')
    return "\n".join(s)


def footer():
    return "</svg>\n"


def write(name, body):
    path = os.path.join(os.path.dirname(__file__), "..", "images", name)
    with open(path, "w") as f:
        f.write(header() + body + "\n" + footer())
    print("wrote", os.path.normpath(path))


# ---- figure 1: base polytope + lattice + optimum ----
base = "\n".join([grid_and_axes(), polytope(), int_points(), opt_marker()])
write("cp_base.svg", base)

def clip_poly_ge(corners, n1, n2, rhs):
    """Clip a convex polygon to the half-plane n1*x1 + n2*x2 >= rhs."""
    out = []
    m = len(corners)
    for i in range(m):
        cur = corners[i]
        nxt = corners[(i + 1) % m]
        cur_in = (n1 * cur[0] + n2 * cur[1]) >= rhs - 1e-9
        nxt_in = (n1 * nxt[0] + n2 * nxt[1]) >= rhs - 1e-9
        if cur_in:
            out.append(cur)
        if cur_in != nxt_in:
            # intersection
            d = (n1 * (nxt[0] - cur[0]) + n2 * (nxt[1] - cur[1]))
            t = (rhs - (n1 * cur[0] + n2 * cur[1])) / d
            out.append((cur[0] + t * (nxt[0] - cur[0]), cur[1] + t * (nxt[1] - cur[1])))
    return out


def removed_region(n1, n2, rhs):
    """Red shading for the part of the polytope with n1*x1 + n2*x2 > rhs."""
    sliver = clip_poly_ge(POLY, n1, n2, rhs)
    if len(sliver) < 3:
        return ""
    return (f'<polygon points="{poly_points_attr(sliver)}" fill="{CUT_BAD}" '
            f'stroke="{RED}" stroke-width="1.5"/>')


def check_valid(n1, n2, rhs):
    assert all(n1 * a + n2 * b <= rhs for (a, b) in INT_PTS), (n1, n2, rhs)


# ---- figure 2: a valid cut that does NOT remove x*  (x1 - x2 <= 5) ----
# It trims a little off the bottom-right corner (17/3, 0) of the polytope,
# but x* = (21/4, 5/4) has x1 - x2 = 4 <= 5, so the LP optimum is unchanged.
check_valid(1, -1, 5)
assert OPT[0] - OPT[1] <= 5
end_x, end_y = px(X1_MAX_AX, X1_MAX_AX - 5)
nonrem = "\n".join([
    grid_and_axes(), polytope(), removed_region(1, -1, 5), int_points(),
    cut_line(1, -1, 5, GREEN, "x_1 &#8722; x_2 &#8804; 5",
             label_px=(VB_W - 4, end_y - 11), label_anchor="end"),
    opt_marker(),
])
write("cp_cut_nonremoving.svg", nonrem)

# ---- figure 3: a cut that DOES remove x*  (x1 + x2 <= 6) ----
check_valid(1, 1, 6)
removing = "\n".join([
    grid_and_axes(), polytope(), removed_region(1, 1, 6), int_points(),
    cut_line(1, 1, 6, GREEN, "x_1 + x_2 &#8804; 6"),
    opt_marker(),
])
write("cp_cut_removing.svg", removing)

# ---- figure 4: generic single cut on the base ----
generic = "\n".join([
    grid_and_axes(), polytope(), int_points(),
    cut_line(1, 1, 6, GREEN, "f&#8868;x &#8804; v"),
    opt_marker(),
])
write("cp_cut_generic.svg", generic)

# ---- figure 5: a cut that decreases the LP optimal value (first slide) ----
# Objective x1 + x2.  The dashed orange line is the old optimal level set
# x1 + x2 = 13/2 through x*; the cut x1 + x2 <= 6 lowers the LP value to 6.
top = X2_MAX_AX - 0.45
cut_lab = px(6 - top, top)
lvl_lab = px(6.5 - top, top)
decrease = "\n".join([
    grid_and_axes(), polytope(), removed_region(1, 1, 6), int_points(),
    cut_line(1, 1, 6.5, ORANGE, "x_1 + x_2 = 13/2", dashed=True,
             label_px=(lvl_lab[0] + 10, lvl_lab[1])),
    cut_line(1, 1, 6, GREEN, "x_1 + x_2 &#8804; 6",
             label_px=(cut_lab[0] - 10, cut_lab[1]), label_anchor="end"),
    opt_marker(),
])
write("cp_cut_decrease.svg", decrease)
