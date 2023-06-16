import math
from network import Network, StraightTrackOptions, CurvedTrackOptions, Direction, Node, Track


class Default:
    HALF_TURN = 0.25 * math.pi

    def __init__(self, track_separation_distance):
        self.track_separation_distance = track_separation_distance / 2
        self.radius = self.track_separation_distance / (1 - math.cos(self.HALF_TURN))
        self.compass_direction_length = self.radius * math.sin(self.HALF_TURN)
        self.diagonal_direction_length = self.compass_direction_length / math.sin(self.HALF_TURN)

    def straight(self, in_compass_direction=True):
        if in_compass_direction:
            return StraightTrackOptions(self.compass_direction_length)
        else:
            return StraightTrackOptions(self.diagonal_direction_length)

    def curve(self, direction: Direction):
        return CurvedTrackOptions(direction, self.radius, self.HALF_TURN)


class DefaultTrackBuilder:
    def __init__(self, network: Network, initial_track: Track, initial_node: Node, in_compass_direction=True):
        self.network = network
        self.stack = [(initial_track, initial_node, in_compass_direction)]
        self.set = Default(track_separation_distance=100)

    def straight(self) -> 'DefaultTrackBuilder':
        (track, node, in_compass_direction) = self.stack[-1]
        new_node, new_track = self.network.build_track(node, track, self.set.straight(in_compass_direction))
        self.stack.append((new_track, new_node, in_compass_direction))
        return self

    def left(self) -> 'DefaultTrackBuilder':
        (track, node, in_compass_direction) = self.stack[-1]
        new_node, new_track = self.network.build_track(node, track, self.set.curve(Direction.LEFT))
        self.stack.append((new_track, new_node, not in_compass_direction))
        return self

    def right(self) -> 'DefaultTrackBuilder':
        (track, node, in_compass_direction) = self.stack[-1]
        new_node, new_track = self.network.build_track(node, track, self.set.curve(Direction.RIGHT))
        self.stack.append((new_track, new_node, not in_compass_direction))
        return self

    def back(self, amount=1) -> 'DefaultTrackBuilder':
        for i in range(amount):
            self.stack.pop()
        return self
