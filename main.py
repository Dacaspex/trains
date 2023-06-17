import pygame

import util
from network import Network, StraightTrack, CurvedTrack, Node, StraightTrackOptions, CurvedTrackOptions, Direction
from trackset import DefaultTrackBuilder
from grid import Grid
from canvas import Canvas
from input import Mouse
from debug import Debug
import math

pygame.init()

SCREEN_WIDTH    = 1600
SCREEN_HEIGHT   = 1000
GRID_DIMENSION  = 200
background_color = (25, 25, 25)
white = (255, 255, 255)
running = True

mouse = Mouse()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
canvas = Canvas(pygame.Vector2(0, SCREEN_HEIGHT))
grid = Grid(canvas, GRID_DIMENSION, SCREEN_WIDTH, SCREEN_HEIGHT)
network = Network(canvas)
Debug.canvas = canvas

node1 = Node(canvas, pygame.Vector2(150, 50))
node2 = Node(canvas, pygame.Vector2(200, 100))
# node2 = Node(canvas, pygame.Vector2(400, 700))
node3 = Node(canvas, pygame.Vector2(500, 50))
node4 = Node(canvas, pygame.Vector2(350, 175))
track1 = StraightTrack(canvas, node1, node2)
track2 = StraightTrack(canvas, node3, node4)
_, track4 = network.build_track(node2, track1, CurvedTrackOptions(Direction.LEFT, 400, math.pi / 3))

network.add_track(track1)
network.add_track(track2)
node5, track3 = network.build_track(node4, track2, CurvedTrackOptions(Direction.RIGHT, 300, math.pi / 3))

from geom import Geom
a_center = pygame.Vector2(500, 500)
a_radius = 100
b_center = pygame.Vector2(500, 600)
b_radius = 100
count, a, b = Geom.intersects_circle_circle(a_center, a_radius, b_center, b_radius)
print(a)
print(b)
Debug.circle(a_center, a_radius, (255, 0, 0))
Debug.circle(b_center, b_radius, (0, 255, 0))
Debug.circle(a, 10)
Debug.circle(b, 10)

# network.add_track(node2, track1, StraightTrackOptions(100))

builder = DefaultTrackBuilder(network, track1, node2, in_compass_direction=True)
# builder.left() \
#     .right() \
#     .straight() \
#     .back(2) \
#     .straight() \
#     .right() \
#     .straight()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse.update()
    mouse_movement = pygame.mouse.get_rel()
    if mouse.is_dragging():
        canvas.offset += mouse_movement

    if mouse.is_right_clicked():
        network.nodes.append(Node(canvas, mouse.current_position - canvas.offset))
        mouse.is_right_clicked()

    screen.fill(background_color)

    grid.draw(screen)
    # network.draw(screen)
    Debug.draw(screen)

    # vector = util.vector_from_angle(math.pi / 3) * 100
    # center = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    # pygame.draw.line(screen, (0, 255, 0), center, center + vector)
    # pygame.draw.circle(screen, (100, 100, 100), center, 10)

    pygame.display.update()
