#!/usr/bin/env python3
"""Generate the SVG figures for the gradient descent lecture.

Writes hand-styled SVGs (Georgia, solarized colours, like the other figures
in images/) using only the standard library.

Usage:  python3 scripts/plot_gradient_descent_figures.py [output_dir]
        (output_dir defaults to images/)
"""
import math
import os
import sys

BASE = "#586e75"    # axes and text
BLUE = "#268bd2"    # the function f
RED = "#dc322f"     # tangent lines / chords
GREEN = "#859900"   # quadratic approximation
ORANGE = "#cb4b16"  # marked points
MUTED = "#93a1a1"


def sub(base, s):
    """Italic symbol with a subscript, as SVG text content."""
    return (f'<tspan font-style="italic">{base}</tspan>'
            f'<tspan dy="4" font-size="70%">{s}</tspan><tspan dy="-4"></tspan>')


class Panel:
    """A rectangular plotting region inside an SVG."""

    _count = 0

    def __init__(self, x, y, w, h, xlim, ylim):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.xlim, self.ylim = xlim, ylim
        Panel._count += 1
        self.clip = f"clip{Panel._count}"
        self.out = [f'<clipPath id="{self.clip}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>']

    def X(self, x):
        return self.x + (x - self.xlim[0]) / (self.xlim[1] - self.xlim[0]) * self.w

    def Y(self, y):
        return self.y + self.h - (y - self.ylim[0]) / (self.ylim[1] - self.ylim[0]) * self.h

    def axes(self, x_at=0.0, y_at=0.0, xlabel="x", yaxis=True):
        x0, x1 = self.x, self.x + self.w
        y0, y1 = self.y + self.h, self.y
        ay = self.Y(y_at)
        self.out.append(f'<line x1="{x0}" y1="{ay:.1f}" x2="{x1}" y2="{ay:.1f}" stroke="{BASE}" stroke-width="2"/>')
        self.out.append(f'<polygon points="{x1 + 8},{ay:.1f} {x1},{ay - 5:.1f} {x1},{ay + 5:.1f}" fill="{BASE}"/>')
        self.out.append(f'<text x="{x1 + 6}" y="{ay + 20:.1f}" text-anchor="middle" font-size="17" font-style="italic" fill="{BASE}">{xlabel}</text>')
        if yaxis:
            ax = self.X(x_at)
            self.out.append(f'<line x1="{ax:.1f}" y1="{y0}" x2="{ax:.1f}" y2="{y1}" stroke="{BASE}" stroke-width="2"/>')
            self.out.append(f'<polygon points="{ax:.1f},{y1 - 8} {ax - 5:.1f},{y1} {ax + 5:.1f},{y1}" fill="{BASE}"/>')

    def curve(self, f, color=BLUE, width=3.5, dash=None, lo=None, hi=None, n=400):
        lo = self.xlim[0] if lo is None else lo
        hi = self.xlim[1] if hi is None else hi
        pts = []
        for i in range(n + 1):
            x = lo + (hi - lo) * i / n
            pts.append(f"{self.X(x):.1f},{self.Y(f(x)):.1f}")
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.out.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="{width}" '
                        f'stroke-linejoin="round" stroke-linecap="round"{d} clip-path="url(#{self.clip})"/>')

    def segment(self, xa, ya, xb, yb, color=RED, width=3, dash=None, clip=True):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        c = f' clip-path="url(#{self.clip})"' if clip else ""
        self.out.append(f'<line x1="{self.X(xa):.1f}" y1="{self.Y(ya):.1f}" x2="{self.X(xb):.1f}" y2="{self.Y(yb):.1f}" '
                        f'stroke="{color}" stroke-width="{width}" stroke-linecap="round"{d}{c}/>')

    def arrow(self, xa, ya, xb, yb, color=RED, width=3):
        """Arrow from (xa, ya) to (xb, yb), in data coordinates."""
        X1, Y1, X2, Y2 = self.X(xa), self.Y(ya), self.X(xb), self.Y(yb)
        L = math.hypot(X2 - X1, Y2 - Y1)
        ux, uy = (X2 - X1) / L, (Y2 - Y1) / L
        bx, by = X2 - 12 * ux, Y2 - 12 * uy
        self.out.append(f'<line x1="{X1:.1f}" y1="{Y1:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{color}" stroke-width="{width}"/>')
        self.out.append(f'<polygon points="{X2:.1f},{Y2:.1f} {bx - 6 * uy:.1f},{by + 6 * ux:.1f} {bx + 6 * uy:.1f},{by - 6 * ux:.1f}" fill="{color}"/>')

    def dot(self, x, y, color=ORANGE, r=6, hollow=False):
        fill = "#fdf6e3" if hollow else color
        self.out.append(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r}" fill="{fill}" stroke="{color}" stroke-width="2.5"/>')

    def drop(self, x, y, label=None, y_at=0.0):
        """Dashed vertical line from (x, y) to the x-axis, with a tick label."""
        self.segment(x, y, x, y_at, color=MUTED, width=1.5, dash="5 4", clip=False)
        if label:
            self.text(x, y_at, label, dy=22)

    def text(self, x, y, s, dx=0, dy=0, color=BASE, size=17, anchor="middle", italic=False):
        st = ' font-style="italic"' if italic else ""
        self.out.append(f'<text x="{self.X(x) + dx:.1f}" y="{self.Y(y) + dy:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{color}"{st}>{s}</text>')


def save(name, w, h, panels, extra=""):
    body = "\n  ".join(line for p in panels for line in p.out)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="Georgia, serif">\n'
           f'  {body}\n  {extra}\n</svg>\n')
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(svg)
    print("wrote", name)


def legend(items, y):
    """A horizontal legend; items are (colour, dash, label, x)."""
    out = []
    for color, dash, label, x in items:
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<line x1="{x}" y1="{y}" x2="{x + 30}" y2="{y}" stroke="{color}" stroke-width="3.5"{d}/>')
        out.append(f'<text x="{x + 38}" y="{y + 5}" font-size="16" fill="{BASE}">{label}</text>')
    return "\n  ".join(out)


# ---------------------------------------------------------------- functions
def f(x):
    return 0.3 * x * x + 0.8 * math.sin(x) + 1.3


def df(x):
    return 0.6 * x + 0.8 * math.cos(x)


def wiggly(x):
    return 0.22 * x * x + 0.9 * math.sin(2.3 * x) + 0.5 * math.cos(5.1 * x + 1) + 0.3 * math.sin(9 * x) + 2.0


def tangent(x0):
    return lambda x: f(x0) + df(x0) * (x - x0)


def critical_point():
    x = -1.0
    for _ in range(60):  # Newton's method on f'
        x -= df(x) / (0.6 - 0.8 * math.sin(x))
    return x


W, H = 560, 300
XLIM, YLIM = (-4.2, 4.2), (-1.2, 6.6)


def base_panel(func=f):
    p = Panel(30, 16, 500, 260, XLIM, YLIM)
    p.axes(yaxis=False)
    p.curve(func)
    return p


def main():
    # 1. A function of one variable.
    p = base_panel()
    p.text(-3.55, f(-3.55), "f", dx=22, dy=4, color=BLUE, size=20, italic=True)
    save("gd_1d_function.svg", W, H, [p])

    # 2. A complicated function of one variable.
    p = base_panel(wiggly)
    p.text(-3.7, wiggly(-3.7), "f", dx=24, dy=0, color=BLUE, size=20, italic=True)
    save("gd_1d_complicated.svg", W, H, [p])

    # 3. Function with a tangent line (no labels).
    x0 = 2.0
    p = base_panel()
    p.curve(tangent(x0), color=RED, width=3)
    p.dot(x0, f(x0))
    p.text(-3.55, f(-3.55), "f", dx=22, dy=4, color=BLUE, size=20, italic=True)
    save("gd_tangent.svg", W, H, [p])

    # 4. Tangent line at x0, labelled.
    p = base_panel()
    p.curve(tangent(x0), color=RED, width=3)
    p.drop(x0, f(x0), sub("x", "0"))
    p.dot(x0, f(x0))
    p.text(-3.55, f(-3.55), "f", dx=22, dy=4, color=BLUE, size=20, italic=True)
    p.text(0.4, 4.7, "tangent line at " + sub("x", "0"), color=RED)
    save("gd_tangent_x0.svg", W, H, [p])

    # 5. Positive derivative: the tangent line decreases as x -> -infinity.
    p = base_panel()
    t = tangent(x0)
    p.curve(t, color=RED, width=3)
    p.drop(x0, f(x0), sub("x", "0"))
    p.dot(x0, f(x0))
    p.arrow(1.2, t(1.2) - 0.8, -0.5, t(-0.5) - 0.8, color=ORANGE)
    p.text(-2.75, 0.35, "decreases forever", color=ORANGE)
    p.text(-3.55, f(-3.55), "f", dx=22, dy=4, color=BLUE, size=20, italic=True)
    save("gd_tangent_positive.svg", W, H, [p])

    # 6. Negative derivative: the tangent line decreases as x -> +infinity.
    x0n = -2.2
    p = base_panel()
    t = tangent(x0n)
    p.curve(t, color=RED, width=3)
    p.drop(x0n, f(x0n), sub("x", "0"))
    p.dot(x0n, f(x0n))
    p.arrow(-1.95, t(-1.95) - 0.9, -1.1, t(-1.1) - 0.9, color=ORANGE)
    p.text(-0.7, 0.3, "decreases forever", color=ORANGE, anchor="start")
    p.text(3.45, f(3.45), "f", dx=-22, dy=4, color=BLUE, size=20, italic=True)
    save("gd_tangent_negative.svg", W, H, [p])

    # 7. Critical point: horizontal tangent line.
    xc = critical_point()
    p = base_panel()
    p.curve(tangent(xc), color=RED, width=3)
    p.drop(xc, f(xc), sub("x", "0"))
    p.dot(xc, f(xc))
    p.text(-3.55, f(-3.55), "f", dx=22, dy=4, color=BLUE, size=20, italic=True)
    p.text(2.2, f(xc), "derivative is 0", dy=-10, color=RED)
    save("gd_tangent_critical.svg", W, H, [p])

    # 8. The tangent line is a poor approximation far from x0.
    p = base_panel()
    t = tangent(x0)
    pts = []
    n = 120
    for i in range(n + 1):
        x = -4.2 + (x0 - 0.0 + 4.2) * i / n
        pts.append((x, f(x)))
    poly = " ".join(f"{p.X(x):.1f},{p.Y(y):.1f}" for x, y in pts)
    poly += f" {p.X(x0):.1f},{p.Y(t(x0)):.1f} {p.X(-4.2):.1f},{p.Y(t(-4.2)):.1f}"
    p.out.insert(1, f'<polygon points="{poly}" fill="{RED}" fill-opacity="0.13" clip-path="url(#{p.clip})"/>')
    p.curve(t, color=RED, width=3)
    p.drop(x0, f(x0), sub("x", "0"))
    p.dot(x0, f(x0))
    p.text(-2.8, 1.5, "large error", color=RED)
    p.text(-2.8, 1.5, "far from " + sub("x", "0"), dy=20, color=RED)
    p.text(-3.55, f(-3.55), "f", dx=22, dy=4, color=BLUE, size=20, italic=True)
    save("gd_tangent_error.svg", W, H, [p])

    # 9. Tangent line and quadratic approximation.
    h = 0.7
    q = lambda x: f(x0) + df(x0) * (x - x0) + (x - x0) ** 2 / (2 * h)
    p = base_panel()
    p.curve(tangent(x0), color=RED, width=3, dash="7 5")
    p.curve(q, color=GREEN, width=3.5)
    p.drop(x0, f(x0), sub("x", "0"))
    p.dot(x0, f(x0))
    extra = legend([(BLUE, None, '<tspan font-style="italic">f</tspan>', 60),
                    (RED, "7 5", "tangent line", 140),
                    (GREEN, None, "quadratic approximation", 300)], 300)
    save("gd_quadratic_approx.svg", W, 316, [p], extra)

    # 10. |x| and its derivative.
    def two_panels(func, dfunc_draw, name, eps=None):
        a = Panel(30, 40, 300, 200, (-3, 3), (-0.6, 3.2))
        a.axes()
        a.curve(func)
        a.text(0, 3.2, '<tspan font-style="italic">f</tspan>(<tspan font-style="italic">x</tspan>)', dx=-150 + 150, dy=-22, color=BLUE, size=19)
        b = Panel(410, 40, 300, 200, (-3, 3), (-1.9, 1.9))
        b.axes()
        dfunc_draw(b)
        b.text(0, 1.9, "derivative of " + '<tspan font-style="italic">f</tspan>', dy=-22, color=RED, size=19)
        for v, lab in ((1, "1"), (-1, "−1")):
            b.segment(-0.08, v, 0.08, v, color=BASE, width=2, clip=False)
        b.text(0, 1, "1", dx=-16, dy=5)
        b.text(0, -1, "−1", dx=20, dy=5)
        if eps:
            for pnl in (a, b):
                for v, lab in ((eps, "ε"), (-eps, "−ε")):
                    y_at = 0
                    pnl.segment(v, -0.07 * (pnl.ylim[1] - pnl.ylim[0]) / 3.8, v, 0.07 * (pnl.ylim[1] - pnl.ylim[0]) / 3.8, color=BASE, width=2, clip=False)
            a.text(eps, 0, "ε", dx=4, dy=22, italic=True)
            a.text(-eps, 0, "−ε", dx=-6, dy=22, italic=True)
            b.text(eps, 0, "ε", dx=6, dy=22, italic=True)
            b.text(-eps, 0, "−ε", dx=-8, dy=-10, italic=True)
        save(name, 750, 270, [a, b])

    def abs_deriv(b):
        b.segment(-3, -1, 0, -1, color=RED, width=3.5)
        b.segment(0, 1, 3, 1, color=RED, width=3.5)
        b.dot(0, -1, color=RED, r=5, hollow=True)
        b.dot(0, 1, color=RED, r=5, hollow=True)

    two_panels(abs, abs_deriv, "gd_abs.svg")

    # 11. Smoothed |x| and its (continuous, piecewise linear) derivative.
    eps = 0.6
    smooth = lambda x: x * x / (2 * eps) if abs(x) <= eps else abs(x) - eps / 2

    def smooth_deriv(b):
        b.curve(lambda x: max(-1.0, min(1.0, x / eps)), color=RED)

    two_panels(smooth, smooth_deriv, "gd_abs_smoothed.svg", eps=eps)

    # 12. Negative second derivative: the midpoint of the curve lies above the chord.
    g = lambda x: 0.8 + 2.4 * math.sin(0.7 * x + 0.3)
    xa, xb = 0.6, 2.6
    xm = (xa + xb) / 2
    p = Panel(30, 16, 500, 215, (0, 3.3), (1.3, 3.75))
    p.axes(y_at=1.3, yaxis=False)
    p.curve(g, lo=0.15, hi=3.15)
    p.segment(xa, g(xa), xb, g(xb), color=RED, width=3, clip=False)
    p.drop(xa, g(xa), sub("x", "0"), y_at=1.3)
    p.drop(xb, g(xb), '<tspan font-style="italic">y</tspan>', y_at=1.3)
    p.segment(xm, g(xm), xm, 1.3, color=MUTED, width=1.5, dash="5 4", clip=False)
    chord_mid = (g(xa) + g(xb)) / 2
    p.dot(xa, g(xa))
    p.dot(xb, g(xb))
    p.dot(xm, g(xm), color=BLUE)
    p.dot(xm, chord_mid, color=RED)
    fi = '<tspan font-style="italic">f</tspan>'
    p.text(xm, g(xm), f'{fi}(½{sub("x", "0")} + ½<tspan font-style="italic">y</tspan>)', dx=14, dy=-12, color=BLUE, anchor="start")
    p.text(xm, chord_mid, f'½{fi}({sub("x", "0")}) + ½{fi}(<tspan font-style="italic">y</tspan>)', dx=14, dy=22, color=RED, anchor="start")
    p.text(0.15, g(0.15), "f", dx=-4, dy=-10, color=BLUE, size=20, italic=True)
    save("gd_concave_midpoint.svg", 560, 262, [p])


if __name__ == "__main__":
    OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images")
    main()
