from pygame import Vector2
from network import Node, Track, StraightTrack, CurvedTrack
from geom import Geom


def is_on_left(start: Vector2, direction: Vector2, point: Vector2) -> bool:
    a = start
    b = start + direction
    d = (point.x - a.x) * (b.y - a.y) - (point.y - a.y) * (b.x - a.x)
    return d > 0


def are_nodes_close(a: Node, b: Node, epsilon: float = 0.001) -> bool:
    return are_close(a.position, b.position, epsilon)


def are_close(a: Vector2, b: Vector2, epsilon: float = 0.001) -> bool:
    return a.distance_to(b) < epsilon


def intersects_track(a: Track, b: Track) -> (bool, list):
    if isinstance(a, StraightTrack) and isinstance(b, StraightTrack):
        return Geom.intersects_line_segment_line_segment(a.node_a.position, a.node_b.position, b.node_a.position,
                                                         b.node_b.position)
    elif isinstance(a, StraightTrack) and isinstance(b, CurvedTrack):
        return Geom.intersects_line_segment_circle_segment(a.node_a.position, a.node_b.position, b.center, b.radius,
                                                           b.start_angle, b.stop_angle)
    elif isinstance(a, CurvedTrack) and isinstance(b, StraightTrack):
        return Geom.intersects_line_segment_circle_segment(b.node_a.position, b.node_b.position, a.center, a.radius,
                                                           a.start_angle, a.stop_angle)
    elif isinstance(a, CurvedTrack) and isinstance(b, CurvedTrack):
        return Geom.intersects_circle_segment_circle_segment(a.center, a.radius, a.start_angle, a.stop_angle, b.center,
                                                             b.radius, b.start_angle, b.stop_angle)
    else:
        return False, []
