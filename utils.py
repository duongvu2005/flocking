import pygame

def draw_boid(surface, pos, vel, r=6, outline_color=(255, 255, 255)):
    center_to_head = r * vel.normalize()
    center_to_ltail = center_to_head.rotate(160)
    center_to_rtail = center_to_head.rotate(-160)

    head  = pos + center_to_head
    ltail = pos + center_to_ltail
    rtail = pos + center_to_rtail

    pygame.draw.polygon(surface, outline_color, (ltail, head, rtail), 1)
