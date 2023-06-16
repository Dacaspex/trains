from pygame import Vector2
from canvas import Canvas


class Debug:
    canvas = None
    shapes = []

    @staticmethod
    def line(a: Vector2, b: Vector2, color=(255, 127, 80)):
        Debug.shapes.append(Line(Debug.canvas, a, b, color))

    @staticmethod
    def circle(center: Vector2, radius: float, color=(255, 127, 80)):
        Debug.shapes.append(Circle(Debug.canvas, center, radius, color))

    @staticmethod
    def draw(surface):
        for shape in Debug.shapes:
            shape.draw(surface)


class DebugShape:
    def __init__(self, canvas: Canvas, color: (float, float, float)):
        self.canvas = canvas
        self.color = color

    def draw(self, surface):
        pass


class Line(DebugShape):
    def __init__(self, canvas: Canvas, a: Vector2, b: Vector2, color: (float, float, float)):
        super().__init__(canvas, color)
        self.a = a
        self.b = b
        self.width = 2

    def draw(self, surface):
        self.canvas.line(surface, self.a, self.b, self.color, self.width)


class Circle(DebugShape):
    def __init__(self, canvas: Canvas, center: Vector2, radius: float, color: (float, float, float)):
        super().__init__(canvas, color)
        self.center = center
        self.radius = radius

    def draw(self, surface):
        self.canvas.circle(surface, self.center, self.radius, self.color)
