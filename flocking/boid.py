"""A single agent and its steering forces."""

from __future__ import annotations

import math
import random

from pygame.math import Vector2

from .config import SimConfig
from .geometry import HitRecord
from .walls import Wall


class Boid:
    def __init__(self, x: float, y: float, cfg: SimConfig, rng: random.Random):
        """
        Given initial positions x, y (floats), initialize a boid.
        """
        self.cfg = cfg
        # Kinematics
        self.position = Vector2(x, y)
        # Random velocity with speed = 1
        angle = rng.uniform(0, 2 * math.pi)
        self.velocity = Vector2(math.cos(angle), math.sin(angle))
        self.acceleration = Vector2(0, 0)

    def step(self, boids, walls, dt, world_size):
        # applies flocking forces
        self.flock(boids)
        self.avoid_walls(walls)
        self.update(dt)
        self.wrap(world_size)

    # Physics helper functions
    def apply_force(self, force):
        self.acceleration += force / self.cfg.mass

    def update(self, dt):
        # Update and cap velocity
        self.velocity += self.acceleration * dt
        if self.velocity.magnitude_squared() > 0:
            self.velocity.clamp_magnitude_ip(self.cfg.max_speed)
        # Update position
        self.position += self.velocity * dt
        # Reset acceleration
        self.acceleration = Vector2(0, 0)

    def wrap(self, world_size):
        width, height = world_size
        self.position.x %= width
        self.position.y %= height

    # Walls
    def avoid_walls(self, walls: list[Wall]):
        if self.velocity.magnitude_squared() == 0:
            return

        pos = self.position
        dir = self.velocity.normalize()

        # Cast each whisker separately and keep whichever finds the nearest
        # surface, so a wall off to the side still registers.
        hit_record = HitRecord(self.cfg.lookahead, None)
        for angle, reach in self.cfg.whiskers:
            ray = dir.rotate(angle)
            found = HitRecord(self.cfg.lookahead * reach, None)
            for w in walls:
                found = w.hit(pos, ray, found)
            if found.normal is not None and found.t < hit_record.t:
                hit_record = found

        if hit_record.normal is None:
            return

        # Steer along the surface normal, keeping some forward momentum so the
        # boid slides past the wall instead of stopping dead against it.
        away = hit_record.normal
        desired = away * self.cfg.max_speed + dir * (self.cfg.avoidance_tangent * self.cfg.max_speed)
        steer_force = desired - self.velocity
        steer_force.clamp_magnitude_ip(self.cfg.max_force)
        # Make obstacle avoidance stronger than flocking
        self.apply_force(self.cfg.avoidance_weight * steer_force)

    # Flocking
    def flock(self, boids):
        sep_force = self.separate(boids)  # Avoid collision with nearby flockmates
        ali_force = self.align(boids)     # Attempt to match velocity w/ nearby flockmates
        coh_force = self.cohesion(boids)  # Attempt to stay close to nearby flockmates

        # Weight the forces
        sep_force *= self.cfg.separation_weight
        ali_force *= self.cfg.alignment_weight
        coh_force *= self.cfg.cohesion_weight

        # Apply
        self.apply_force(sep_force)
        self.apply_force(ali_force)
        self.apply_force(coh_force)

    def separate(self, boids):
        # basically 1/r force law to compute the desired steering direction
        desired_steering = Vector2(0, 0)
        for b in boids:
            dist = self.position.distance_to(b.position)
            if dist > 0 and dist < self.cfg.separation_radius:
                desired_steering += (self.position - b.position) / dist**2

        return self.steer(desired_steering)

    def align(self, boids):
        # try to match velocity of group
        desired_steering = Vector2(0, 0)
        for b in boids:
            dist = self.position.distance_to(b.position)
            if dist > 0 and dist < self.cfg.neighbor_radius:
                desired_steering += b.velocity

        return self.steer(desired_steering)

    def cohesion(self, boids):
        # try to steer towards the COM of group
        num_neighbor = 0
        group_center = Vector2(0, 0)
        for b in boids:
            dist = self.position.distance_to(b.position)
            if dist > 0 and dist < self.cfg.neighbor_radius:
                group_center += b.position
                num_neighbor += 1

        if num_neighbor > 0:
            group_center /= num_neighbor
            desired_steering = group_center - self.position
            return self.steer(desired_steering)

        return Vector2(0, 0)

    def steer(self, direction: Vector2):
        # Given desired steering direction, return the steering force
        if direction.magnitude_squared() == 0:
            return Vector2(0, 0)

        steering_force = direction.normalize()
        steering_force *= self.cfg.max_speed
        steering_force -= self.velocity
        steering_force.clamp_magnitude_ip(self.cfg.max_force)
        return steering_force
