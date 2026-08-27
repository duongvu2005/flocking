"""All the drawing."""

from __future__ import annotations

import math

import pygame
from pygame.math import Vector2

from .config import RenderConfig


class Renderer:
    """Draws the flock onto a supersampled canvas, then scales it down."""

    def __init__(self, cfg: RenderConfig, world_size: tuple[int, int]):
        self.cfg = cfg
        self.scale = cfg.supersample
        width, height = world_size
        size = (width * self.scale, height * self.scale)

        self.canvas = pygame.Surface(size)
        self.canvas.fill(cfg.background)
        # Blitted over the previous frame instead of clearing it, so boids
        # leave a fading wake. Per-surface alpha rather than per-pixel, which
        # blits a good deal faster at this size.
        self.fade = pygame.Surface(size)
        self.fade.fill(cfg.background)
        self.fade.set_alpha(cfg.trail_alpha)

    def draw(self, screen: pygame.Surface, flock):
        self.canvas.blit(self.fade, (0, 0))

        for wall in flock.walls:
            wall.draw(self.canvas, self.cfg, self.scale)
        for boid in flock.boids:
            self.draw_boid(boid)

        pygame.transform.smoothscale(self.canvas, screen.get_size(), screen)

    def draw_boid(self, boid):
        if boid.velocity.magnitude_squared() == 0:
            heading = Vector2(1, 0)
        else:
            heading = boid.velocity.normalize()
        side = Vector2(-heading.y, heading.x)

        length = self.cfg.boid_length
        half_width = self.cfg.boid_width / 2
        pos = boid.position

        # A swept dart: nose out front, two swept-back wings, and a notch in
        # the tail so the heading stays readable at this size.
        points = [
            pos + heading * (0.6 * length),
            pos - heading * (0.4 * length) + side * half_width,
            pos - heading * (0.25 * length),
            pos - heading * (0.4 * length) - side * half_width,
        ]
        pygame.draw.polygon(
            self.canvas, self.color_for(heading), [p * self.scale for p in points]
        )

    def color_for(self, heading: Vector2):
        if self.cfg.color_mode == "mono":
            return self.cfg.mono_color

        turn = (math.degrees(math.atan2(heading.y, heading.x)) % 360) / 360
        hue = (self.cfg.hue_start + turn * self.cfg.hue_span) % 360
        color = pygame.Color(0)
        color.hsva = (hue, self.cfg.saturation * 100, self.cfg.value * 100, 100)
        return color
