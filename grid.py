import math
import pygame


class Grid:
    def __init__(self, canvas, grid_dimension, screen_width, screen_height):
        self.canvas = canvas
        self.grid_dimension = grid_dimension
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.color = (50, 50, 50)
        self.width = 1

    def draw(self, surface):
        x_ticks = math.floor(self.screen_width / self.grid_dimension) + 1
        y_ticks = math.floor(self.screen_height / self.grid_dimension) + 1
        for i in range(x_ticks):
            offset = self.canvas.offset[0] % self.grid_dimension
            x = i * self.grid_dimension + offset
            pygame.draw.line(surface, self.color, (x, 0), (x, self.screen_height), self.width)
        for i in range(y_ticks):
            offset = self.canvas.offset[1] % self.grid_dimension
            y = i * self.grid_dimension + offset
            pygame.draw.line(surface, self.color, (0, y), (self.screen_width, y), self.width)
