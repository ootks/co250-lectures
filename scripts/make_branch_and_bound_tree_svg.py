#!/usr/bin/env python3
"""Generate the branch and bound tree for the lecture 20 example

    max x1 + x2  s.t.  2 x1 + 3 x2 <= 12,  4 x1 + x2 <= 10,  x >= 0 integer.

Root LP optimum (9/5, 14/5), value 23/5.  Branch on x1:
    x1 <= 1 : LP optimum (1, 10/3), value 13/3  -> pruned (floor(13/3) = 4)
    x1 >= 2 : LP optimum (2, 2),    value 4     -> integral
The children of the x1 <= 1 node (x2 <= 3, x2 >= 4) are never solved.
"""

import os

INK = "#073642"
BLUE = "#268bd2"
GREEN = "#859900"
RED = "#dc322f"
FAINT = "#93a1a1"
BOX = "rgba(238,232,213,0.75)"

VB_W, VB_H = 640, 400
NW, NH = 196, 60


def node(cx, cy, lines, stroke=BLUE, faded=False, dashed=False, w=NW, h=NH):
    op = ' opacity="0.7"' if faded else ""
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    s = [f'<g{op}>',
         f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" rx="12" fill="{BOX}" '
         f'stroke="{stroke}" stroke-width="2.5"{dash}/>']
    n = len(lines)
    for k, (txt, color) in enumerate(lines):
        y = cy + 5 + (k - (n - 1) / 2) * 21
        s.append(f'<text x="{cx}" y="{y:.1f}" font-size="16" fill="{color}" text-anchor="middle">{txt}</text>')
    s.append('</g>')
    return "\n".join(s)


def edge(a, b, label, side, color=INK, dashed=False, faded=False):
    """a = (x, y of bottom of parent), b = (x, y of top of child)."""
    op = ' opacity="0.7"' if faded else ""
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    anchor, dx = ("end", -14) if side == "left" else ("start", 14)
    return (f'<g{op}><line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{FAINT}" stroke-width="2"{dash}/>'
            f'<text x="{mx+dx:.1f}" y="{my+4:.1f}" font-size="16" font-style="italic" fill="{color}" '
            f'text-anchor="{anchor}">{label}</text></g>')


H3 = 84           # height of a three-line node
GW, GH = 150, 50  # unsolved grandchildren
ROOT = (320, 42)
L = (170, 196)
R = (470, 196)
LL = (85, 362)
LR = (255, 362)

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB_W} {VB_H}" width="{VB_W}" height="{VB_H}" '
    f'font-family="Georgia, serif">',
    edge((ROOT[0], ROOT[1] + NH / 2), (L[0], L[1] - H3 / 2), "x&#8321; &#8804; 1", "left"),
    edge((ROOT[0], ROOT[1] + NH / 2), (R[0], R[1] - H3 / 2), "x&#8321; &#8805; 2", "right"),
    edge((L[0], L[1] + H3 / 2), (LL[0], LL[1] - GH / 2), "x&#8322; &#8804; 3", "left", dashed=True, faded=True),
    edge((L[0], L[1] + H3 / 2), (LR[0], LR[1] - GH / 2), "x&#8322; &#8805; 4", "right", dashed=True, faded=True),
    node(*ROOT, [("x* = (9/5, 14/5)", INK), ("LP value 23/5", INK)]),
    node(*L, [("x* = (1, 10/3)", INK), ("LP value 13/3", INK), ("pruned: &#8970;13/3&#8971; = 4 &#8804; 4", RED)],
         stroke=RED, h=H3),
    node(*R, [("x* = (2, 2)", INK), ("LP value 4", INK), ("integral", GREEN)], stroke=GREEN, h=H3),
    node(*LL, [("not solved", INK)], stroke=FAINT, faded=True, dashed=True, w=GW, h=GH),
    node(*LR, [("not solved", INK)], stroke=FAINT, faded=True, dashed=True, w=GW, h=GH),
    '</svg>',
]
path = os.path.join(os.path.dirname(__file__), "..", "images", "branch_and_bound_tree.svg")
with open(path, "w") as fh:
    fh.write("\n".join(parts) + "\n")
print("wrote", os.path.normpath(path))
