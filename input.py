import pygame

class Mouse:
    def __init__(self):
        self.previous_left_pressed = False
        self.previous_right_pressed = False
        self.current_left_pressed = False
        self.current_right_pressed = False
        self.mouse_down_position = (0, 0)
        self.current_position = (0, 0)

    def update(self):
        [button1, _, button3] = pygame.mouse.get_pressed(3)
        self.current_position = pygame.mouse.get_pos()
        self.previous_left_pressed = self.current_left_pressed
        self.previous_right_pressed = self.current_right_pressed
        self.current_left_pressed = button1
        self.current_right_pressed = button3
        if not self.previous_left_pressed and self.current_left_pressed:
            self.mouse_down_position = self.current_position
        if not self.previous_right_pressed and self.current_right_pressed:
            self.mouse_down_position = self.current_position

    def is_left_clicked(self):
        return self.previous_left_pressed and not self.current_left_pressed and not self.is_dragging()

    def is_right_clicked(self):
        return self.previous_right_pressed and not self.current_right_pressed and not self.is_dragging()

    def is_dragging(self):
        pressed = self.previous_left_pressed or self.previous_right_pressed
        moved = abs((self.mouse_down_position[0] - self.current_position[0])
                    + (self.mouse_down_position[1] - self.current_position[1])) > 1
        return pressed and moved