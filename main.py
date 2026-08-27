"""Real-time flocking simulation with obstacle avoidance."""

import argparse

import pygame

from flocking import scenes
from flocking.config import RenderConfig, SimConfig
from flocking.flock import Flock
from flocking.render import Renderer


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boids", type=int, default=SimConfig.num_boids)
    parser.add_argument("--scene", default="full_scale", choices=sorted(scenes.SCENES))
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--color", default=RenderConfig.color_mode, choices=["heading", "mono"])
    return parser.parse_args()


def main():
    args = parse_args()
    sim_cfg = SimConfig(num_boids=args.boids, seed=args.seed)
    render_cfg = RenderConfig(color_mode=args.color)

    flocking = Flock(sim_cfg, scenes.build(args.scene))
    flocking.populate()

    pygame.init()
    screen = pygame.display.set_mode(sim_cfg.world_size)
    pygame.display.set_caption("flocking")
    clock = pygame.time.Clock()
    renderer = Renderer(render_cfg, sim_cfg.world_size)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                flocking.add_boid(*pygame.mouse.get_pos())

        elapsed = clock.tick(render_cfg.fps) / 1000
        flocking.step(min(elapsed / sim_cfg.tick_seconds, sim_cfg.max_dt))

        renderer.draw(screen, flocking)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
