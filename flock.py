class Flock:
    def __init__(self, window_size, boids=[], walls=[]):
        self.window_size = window_size
        self.boids = boids
        self.walls = walls

    def run(self, screen, dt):
        for boid in self.boids:
            boid.run(self.boids, self.walls, dt, screen, self.window_size)

        for wall in self.walls:
            wall.update(screen, dt, self.window_size)

    def add_boid(self, boid):
        self.boids.append(boid)

    def add_wall(self, wall):
        self.walls.append(wall)
