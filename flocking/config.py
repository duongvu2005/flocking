"""Simulation and display parameters."""

from dataclasses import dataclass

Color = tuple[int, int, int]


@dataclass(frozen=True)
class SimConfig:
    """Parameters that affect how the flock moves."""

    # World. Boids wrap around the edges.
    world_size: tuple[int, int] = (1280, 720)
    num_boids: int = 115
    seed: int | None = None

    # Kinematics. Speeds and forces are per tick; one tick is `tick_seconds`
    # of wall clock. `max_dt` caps the step after a stall.
    tick_seconds: float = 0.01
    max_dt: float = 3.0
    max_speed: float = 1.4
    max_force: float = 0.02
    mass: float = 1.0

    # Interaction radii
    separation_radius: float = 58.0
    neighbor_radius: float = 140.0

    # Flocking weights
    separation_weight: float = 1.7
    alignment_weight: float = 1.1
    cohesion_weight: float = 0.85

    # Obstacle avoidance. Boids cast a ray `lookahead` units ahead;
    # `avoidance_tangent` is the forward momentum kept while sliding past.
    lookahead: float = 200.0
    avoidance_weight: float = 5.0
    avoidance_tangent: float = 0.5
    # Rays cast to look for obstacles, as (angle from heading, reach as a
    # fraction of `lookahead`). The side whiskers are shorter, and catch walls
    # a boid is drifting toward rather than heading straight at.
    whiskers: tuple[tuple[float, float], ...] = (
        (0.0, 1.0),
        (-30.0, 0.55),
        (30.0, 0.55),
    )


@dataclass(frozen=True)
class RenderConfig:
    """Parameters that affect how the flock looks."""

    # Draw to a surface this many times larger, then scale down to anti-alias.
    supersample: int = 2
    fps: int = 60

    background: Color = (18, 18, 20)
    # Alpha of the background blitted over the previous frame, leaving a wake.
    # Lower is a longer trail; 255 clears completely.
    trail_alpha: int = 200

    # "heading" hues each boid by direction of travel, "mono" uses mono_color.
    # Headings map onto `hue_span` degrees starting at `hue_start`, so a narrow
    # span keeps the palette tight rather than running the full spectrum.
    color_mode: str = "mono"
    mono_color: Color = (232, 238, 250)
    hue_start: float = 190.0
    hue_span: float = 90.0
    saturation: float = 0.42
    value: float = 0.98

    # Boid dart, in world units
    boid_length: float = 14.0
    boid_width: float = 6.0

    wall_fill: Color = (36, 38, 46)
    wall_edge: Color = (124, 132, 150)
    wall_width: int = 2
