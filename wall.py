import pygame
from pygame.math import Vector2
from abc import ABC, abstractmethod
from dataclasses import dataclass
import math


@dataclass
class HitRecord:
    t: float
    normal: Vector2


class Wall(ABC):
    @abstractmethod
    def update(self, surface, dt, window_size):
        pass

    @abstractmethod 
    def render(self, surface):
        """
        Any wall must have a render method to display itself to surface.
        """
        pass

    @abstractmethod
    def hit(self, position, direction, hit_record) -> HitRecord:
        pass

class StraightWall(Wall):
    def __init__(self, x1, y1, x2, y2, color=(100, 100, 100), width=2):
        """
        Wall spans from point 1 (x1, y1) to point 2 (x2, y2).
        """
        self.p1 = Vector2(x1, y1)
        self.p2 = Vector2(x2, y2)
        self.color = color
        self.width = width

    def update(self, surface, dt, window_size):
        self.render(surface)

    def render(self, surface):
        pygame.draw.line(surface, self.color, self.p1, self.p2, self.width)

    def hit(self, position : Vector2, direction : Vector2, hit_record) -> HitRecord:
        wall_vec = self.p2 - self.p1
        wall_len = wall_vec.magnitude()
        if wall_len == 0:
            return hit_record
        wall_direction = (wall_vec).normalize()
        wall_normal = direction - direction.project(wall_direction)
        if wall_normal.magnitude_squared() == 0:
            # parallel, doesn't hit wall
            return hit_record
        wall_normal.normalize_ip()
        t = (self.p1 - position).dot(wall_normal) / direction.dot(wall_normal)
        hit_pos = position + direction * t
        u = (hit_pos - self.p1).dot(wall_direction) / wall_len
        if not (0.0 <= u <= 1.0):
            return hit_record

        if t > 0 and t < hit_record.t:
            return HitRecord(t, -wall_normal)
        return hit_record


class CircleWall(Wall):
    def __init__(self, x, y, r, velocity=Vector2(0, 0), color=(100, 100, 100), width=2):
        self.center = Vector2(x, y)
        self.r = r
        self.v = velocity
        self.color = color
        self.width = width

    def update(self, surface, dt, window_size):
        self.center += self.v * dt
        self.borders(window_size)
        self.render(surface)

    def borders(self, window_size):
        width, height = window_size
        self.center.x %= width
        self.center.y %= height

    def render(self, surface):
        pygame.draw.circle(surface, self.color, self.center, self.r, self.width)

    def hit(self, position : Vector2, direction : Vector2, hit_record) -> HitRecord:
        a = direction.dot(direction)
        b = 2 * direction.dot(position - self.center)
        c = (position - self.center).magnitude_squared() - self.r**2
        delta = b**2 - 4*a*c
        if delta < 0:
            return hit_record
        t_plus  = (-b + delta**0.5) / (2*a)
        t_minus = (-b - delta**0.5) / (2*a)
        if t_plus < 0 or t_minus > hit_record.t:
            return hit_record
        if t_minus > 0:
            normal = (position + direction * t_minus - self.center).normalize()
            return HitRecord(t_minus, normal)
        if t_plus < hit_record.t:
            normal = (position + direction * t_plus - self.center).normalize()
            return HitRecord(t_plus, normal)
        
class RectangleWall(Wall):
    def __init__(self, x, y, w, h, angle=0.0, color=(100, 100, 100), width=1):
       angle_rad = math.radians(angle)

       corner_1 = Vector2(x, y)
       corner_2 = corner_1 + Vector2(math.cos(angle_rad), math.sin(angle_rad)) * w
       corner_3 = corner_1 + Vector2(-math.sin(angle_rad), math.cos(angle_rad)) * h
       corner_4 = corner_3 + Vector2(math.cos(angle_rad), math.sin(angle_rad)) * w

       self.edges = [
           StraightWall(corner_1.x, corner_1.y, corner_2.x, corner_2.y, color, width),
           StraightWall(corner_1.x, corner_1.y, corner_3.x, corner_3.y, color, width),
           StraightWall(corner_2.x, corner_2.y, corner_4.x, corner_4.y, color, width),
           StraightWall(corner_3.x, corner_3.y, corner_4.x, corner_4.y, color, width)
       ]

    def update(self, surface, dt, window_size):
        self.render(surface)

    def render(self, surface):
        for edge in self.edges:
            edge.render(surface)

    def hit(self, position, direction, hit_record) -> HitRecord:
        for edge in self.edges:
            hit_record = edge.hit(position, direction, hit_record)
        
        return hit_record

class PolygonWall(Wall):
    def __init__(self, points, color=(100, 100, 100), width=1):
        """
        points: sequence of (x, y) or Vector2.
        """
        self.points = [Vector2(p) for p in points]
        self.color = color
        self.width = width

        self.edges = []
        n = len(self.points)
        for i in range(n):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % n]
            self.edges.append(StraightWall(p1.x, p1.y, p2.x, p2.y, color, width))

    def update(self, surface, dt, window_size):
        self.render(surface)

    def render(self, surface):
        pygame.draw.polygon(surface, self.color, self.points, self.width)

    def hit(self, position: Vector2, direction: Vector2, hit_record: HitRecord) -> HitRecord:
        for edge in self.edges:
            hit_record = edge.hit(position, direction, hit_record)
        
        return hit_record