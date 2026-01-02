import pygame
from pygame.math import Vector2
import random
import math
from wall import HitRecord
import utils

class Boid:
    def __init__(self, x, y):
        """
        Given initial positions x, y (floats), initialize a boid.
        """
        # Kinematics
        self.position = Vector2(x, y)
        # Random velocity with speed = 1
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = Vector2(math.cos(angle), math.sin(angle))
        self.acceleration = Vector2(0, 0)
        # Params
        self.r = 5
        self.desired_sep = 50.0
        self.neighbor_distance = 100.0
        self.max_speed = 2
        self.max_force = 0.03
        self.mass = 1

    def run(self, boids, walls, dt, screen, window_size):
        # applies flocking forces
        self.flock(boids)
        self.avoid_walls(walls)
        self.update(dt)
        self.borders(window_size)
        self.render(screen)

    # Physics helper functions
    def apply_force(self, force):
        self.acceleration += force / self.mass

    def update(self, dt):
        # Update and cap velocity
        self.velocity += self.acceleration * dt
        if self.velocity.magnitude_squared() > 0 :
            self.velocity.clamp_magnitude_ip(self.max_speed)
        # Update position
        self.position += self.velocity * dt 
        # Reset acceleration
        self.acceleration = Vector2(0, 0)        

    def borders(self, window_size):
        width, height = window_size
        self.position.x %= width
        self.position.y %= height

    # Draw to screen
    def render(self, screen):
        utils.draw_boid(screen, self.position, self.velocity, self.r)

    # Walls
    def avoid_walls(self, walls):
        if self.velocity.magnitude_squared() == 0:
            return

        look_ahead = 200
        pos = self.position
        dir = self.velocity.normalize()

        hit_record = HitRecord(look_ahead, None)

        for w in walls:
            hit_record = w.hit(pos, dir, hit_record)

        if hit_record.normal is not None:
            
            # to_wall = pos - hit_point
            # dist_along_normal = to_wall.dot(hit_record.normal)
            # # steer to point 1 radius away from wall
            # steer_force = self.steer(pos - (hit_point + 3 * self.r * hit_record.normal))
            # # self.apply_force(0.5 * steer_force * look_ahead / dist_along_normal)
            # self.apply_force(10 * steer_force)

            away = hit_record.normal
            desired = away * self.max_speed + dir * (0.5 * self.max_speed)
            steer_force = desired - self.velocity
            steer_force.clamp_magnitude_ip(self.max_force)
            # Make obstacle avoidance stronger than flocking
            self.apply_force(5.0 * steer_force)


    # Flocking
    def flock(self, boids):
        sep_force = self.separate(boids)  # Avoid collision with nearby flockmates
        ali_force = self.align(boids)     # Attempt to match velocity w/ nearby flockmates
        coh_force = self.cohesion(boids)  # Attempt to stay close to nearby flockmates

        # Weight the forces
        sep_force *= 1.5
        ali_force *= 1.0
        coh_force *= 1.0

        # Apply
        self.apply_force(sep_force)
        self.apply_force(ali_force)
        self.apply_force(coh_force)

    def separate(self, boids):
        # basically 1/r force law to compute the desired steering direction
        desired_steering = Vector2(0, 0)
        for b in boids:
            dist = self.position.distance_to(b.position)
            if dist > 0 and dist < self.desired_sep:
                desired_steering += (self.position - b.position) / dist**2

        return self.steer(desired_steering)

    def align(self, boids):
        # try to match velocity of group
        desired_steering = Vector2(0, 0)
        for b in boids:
            dist = self.position.distance_to(b.position)
            if dist > 0 and dist < self.neighbor_distance:
                desired_steering += b.velocity

        return self.steer(desired_steering)

    def cohesion(self, boids):
         # try to steer towards the COM of group
        num_neighbor = 0
        group_center = Vector2(0, 0)
        for b in boids:
            dist = self.position.distance_to(b.position)
            if dist > 0 and dist < self.neighbor_distance:
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
        steering_force *= self.max_speed
        steering_force -= self.velocity
        steering_force.clamp_magnitude_ip(self.max_force)
        return steering_force