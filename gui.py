import pygame
from typing import Optional

import network
from input import Mouse
from network import Network, StraightTrack, CurvedTrack
from geom import Geom
from canvas import Canvas


class Gui:
    MARGIN = 25
    INFO_SCREEN_WIDTH = 300
    INFO_SCREEN_HEIGHT = 100
    INFO_SCREEN_PADDING = 25
    INFO_SCREEN_COLOR = (40, 40, 40)
    INFO_SCREEN_BORDER_RADIUS = 5
    MOUSE_HIT_AREA = 30
    SELECTED_TRACK_COLOR = (100, 255, 100)
    CONNECTED_TRACK_COLOR = (100, 100, 200)

    def __init__(self, mouse: Mouse, font: pygame.font.Font, canvas: Canvas, screen_width: int, screen_height: int, network: Network):
        self.mouse = mouse
        self.font = font
        self.canvas = canvas
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.network = network
        pass

    def draw(self, screen: pygame.surface.Surface):
        selected_track = None
        mouse_position = self.mouse.current_position - self.canvas.offset
        mouse_circle_center = pygame.Vector2(mouse_position[0], -mouse_position[1])

        selected_track = self._get_track_near_position(mouse_circle_center, self.MOUSE_HIT_AREA)
        selected_node = self._get_node_near_position(mouse_circle_center, self.MOUSE_HIT_AREA)

        if selected_track is None and selected_node is None:
            return
        elif selected_node is not None:
            self._show_node_info(screen, selected_node)
        elif selected_track is not None:
            self._show_track_info(screen, selected_track)

    def _show_track_info(self, screen: pygame.surface.Surface, selected_track: network.Track):
        container_x = self.screen_width - self.MARGIN - self.INFO_SCREEN_WIDTH
        container_y = 0 + self.MARGIN
        text = self.font.render(f'Track id: {selected_track.id}', True, (255, 255, 255))
        text_x = container_x + self.INFO_SCREEN_PADDING
        text_y = container_y + self.INFO_SCREEN_PADDING
        container_h = 2 * self.INFO_SCREEN_PADDING + text.get_rect().height

        pygame.draw.rect(screen, self.INFO_SCREEN_COLOR,
                         (container_x, container_y, self.INFO_SCREEN_WIDTH, container_h),
                         border_radius=self.INFO_SCREEN_BORDER_RADIUS)
        screen.blit(text, (text_x, text_y))

        if isinstance(selected_track, StraightTrack):
            self.canvas.line(screen, selected_track.node_a.position, selected_track.node_b.position,
                             self.SELECTED_TRACK_COLOR, selected_track.width)
        elif isinstance(selected_track, CurvedTrack):
            self.canvas.arc(screen, selected_track.center, selected_track.radius, selected_track.start_angle,
                            selected_track.stop_angle, self.SELECTED_TRACK_COLOR, selected_track.width)

    def _show_node_info(self, screen: pygame.surface.Surface, selected_node: network.Node):
        container_x = self.screen_width - self.MARGIN - self.INFO_SCREEN_WIDTH
        container_y = 0 + self.MARGIN
        text = self.font.render(f'Node id: {selected_node.id}', True, (255, 255, 255))
        text_x = container_x + self.INFO_SCREEN_PADDING
        text_y = container_y + self.INFO_SCREEN_PADDING
        container_h = 2 * self.INFO_SCREEN_PADDING + text.get_rect().height

        pygame.draw.rect(screen, self.INFO_SCREEN_COLOR,
                         (container_x, container_y, self.INFO_SCREEN_WIDTH, container_h),
                         border_radius=self.INFO_SCREEN_BORDER_RADIUS)
        screen.blit(text, (text_x, text_y))

        self.canvas.circle(screen, selected_node.position, selected_node.size, self.SELECTED_TRACK_COLOR)
        for track in selected_node.connections.tracks:
            if isinstance(track, StraightTrack):
                self.canvas.line(screen, track.node_a.position, track.node_b.position,
                                 self.CONNECTED_TRACK_COLOR, track.width)
            elif isinstance(track, CurvedTrack):
                self.canvas.arc(screen, track.center, track.radius, track.start_angle,
                                track.stop_angle, self.CONNECTED_TRACK_COLOR, track.width)

    def _get_track_near_position(self, position, radius) -> Optional[network.Track]:
        for track in self.network.tracks:
            intersects = False
            if isinstance(track, StraightTrack):
                intersects, _ = Geom.intersects_line_segment_circle(track.node_a.position, track.node_b.position,
                                                                    position, radius)
            elif isinstance(track, CurvedTrack):
                intersects, _ = Geom.intersects_circle_segment_circle(track.center, track.radius, track.start_angle,
                                                                      track.stop_angle, position,
                                                                      radius)
            if intersects:
                return track
        return None

    def _get_node_near_position(self, position, radius) -> Optional[network.Node]:
        for node in self.network.nodes:
            intersects, _ = Geom.intersects_circle_circle(node.position, node.size, position, radius)
            if intersects:
                return node
        return None