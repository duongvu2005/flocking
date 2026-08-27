"""Ray intersection tests against obstacle primitives.

`direction` is always a unit vector, so `t` is a distance in world units.
Each function returns either the record it was given or a strictly closer one.
"""

from __future__ import annotations

from dataclasses import dataclass

from pygame.math import Vector2


@dataclass(frozen=True)
class HitRecord:
    """Nearest intersection so far: distance `t`, and the unit surface normal
    there, pointing back toward the ray origin. `normal` is None when nothing
    has been hit within `t`."""

    t: float
    normal: Vector2 | None = None


def ray_segment(
    origin: Vector2,
    direction: Vector2,
    a: Vector2,
    b: Vector2,
    record: HitRecord,
) -> HitRecord:
    """Test the ray against the segment from a to b."""
    span = b - a
    length = span.magnitude()
    if length == 0:
        return record
    along = span / length

    # The part of the ray direction perpendicular to the segment, so the
    # normal points from the boid into the wall.
    normal = direction - direction.project(along)
    if normal.magnitude_squared() == 0:
        # parallel, doesn't hit
        return record
    normal.normalize_ip()

    t = (a - origin).dot(normal) / direction.dot(normal)
    if t <= 0 or t >= record.t:
        return record

    # The ray meets the infinite line; check it lands on the segment.
    u = (origin + direction * t - a).dot(along) / length
    if not 0.0 <= u <= 1.0:
        return record

    return HitRecord(t, -normal)


def ray_circle(
    origin: Vector2,
    direction: Vector2,
    center: Vector2,
    radius: float,
    record: HitRecord,
) -> HitRecord:
    """Test the ray against the circle at `center`."""
    if radius <= 0:
        return record

    # Quadratic in t. |direction| is 1, so the leading coefficient drops out.
    offset = origin - center
    b = 2 * direction.dot(offset)
    c = offset.magnitude_squared() - radius * radius
    discriminant = b * b - 4 * c
    if discriminant < 0:
        return record

    root = discriminant**0.5
    near = (-b - root) / 2
    far = (-b + root) / 2

    # Inside the circle the near root is behind us, so the surface ahead is the far one.
    t = near if near > 0 else far
    if t <= 0 or t >= record.t:
        return record

    normal = (origin + direction * t - center).normalize()
    return HitRecord(t, normal)
