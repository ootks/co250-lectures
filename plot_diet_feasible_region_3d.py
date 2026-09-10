#!/usr/bin/env python3
"""Plot the bounded feasible region for the three-food diet problem.

The plotted polytope is

    A x >= b,  x >= 0,  x_1 + x_2 + x_3 <= 700,

where x_1, x_2, and x_3 are servings of eggs, bananas, and chicken.

The script enumerates vertices using NumPy, recovers each polygonal facet from
the active inequalities, and saves both PNG and SVG versions of the figure.
"""

from itertools import combinations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


# Rows correspond to calories, protein, and carbohydrates.
A = np.array(
    [
        [72.0, 105.0, 128.0],
        [6.3, 1.3, 26.0],
        [0.4, 27.0, 0.0],
    ]
)
b = np.array([2000.0, 50.0, 275.0])
SUM_BOUND = 120.0


def diet_constraints(sum_bound=SUM_BOUND):
    """Return every inequality in the form normal @ x >= rhs."""
    return [
        ("Calories", A[0], b[0]),
        ("Protein", A[1], b[1]),
        ("Carbohydrates", A[2], b[2]),
        ("x1 = 0", np.array([1.0, 0.0, 0.0]), 0.0),
        ("x2 = 0", np.array([0.0, 1.0, 0.0]), 0.0),
        ("x3 = 0", np.array([0.0, 0.0, 1.0]), 0.0),
        ("Sum cap", -np.ones(3), -sum_bound),
    ]


def enumerate_vertices(constraints, tolerance=1e-8):
    """Enumerate feasible intersections of triples of active constraints."""
    vertices = []
    for active in combinations(range(len(constraints)), 3):
        matrix = np.vstack([constraints[i][1] for i in active])
        rhs = np.array([constraints[i][2] for i in active])
        if abs(np.linalg.det(matrix)) <= tolerance:
            continue

        point = np.linalg.solve(matrix, rhs)
        feasible = all(
            normal @ point >= value - 1e-7
            for _, normal, value in constraints
        )
        if feasible and not any(
            np.linalg.norm(point - old_point) <= 1e-6
            for old_point in vertices
        ):
            point[np.abs(point) < 1e-10] = 0.0
            vertices.append(point)

    vertices = np.asarray(vertices)
    order = np.lexsort((vertices[:, 2], vertices[:, 1], vertices[:, 0]))
    return vertices[order]


def order_points_on_facet(points, normal):
    """Order coplanar points cyclically around their centroid."""
    center = points.mean(axis=0)
    normal = normal / np.linalg.norm(normal)

    # Choose a stable vector not parallel to the facet normal.
    trial = np.array([1.0, 0.0, 0.0])
    if abs(trial @ normal) > 0.9:
        trial = np.array([0.0, 1.0, 0.0])
    axis_1 = trial - (trial @ normal) * normal
    axis_1 /= np.linalg.norm(axis_1)
    axis_2 = np.cross(normal, axis_1)

    centered = points - center
    angles = np.arctan2(centered @ axis_2, centered @ axis_1)
    return points[np.argsort(angles)]


def recover_facets(vertices, constraints):
    """Return the polygonal facet supported by each active inequality."""
    facets = []
    for name, normal, rhs in constraints:
        scale = max(1.0, abs(rhs))
        ids = [
            i
            for i, point in enumerate(vertices)
            if abs(normal @ point - rhs) <= 2e-7 * scale
        ]
        if len(ids) < 3:
            continue

        points = vertices[ids]
        if np.linalg.matrix_rank(points - points.mean(axis=0)) < 2:
            continue
        facets.append((name, order_points_on_facet(points, normal)))
    return facets


def add_plot_style(ax, limit, title):
    background = "#fdf6e3"
    grid = "#d9d2bd"
    text = "#586e75"

    ax.set_facecolor(background)
    ax.set_title(title, color="#073642", fontsize=15, fontweight="bold", pad=15)
    ax.set_xlim(0, limit)
    ax.set_ylim(0, limit)
    ax.set_zlim(0, limit)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel("Egg servings  $x_1$", color=text, labelpad=10)
    ax.set_ylabel("Banana servings  $x_2$", color=text, labelpad=10)
    ax.set_zlabel("Chicken portions  $x_3$", color=text, labelpad=10)
    ax.tick_params(colors=text, labelsize=8)
    ax.view_init(elev=24, azim=-56)

    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor(background)
        axis.pane.set_edgecolor(grid)
        axis._axinfo["grid"]["color"] = grid
        axis._axinfo["grid"]["linewidth"] = 0.7


FACET_STYLE = {
    "Calories": ("#6c71c4", 0.42),
    "Protein": ("#b58900", 0.42),
    "Carbohydrates": ("#268bd2", 0.42),
    "x1 = 0": ("#93a1a1", 0.13),
    "x2 = 0": ("#93a1a1", 0.13),
    "x3 = 0": ("#93a1a1", 0.13),
    "Sum cap": ("#859900", 0.25),
    "x1 = zoom": ("#93a1a1", 0.08),
    "x2 = zoom": ("#93a1a1", 0.08),
    "x3 = zoom": ("#93a1a1", 0.08),
}


def draw_polytope(ax, vertices, constraints, original_vertices, limit, title):
    """Draw facets, edges, and distinguished original extreme points."""
    add_plot_style(ax, limit, title)
    facets = recover_facets(vertices, constraints)

    # Draw artificial bounding facets first and nutrient facets last.
    priority = {
        "Sum cap": 0,
        "x1 = zoom": 0,
        "x2 = zoom": 0,
        "x3 = zoom": 0,
        "x1 = 0": 1,
        "x2 = 0": 1,
        "x3 = 0": 1,
        "Calories": 2,
        "Protein": 2,
        "Carbohydrates": 2,
    }
    facets.sort(key=lambda item: priority[item[0]])

    for name, polygon in facets:
        color, alpha = FACET_STYLE[name]
        collection = Poly3DCollection(
            [polygon],
            facecolor=color,
            edgecolor=color,
            linewidth=1.6,
            alpha=alpha,
        )
        ax.add_collection3d(collection)

    ax.scatter(
        vertices[:, 0],
        vertices[:, 1],
        vertices[:, 2],
        s=22,
        color="#2aa198",
        edgecolor="#fdf6e3",
        linewidth=0.7,
        depthshade=False,
        zorder=5,
    )

    visible_original = np.array(
        [
            point
            for point in original_vertices
            if np.all(point <= limit + 1e-7)
        ]
    )
    if len(visible_original):
        ax.scatter(
            visible_original[:, 0],
            visible_original[:, 1],
            visible_original[:, 2],
            s=55,
            color="#cb4b16",
            edgecolor="#fdf6e3",
            linewidth=1.2,
            depthshade=False,
            zorder=7,
        )


def main():
    original_constraints = diet_constraints()[:-1]
    original_vertices = enumerate_vertices(original_constraints)

    bounded_constraints = diet_constraints()
    bounded_vertices = enumerate_vertices(bounded_constraints)

    # A coordinate-wise 50-serving window reveals the five vertices clustered
    # near the origin. The sixth original vertex remains visible in the full plot.
    zoom_limit = 40
    zoom_constraints = bounded_constraints + [
        ("x1 = zoom", np.array([-1.0, 0.0, 0.0]), -zoom_limit),
        ("x2 = zoom", np.array([0.0, -1.0, 0.0]), -zoom_limit),
        ("x3 = zoom", np.array([0.0, 0.0, -1.0]), -zoom_limit),
    ]
    zoom_vertices = enumerate_vertices(zoom_constraints)

    fig = plt.figure(figsize=(14, 7.2), facecolor="#fdf6e3")
    zoom_ax = fig.add_subplot(projection="3d")

    draw_polytope(
        zoom_ax,
        zoom_vertices,
        zoom_constraints,
        original_vertices,
        zoom_limit,
        "Detail near the origin",
    )

    # Label the distant original vertex in the full view.
    distant = original_vertices[np.argmax(original_vertices[:, 0])]

    fig.suptitle(
        r"Diet feasible region:  $Ax\geq b,\ x\geq0$",
        x=0.5,
        y=0.965,
        color="#073642",
        fontsize=19,
        fontweight="bold",
    )
    fig.text(
        0.5,
        0.055,
        "The full plot uses one common serving scale. "
        "The detail view intersects the same polytope with $0\\leq x_i\\leq50$.",
        ha="center",
        color="#586e75",
        fontsize=10,
    )

    legend_items = [
        Patch(facecolor="#6c71c4", alpha=0.42, label="Calories = 2000"),
        Patch(facecolor="#b58900", alpha=0.42, label="Protein = 50 g"),
        Patch(facecolor="#268bd2", alpha=0.42, label="Carbohydrates = 275 g"),
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="",
            markerfacecolor="#cb4b16",
            markeredgecolor="#fdf6e3",
            markersize=8,
            label="Original extreme point",
        ),
    ]
    fig.legend(
        handles=legend_items,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.005),
        ncol=5,
        frameon=False,
        fontsize=9,
        labelcolor="#586e75",
    )

    fig.savefig(
        "diet-feasible-region-3d.svg",
        facecolor=fig.get_facecolor(),
        bbox_inches="tight",
    )

    np.set_printoptions(precision=6, suppress=True)
    print("Original extreme points:")
    print(original_vertices)
    print(f"\nMaximum original coordinate sum: {original_vertices.sum(axis=1).max():.6f}")
    print(f"Sum bound: {SUM_BOUND:.1f}")
    print(f"Bounded polytope vertices: {len(bounded_vertices)}")
    print(bounded_vertices)


if __name__ == "__main__":
    main()
