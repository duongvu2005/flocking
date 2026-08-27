"""Named obstacle layouts."""

from __future__ import annotations

from collections.abc import Callable

from .walls import CircleWall, PolygonWall, RectangleWall, StraightWall, Wall

WORLD = (1280, 720)


def plain() -> list[Wall]:
    """Open water, nothing to steer around."""
    return []


def corridor() -> list[Wall]:
    """A funnel narrowing to a throat, so the flock compresses and jets through."""
    return [
        StraightWall(0, 90, 470, 290),
        StraightWall(470, 290, 810, 290),
        StraightWall(810, 290, 1280, 90),
        StraightWall(0, 630, 470, 430),
        StraightWall(470, 430, 810, 430),
        StraightWall(810, 430, 1280, 630),
    ]


def pillars() -> list[Wall]:
    """A staggered lattice of discs. The flock threads through and forms lanes."""
    radius, spacing, rows = 26, 170, 4
    top = (WORLD[1] - (rows - 1) * spacing) / 2
    walls = []
    for row in range(rows):
        y = top + row * spacing
        offset = spacing / 2 if row % 2 else 0
        for col in range(9):
            x = -60 + offset + col * spacing
            if 0 <= x <= WORLD[0]:
                walls.append(CircleWall(x, y, radius))
    return walls


def full_scale() -> list[Wall]:
    """One of every obstacle type, spread across open water."""
    return [
        PolygonWall.regular(285, 250, 72, sides=6, angle=90),
        RectangleWall.centered(975, 470, 230, 85, angle=-20),
        CircleWall(620, 180, 34),
        CircleWall(505, 470, 30),
        CircleWall(810, 300, 28),
        StraightWall(90, 560, 430, 655),
        StraightWall(880, 95, 1190, 185),
        CircleWall(150, 380, 32, velocity=(0.45, 0)),
    ]


SCENES: dict[str, Callable[[], list[Wall]]] = {
    "plain": plain,
    "corridor": corridor,
    "pillars": pillars,
    "full_scale": full_scale,
}


def build(name: str) -> list[Wall]:
    """Build the named scene, or raise with the list of valid names."""
    if name not in SCENES:
        raise ValueError(f"unknown scene {name!r}; expected one of {', '.join(SCENES)}")
    return SCENES[name]()
