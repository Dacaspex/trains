from pygame import Vector2
import pygame


class Canvas:
    def __init__(self, offset: Vector2 = Vector2()):
        self.offset = offset

    def line(self, surface, start: Vector2, end: Vector2, color: (float, float, float), width: int):
        start = Vector2(start.x, -start.y)
        end = Vector2(end.x, -end.y)
        pygame.draw.line(surface, color, start + self.offset, end + self.offset, width)

    def circle(self, surface, center: Vector2, radius: float, color: (float, float, float)):
        x = center.x + self.offset.x
        y = -center.y + self.offset.y
        if x < 0 or y < 0:
            return
        pygame.draw.circle(surface, color, [x, y], radius)

    def arc(self, surface, center: Vector2, radius: float, start_angle: float, stop_angle: float,
            color: (float, float, float), width: int):
        center = Vector2(center.x, -center.y)
        rect = pygame.Rect(center.x - radius + self.offset.x, center.y - radius + self.offset.y, 2 * radius,
                           2 * radius)
        pygame.draw.arc(surface, color, rect, start_angle, stop_angle, width)
