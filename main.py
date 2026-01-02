import pygame
from pygame.math import Vector2
import flock
import boid
import wall

def set_up(num_boid, screen_size):
    width, height = screen_size
    flocking = flock.Flock(screen_size)
    for _ in range(num_boid):
        flocking.add_boid(boid.Boid(width/2, height/2))
    
    # example walls
    flocking.add_wall(wall.StraightWall(200, 100, 1080, 100))
    flocking.add_wall(wall.StraightWall(200, 620, 1080, 620))
    flocking.add_wall(wall.CircleWall(200, 300, 30))
    flocking.add_wall(wall.CircleWall(400, 200, 30))
    flocking.add_wall(wall.CircleWall(300, 550, 30, velocity=Vector2(0.5, 0)))
    flocking.add_wall(wall.CircleWall(800, 250, 30))
    flocking.add_wall(wall.CircleWall(900, 450, 30))
    flocking.add_wall(wall.CircleWall(600, 300, 30))
    flocking.add_wall(wall.RectangleWall(1000, 300, 200, 80, 30))
    flocking.add_wall(wall.PolygonWall([
        (50, 300), (70, 320), (90, 350), (100, 400), (80, 420), (70, 430)
    ]))
    return flocking

# Config
WINDOW_SIZE = (1280, 720)
BACKGROUND_COLOR = (30, 30, 30)

# Basic game loop
pygame.init()

# Create window
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

flocking = set_up(250, WINDOW_SIZE)
running = True
mouse_pressed = False

while running:
    # Handle closing window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not mouse_pressed:
                m_x, m_y = pygame.mouse.get_pos()
                flocking.add_boid(boid.Boid(m_x, m_y))
                mouse_pressed = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_pressed = False


    # Draw background (also wipes away things from last frame)
    screen.fill(BACKGROUND_COLOR)

    # Render scene
    dt = clock.tick(60) / 1000 * 100
    # Update the window
    flocking.run(screen, dt)

    pygame.display.flip()

pygame.quit()



