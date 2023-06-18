import pygame
from canvas import Canvas
from debug import Debug
import util
from geom import VectorUtil, Geom
import math

ids = {
    'track': 0,
    'node': 0
}

# TRACK_WIDTH = 3
# NODE_SIZE   = 8
TRACK_WIDTH = 6
NODE_SIZE   = 16


class Direction:
    RIGHT = 1
    LEFT = 2


def get_id(id_type):
    global ids
    assigned_id = ids[id_type]
    ids[id_type] = ids[id_type] + 1
    return assigned_id


class StraightTrackOptions:
    def __init__(self, length):
        self.length = length


class CurvedTrackOptions:
    def __init__(self, direction: Direction, radius: float, angle: float):
        self.direction = direction
        self.radius = radius
        self.angle = angle


class Track:
    def __init__(self, canvas: Canvas, node_a, node_b):
        self.id = get_id('track')
        self.canvas = canvas
        self.node_a = node_a
        self.node_b = node_b
        self.color = (255, 255, 255)
        self.width = TRACK_WIDTH

    def get_direction_vector(self, node) -> pygame.Vector2:
        pass


class StraightTrack(Track):
    def __init__(self, canvas, node_a, node_b):
        super().__init__(canvas, node_a, node_b)

    def get_direction_vector(self, node):
        if node is self.node_a:
            v1 = self.node_a
            v2 = self.node_b
        else:
            v1 = self.node_b
            v2 = self.node_a
        return pygame.Vector2(v1.position.x - v2.position.x, v1.position.y - v2.position.y).normalize()

    def draw(self, surface):
        self.canvas.line(surface, self.node_a.position, self.node_b.position, self.color, self.width)


class CurvedTrack(Track):
    def __init__(self, canvas: Canvas, node_a, node_b, center: pygame.Vector2, radius: float, start_angle: float,
                 stop_angle: float):
        super().__init__(canvas, node_a, node_b)
        self.center = center
        self.radius = radius
        self.start_angle = start_angle
        self.stop_angle = stop_angle

    def get_direction_vector(self, node) -> pygame.Vector2:
        start_vector = VectorUtil.from_angle(self.start_angle) * self.radius
        stop_vector = VectorUtil.from_angle(self.stop_angle) * self.radius
        if util.are_close(self.center + start_vector, node.position):
            return VectorUtil.rotate_clockwise(start_vector).normalize()
        if util.are_close(self.center + stop_vector, node.position):
            return VectorUtil.rotate_counter_clockwise(stop_vector).normalize()
        raise AssertionError()

    def draw(self, surface):
        self.canvas.arc(surface, self.center, self.radius, self.start_angle, self.stop_angle, self.color, self.width)


class Node:
    def __init__(self, canvas, position: pygame.Vector2):
        self.id = get_id('node')
        self.canvas = canvas
        self.position = position
        self.color = (75, 75, 75)
        self.size = NODE_SIZE

    def draw(self, surface):
        self.canvas.circle(surface, self.position, self.size, self.color)


class Network:
    def __init__(self, canvas):
        self.canvas = canvas
        self.nodes = []
        self.tracks = []

    def add_track(self, track: Track):
        self._add_track(track)
        pass

    def build_track(self, source_node: Node, source_track: Track, track_options) -> (Node, Track):
        if isinstance(track_options, StraightTrackOptions):
            new_node, new_track = self._add_straight_track(source_node, source_track, track_options)
        elif isinstance(track_options, CurvedTrackOptions):
            new_node, new_track = self._add_curved_track(source_node, source_track, track_options)
        else:
            raise Exception()

        self._add_track(new_track, skip_check_node_a=True)
        return new_node, new_track

    def _add_track(self, new_track: Track, skip_check_node_a=False, skip_check_node_b=False, skip_check_intersections=False):
        # Check whether nodes are duplicates of other nodes
        for node in self.nodes:
            if not skip_check_node_a:
                if util.are_nodes_close(node, new_track.node_a, epsilon=1):
                    new_track.node_a = node
                    skip_check_node_a = True
            if not skip_check_node_b:
                if util.are_nodes_close(node, new_track.node_b, epsilon=1):
                    new_track.node_b = node
                    skip_check_node_b = True

        if not skip_check_node_a:
            self.nodes.append(new_track.node_a)
        if not skip_check_node_b:
            self.nodes.append(new_track.node_b)

        # Check whether track overlaps any other track
        if skip_check_intersections:
            self.tracks.append(new_track)
            return

        track_invalid = False
        track_to_remove = []
        for track in self.tracks:
            intersects, intersections = util.intersects_track(new_track, track)
            if not intersects:
                continue

            for intersection in intersections:
                if not self._is_valid_intersection(intersection):
                    continue
                track_invalid = True
                # Split track
                node_split = Node(self.canvas, intersection)
                if isinstance(new_track, StraightTrack):
                    track_a = StraightTrack(self.canvas, new_track.node_a, node_split)
                    track_b = StraightTrack(self.canvas, new_track.node_b, node_split)
                    self._add_track(track_a, skip_check_node_a=True)
                    self._add_track(track_b, skip_check_node_a=True, skip_check_node_b=True)
                elif isinstance(new_track, CurvedTrack):
                    split_angle = Geom.full_angle_to_horizon(intersection - new_track.center)
                    start_angle = new_track.start_angle if new_track.start_angle < new_track.stop_angle else new_track.stop_angle
                    stop_angle = new_track.stop_angle if new_track.start_angle < new_track.stop_angle else new_track.start_angle
                    track_a = CurvedTrack(self.canvas, new_track.node_a, node_split, new_track.center, new_track.radius, start_angle, split_angle)
                    track_b = CurvedTrack(self.canvas, new_track.node_b, node_split, new_track.center, new_track.radius,
                                          split_angle, stop_angle)
                    self._add_track(track_a, skip_check_node_a=True)
                    self._add_track(track_b, skip_check_node_a=True, skip_check_node_b=True)

                track_to_remove.append(track)
                if isinstance(track, StraightTrack):
                    track_a = StraightTrack(self.canvas, track.node_a, node_split)
                    track_b = StraightTrack(self.canvas, track.node_b, node_split)
                    self._add_track(track_a, skip_check_node_a=True, skip_check_node_b=True, skip_check_intersections=True)
                    self._add_track(track_b, skip_check_node_a=True, skip_check_node_b=True, skip_check_intersections=True)
                    pass
                elif isinstance(track, CurvedTrack):
                    split_angle = Geom.full_angle_to_horizon(intersection - track.center)
                    track_a = CurvedTrack(self.canvas, track.node_a, node_split, track.center, track.radius, track.start_angle, split_angle)
                    track_b = CurvedTrack(self.canvas, track.node_b, node_split, track.center, track.radius,
                                          split_angle, track.stop_angle)
                    self._add_track(track_a, skip_check_node_a=True, skip_check_node_b=True, skip_check_intersections=True)
                    self._add_track(track_b, skip_check_node_a=True, skip_check_node_b=True,
                                    skip_check_intersections=True)

        for track in track_to_remove:
            self.tracks.remove(track)

        if not track_invalid:
            self.tracks.append(new_track)

    def _is_valid_intersection(self, coord: pygame.Vector2):
        for node in self.nodes:
            if util.are_close(node.position, coord):
                return False
        return True

    def _add_straight_track(self, source_node: Node, source_track: Track, options: StraightTrackOptions) \
            -> (Node, StraightTrack):
        direction = source_track.get_direction_vector(source_node)
        end_position = source_node.position + direction * options.length
        new_node = Node(self.canvas, end_position)
        new_track = StraightTrack(self.canvas, source_node, new_node)
        return new_node, new_track

    def _add_curved_track(self, source_node: Node, source_track: Track, options: CurvedTrackOptions) \
            -> (Node, CurvedTrack):
        direction = source_track.get_direction_vector(source_node)
        if options.direction is Direction.RIGHT:
            center_direction = VectorUtil.rotate_clockwise(direction)
        else:
            center_direction = VectorUtil.rotate_counter_clockwise(direction)

        center_position = source_node.position + center_direction * options.radius

        rotation = options.angle if options.direction is Direction.LEFT else -options.angle
        start_vector = (source_node.position - center_position).normalize()
        stop_vector = start_vector.rotate_rad(rotation)

        start_angle = Geom.full_angle_to_horizon(start_vector)
        stop_angle = Geom.full_angle_to_horizon(stop_vector)

        if options.direction is Direction.LEFT and start_angle > stop_angle:
            pass
        if options.direction is Direction.RIGHT and start_angle > stop_angle:
            temp = start_angle
            start_angle = stop_angle
            stop_angle = temp

        new_node = Node(self.canvas, center_position + stop_vector * options.radius)
        new_track = CurvedTrack(self.canvas, source_node, new_node, center_position, options.radius,
                                start_angle, stop_angle)
        return new_node, new_track

    def draw(self, surface):
        for track in self.tracks:
            track.draw(surface)

        for node in self.nodes:
            node.draw(surface)
