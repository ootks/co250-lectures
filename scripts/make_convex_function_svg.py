#!/usr/bin/env python3
"""Generate the chord-above-the-graph picture for the definition of a convex
function (lecture 20)."""

import os

INK = "#073642"
BLUE = "#268bd2"
GREEN = "#859900"
ORANGE = "#cb4b16"
FAINT = "#93a1a1"

VB_W, VB_H = 480, 340
OX, OY, UX, UY = 50, 300, 85, 110


def f(t):
    return 0.35 * (t - 2.2) ** 2 + 0.6


def px(t, v):
    return (OX + t * UX, OY - v * UY)


X, Y, LAM = 0.8, 4.0, 0.45
Z = LAM * X + (1 - LAM) * Y
CHORD_Z = LAM * f(X) + (1 - LAM) * f(Y)
assert f(Z) <= CHORD_Z

s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB_W} {VB_H}" '
     f'width="{VB_W}" height="{VB_H}" font-family="Georgia, serif">']

# axis
x0, y0 = px(0, 0)
s.append(f'<line x1="{x0}" y1="{y0}" x2="{px(4.9, 0)[0]:.1f}" y2="{y0}" stroke="{FAINT}" stroke-width="1.5"/>')

# dashed guides
for t, top in ((X, f(X)), (Y, f(Y)), (Z, CHORD_Z)):
    a, b = px(t, 0), px(t, top)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
             f'stroke="{FAINT}" stroke-width="1.2" stroke-dasharray="4 5"/>')

# graph of f
N = 120
pts = " ".join(f"{px(0.15 + i * (4.45 - 0.15) / N, f(0.15 + i * (4.45 - 0.15) / N))[0]:.1f},"
               f"{px(0.15 + i * (4.45 - 0.15) / N, f(0.15 + i * (4.45 - 0.15) / N))[1]:.1f}" for i in range(N + 1))
s.append(f'<polyline points="{pts}" fill="none" stroke="{BLUE}" stroke-width="3"/>')
gx, gy = px(4.45, f(4.45))
s.append(f'<text x="{gx-8:.1f}" y="{gy-10:.1f}" font-size="16" font-style="italic" fill="{BLUE}" text-anchor="end">f</text>')

# chord
a, b = px(X, f(X)), px(Y, f(Y))
s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GREEN}" stroke-width="3" stroke-linecap="round"/>')
for p in (a, b):
    s.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="5" fill="{BLUE}"/>')

# the two compared values
c = px(Z, CHORD_Z)
g = px(Z, f(Z))
s.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="6" fill="{GREEN}" stroke="#fff" stroke-width="1.5"/>')
s.append(f'<text x="{c[0]:.1f}" y="{c[1]-16:.1f}" font-size="15" fill="{GREEN}" text-anchor="middle">&#955;f(x) + (1 &#8722; &#955;)f(y)</text>')
s.append(f'<circle cx="{g[0]:.1f}" cy="{g[1]:.1f}" r="6" fill="{ORANGE}" stroke="#fff" stroke-width="1.5"/>')
s.append(f'<text x="{g[0]+12:.1f}" y="{g[1]+22:.1f}" font-size="15" fill="{ORANGE}" text-anchor="start">f(&#955;x + (1 &#8722; &#955;)y)</text>')

# axis labels
for t, lab in ((X, "x"), (Y, "y"), (Z, "&#955;x + (1 &#8722; &#955;)y")):
    p = px(t, 0)
    s.append(f'<line x1="{p[0]:.1f}" y1="{p[1]-4}" x2="{p[0]:.1f}" y2="{p[1]+4}" stroke="{FAINT}" stroke-width="1.5"/>')
    s.append(f'<text x="{p[0]:.1f}" y="{p[1]+22}" font-size="15" font-style="italic" fill="{INK}" text-anchor="middle">{lab}</text>')

s.append("</svg>")
path = os.path.join(os.path.dirname(__file__), "..", "images", "convex_function_chord.svg")
with open(path, "w") as fh:
    fh.write("\n".join(s) + "\n")
print("wrote", os.path.normpath(path))
