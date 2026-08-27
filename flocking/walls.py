"""Obstacle primitives.

A wall owns its pose and motion, delegates intersection to `geometry`, and
draws itself. Colours and widths come from RenderConfig.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections.abc import Sequence

import pygame
from pygame.math import Vector2

from .config import RenderConfig
from .geometry import HitRecord, ray_circle, ray_segment


class Wall(ABC):
    """An obstacle that boids steer around."""

    def update(self, dt: float, world_size: tuple[int, int]) -> None:
        """Advance this wall's motion. Static walls do nothing."""

    def contains(self, point: Vector2) -> bool:
        """Whether a point is inside this wall. Open shapes contain nothing."""
        return False

    @abstractmethod
    def hit(self, origin: Vector2, direction: Vector2, record: HitRecord) -> HitRecord:
        """Return `record`, or a closer one if this wall is hit first."""

    @abstractmethod
    def draw(self, surface: pygame.Surface, cfg: RenderConfig, scale: int) -> None:
        """Draw onto a surface `scale` times larger than the world."""


def _edge_width(cfg: RenderConfig, scale: int) -> int:
    return max(1, int(cfg.wall_width * scale))


class StraightWall(Wall):
    """A line segment from (x1, y1) to (x2, y2)."""

    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        self.p1 = Vector2(x1, y1)
        self.p2 = Vector2(x2, y2)

    def hit(self, origin, direction, record):
        return ray_segment(origin, direction, self.p1, self.p2, record)

    def draw(self, surface, cfg, scale):
        pygame.draw.line(
            surface, cfg.wall_edge, self.p1 * scale, self.p2 * scale, _edge_width(cfg, scale)
        )


class CircleWall(Wall):
    """A disc, optionally drifting at a constant velocity."""

    def __init__(self, x: float, y: float, radius: float, velocity: Sequence[float] | None = None):
        self.center = Vector2(x, y)
        self.radius = radius
        self.velocity = Vector2(velocity) if velocity is not None else Vector2(0, 0)

    def update(self, dt, world_size):
        if self.velocity.magnitude_squared() == 0:
            return
        self.center += self.velocity * dt
        width, height = world_size
        self.center.x %= width
        self.center.y %= height

    def contains(self, point):
        return self.center.distance_to(point) < self.radius

    def hit(self, origin, direction, record):
        return ray_circle(origin, direction, self.center, self.radius, record)

    def draw(self, surface, cfg, scale):
        center, radius = self.center * scale, self.radius * scale
        pygame.draw.circle(surface, cfg.wall_fill, center, radius)
        pygame.draw.circle(surface, cfg.wall_edge, center, radius, _edge_width(cfg, scale))


class PolygonWall(Wall):
    """A closed outline through the given points."""

    def __init__(self, points: Sequence[Sequence[float]]):
        self.points = [Vector2(p) for p in points]
        if len(self.points) < 3:
            raise ValueError("a polygon wall needs at least three points")

    @classmethod
    def regular(cls, cx: float, cy: float, radius: float, sides: int, angle: float = 0.0):
        """A regular polygon centred at (cx, cy)."""
        start = math.radians(angle)
        step = 2 * math.pi / sides
        return cls(
            [
                (cx + radius * math.cos(start + i * step), cy + radius * math.sin(start + i * step))
                for i in range(sides)
            ]
        )

    def contains(self, point):
        # Even-odd rule: count how many edges a ray to the left crosses.
        inside = False
        count = len(self.points)
        for i in range(count):
            a, b = self.points[i], self.points[(i + 1) % count]
            if (a.y > point.y) != (b.y > point.y):
                crossing = a.x + (point.y - a.y) / (b.y - a.y) * (b.x - a.x)
                if point.x < crossing:
                    inside = not inside
        return inside

    def hit(self, origin, direction, record):
        count = len(self.points)
        for i in range(count):
            record = ray_segment(
                origin, direction, self.points[i], self.points[(i + 1) % count], record
            )
        return record

    def draw(self, surface, cfg, scale):
        points = [p * scale for p in self.points]
        pygame.draw.polygon(surface, cfg.wall_fill, points)
        pygame.draw.polygon(surface, cfg.wall_edge, points, _edge_width(cfg, scale))


class RectangleWall(PolygonWall):
    """A rectangle with its corner at (x, y), rotated `angle` degrees."""

    def __init__(self, x: float, y: float, width: float, height: float, angle: float = 0.0):
        radians = math.radians(angle)
        along = Vector2(math.cos(radians), math.sin(radians))
        across = Vector2(-math.sin(radians), math.cos(radians))
        corner = Vector2(x, y)
        # Corners in traversal order, so the outline doesn't cross itself.
        super().__init__(
            [
                corner,
                corner + along * width,
                corner + along * width + across * height,
                corner + across * height,
            ]
        )

    @classmethod
    def centered(cls, cx: float, cy: float, width: float, height: float, angle: float = 0.0):
        """A rectangle centred at (cx, cy) rather than cornered there."""
        radians = math.radians(angle)
        along = Vector2(math.cos(radians), math.sin(radians))
        across = Vector2(-math.sin(radians), math.cos(radians))
        corner = Vector2(cx, cy) - along * (width / 2) - across * (height / 2)
        return cls(corner.x, corner.y, width, height, angle)
