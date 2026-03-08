import pygame
import Spritehandlers as Spr
import Texthandlers as Txt

class Window:
    def __init__(self, x: int, y: int, width: int, height: int, title: str, atlas: str, frameless: bool = False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.frameless = frameless
        self.grabbed = False
        self.resize_grabbed = False
        self.grabbed_offset = (0, 0)
        self.size_offset = (0, 0)
        self.colors = [(0, 0, 0, 255), (255, 255, 255, 255), (255, 255, 255, 255)]
        self.outline = True
        self.atlas = Spr.UIAtlas(atlas)
        self.font = Txt.Font("uifont.png", 8, 8, ("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-*!.\uE00D "), 14)
        self.widgets = []

    def get_button_sprite(self):
        return self.atlas.button_spr

    def set_theme(self, colors, outline: bool = True):
        self.colors = colors
        self.outline = outline

    def render(self, surface):
        internal_x = self.x
        internal_y = self.y
        if not self.frameless:
            internal_y += 8
            if self.atlas == None:
                if self.outline:
                    pygame.draw.rect(surface, self.colors[0], (internal_x - 1, self.y - 1, self.width + 2, 10))
                else:
                    pygame.draw.rect(surface, self.colors[0], (internal_x, self.y, self.width, 8))
        if self.atlas == None:
            if self.outline:
                pygame.draw.rect(surface, self.colors[0], (internal_x - 1, internal_y - 1, self.width + 2, self.height + 2))
            pygame.draw.rect(surface, self.colors[1], (internal_x, internal_y, self.width, self.height))
        else:
            self.atlas.draw_window(internal_x, self.y, self.width, self.height, surface, self.frameless)
        
        if not self.frameless:
            truncated_title = self.title[:self.width // 8 - 2].strip().upper()
            if len(truncated_title) < len(self.title):
                truncated_title += ":elipses:"
            self.font.draw(surface, truncated_title, internal_x + 2, self.y + 1, 1, self.colors[2], 0)

        for widget in self.widgets:
            widget.render(internal_x + 2, internal_y + 2, surface)

    #Input example:
    # [(mouse_x, mouse_y), (mouse_leftclick, mouse_midclick, mouse_rightclick)]
    def update(self, input, screen_size):
        if not input[1][0]:
            self.grabbed = False
            self.resize_grabbed = False
        if not self.grabbed and not self.resize_grabbed and not self.frameless and input[1][0] and input[0][0] > self.x and input[0][0] < self.x + self.width and input[0][1] > self.y and input[0][1] < self.y + 8:
            self.grabbed = True
            self.grabbed_offset = (input[0][0] - self.x,input[0][1] - self.y)
        if not self.resize_grabbed and not self.frameless and input[1][0] and input[0][0] > self.x + self.width - 8 and input[0][0] < self.x + self.width:
            self.resize_grabbed = True
            self.grabbed_offset = (input[0][0], input[0][1])
            self.size_offset = (self.width, self.height)
        if self.grabbed:
            self.x = input[0][0] - self.grabbed_offset[0]
            self.y = input[0][1] - self.grabbed_offset[1]
        elif self.resize_grabbed:
            self.width = self.size_offset[0] + input[0][0] - self.grabbed_offset[0]
            self.height = self.size_offset[1] + input[0][1] - self.grabbed_offset[1]
        self.x = round(min(max(0, self.x), screen_size[0] - self.width))
        self.y = round(min(max(0, self.y), screen_size[1] - self.height))
        self.width = round(min(max(16, self.width), screen_size[0]))
        self.height = round(min(max(16, self.height), screen_size[1]))

        for widget in self.widgets:
            widget.update(input)

    def set_atlas(self, atlas):
        self.atlas = Spr.UIAtlas(atlas)

    def add_widget(self, widget):
        self.widgets.append(widget)

class Frame:
    def __init__():
        pass

class Widget:
    def __init__(self):
        pass

    def update(self, input):
        pass

    def render(self, surface):
        pass

class Button(Widget):
    def __init__(self, width, height, sprite: Spr.NineSlice):
        self.width = width
        self.height = height
        self.sprite = sprite

    def update(self, surface):
        pass

    def render(self, x, y, screen):
        self.sprite.draw(x, y, self.width, self.height, screen)