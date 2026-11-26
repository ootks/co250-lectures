#!/usr/bin/env python3
"""Lecture 21: the gradient of f(x, y) = x^2 + y^2 at (1, 1) is a subgradient.

Draws the bowl t = x^2 + y^2 together with the plane
    t = h(x, y) = f(1, 1) + (2, 2) . ((x, y) - (1, 1)) = 2x + 2y - 2,
which touches the bowl at (1, 1, 2) and lies below it everywhere else, since
    f(x, y) - h(x, y) = (x - 1)^2 + (y - 1)^2 >= 0.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, GREEN, ORANGE, INK, FAINT = "#268bd2", "#859900", "#cb4b16", "#073642", "#93a1a1"

AZIM = float(sys.argv[2]) if len(sys.argv) > 2 else -38
ELEV = float(sys.argv[3]) if len(sys.argv) > 3 else 12

fig = plt.figure(figsize=(5.2, 4.6))
ax = fig.add_subplot(111, projection="3d", computed_zorder=False)
ax.view_init(elev=ELEV, azim=AZIM)

# bowl in polar coordinates
r = np.linspace(0, 2.0, 40)
th = np.linspace(0, 2 * np.pi, 80)
R, TH = np.meshgrid(r, th)
X, Y = R * np.cos(TH), R * np.sin(TH)
Z = X ** 2 + Y ** 2

# tangent plane on a square patch around (1, 1), clipped to t >= -0.6
u = np.linspace(-0.25, 2.1, 30)
PX, PY = np.meshgrid(u, u)
PZ = 2 * PX + 2 * PY - 2
assert np.all(PX ** 2 + PY ** 2 - PZ >= -1e-12)

ax.plot_surface(PX, PY, PZ, color=GREEN, alpha=0.45, linewidth=0, zorder=1)
ax.plot_surface(X, Y, Z, color=BLUE, alpha=0.42, linewidth=0.25, edgecolor=BLUE,
                rstride=4, cstride=5, zorder=2)
ax.scatter([1], [1], [2], color=ORANGE, s=55, depthshade=False, zorder=5,
           edgecolors="white", linewidths=1.0)
# the gradient direction drawn in the (x, y)-plane underneath
ax.plot([1, 1], [1, 1], [-2.0, 2], color=FAINT, linestyle=(0, (3, 3)), linewidth=1, zorder=0)

ax.text(1.02, 1.02, 2.0, "  (1, 1, 2)", color=ORANGE, fontsize=11, zorder=6, family="serif")
ax.text2D(0.20, 0.70, "$t = x^2 + y^2$", color=BLUE, fontsize=13, transform=ax.transAxes)
ax.text2D(0.97, 0.80, "$t = 2 + 2(x-1) + 2(y-1)$", color=GREEN, fontsize=13, transform=ax.transAxes, ha="right")

ax.set_xlabel("$x$", color=INK, labelpad=-8)
ax.set_ylabel("$y$", color=INK, labelpad=-8)
ax.set_xlim(-2, 2.2); ax.set_ylim(-2, 2.2); ax.set_zlim(-2, 6.4)
ax.set_xticks([-2, -1, 0, 1, 2]); ax.set_yticks([-2, -1, 0, 1, 2]); ax.set_zticks([0, 2, 4, 6])
ax.tick_params(colors=FAINT, labelsize=8, pad=-3)
for a in (ax.xaxis, ax.yaxis, ax.zaxis):
    a.set_pane_color((1, 1, 1, 0))
    a.line.set_color(FAINT)
    a._axinfo["grid"]["color"] = (0.58, 0.63, 0.63, 0.25)
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "images", "gradient_subgradient_3d.png")
fig.savefig(out, dpi=200, transparent=True, bbox_inches="tight", pad_inches=0.05)
print("wrote", os.path.normpath(out))
