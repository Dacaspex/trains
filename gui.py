import pygame
from input import Mouse
from network import Network
from geom import Geom
from canvas import Canvas


class Gui:
    MARGIN = 25
    INFO_SCREEN_WIDTH = 300
    INFO_SCREEN_HEIGHT = 100
    INFO_SCREEN_PADDING = 25
    INFO_SCREEN_COLOR = (40, 40, 40)
    INFO_SCREEN_BORDER_RADIUS = 5
    MOUSE_HIT_AREA = 20
    SELECTED_TRACK_COLOR = (100, 255, 100)

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
        for track in self.network.tracks:
            intersects, _ = Geom.intersects_line_segment_circle(track.node_a.position, track.node_b.position, mouse_circle_center, self.MOUSE_HIT_AREA)
            if intersects:
                selected_track = track
                break

        if selected_track is None:
            return

        # Info screen
        container_x = self.screen_width - self.MARGIN - self.INFO_SCREEN_WIDTH
        container_y = 0 + self.MARGIN
        text = self.font.render(f'Track id: {selected_track.id}', True, (255, 255, 255))
        text_x = container_x + self.INFO_SCREEN_PADDING
        text_y = container_y + self.INFO_SCREEN_PADDING
        container_h = 2 * self.INFO_SCREEN_PADDING + text.get_rect().height

        pygame.draw.rect(screen, self.INFO_SCREEN_COLOR, (container_x, container_y, self.INFO_SCREEN_WIDTH, container_h),
                         border_radius=self.INFO_SCREEN_BORDER_RADIUS)
        screen.blit(text, (text_x, text_y))
        self.canvas.line(screen, selected_track.node_a.position, selected_track.node_b.position, self.SELECTED_TRACK_COLOR, selected_track.width)
