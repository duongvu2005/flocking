"""The simulation: owns the boids and the walls, and steps them."""

from __future__ import annotations

import random

from pygame.math import Vector2

from .boid import Boid
from .config import SimConfig
from .walls import Wall


class Flock:
    def __init__(self, cfg: SimConfig, walls: list[Wall] | None = None):
        self.cfg = cfg
        self.boids: list[Boid] = []
        self.walls: list[Wall] = list(walls) if walls else []
        self.rng = random.Random(cfg.seed)

    def populate(self):
        """Scatter `cfg.num_boids` boids across the open parts of the world."""
        for _ in range(self.cfg.num_boids):
            self.add_boid(*self.open_position())

    def open_position(self, attempts=64):
        """A random point outside every wall. Boids that start inside a closed
        wall can never steer out of it, since avoidance only turns them away
        from surfaces they approach from outside."""
        width, height = self.cfg.world_size
        for _ in range(attempts):
            point = Vector2(self.rng.uniform(0, width), self.rng.uniform(0, height))
            if not any(wall.contains(point) for wall in self.walls):
                return point
        return point

    def add_boid(self, x, y):
        self.boids.append(Boid(x, y, self.cfg, self.rng))

    def add_wall(self, wall):
        self.walls.append(wall)

    def step(self, dt):
        for boid in self.boids:
            boid.step(self.boids, self.walls, dt, self.cfg.world_size)

        for wall in self.walls:
            wall.update(dt, self.cfg.world_size)
