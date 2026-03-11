import pygame
import Spritehandlers as Spr
import Texthandlers as Txt
import Mousehandlers as Mou

class Widget:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.visible = True

    def set_visibile(self, visible):
        self.visible = visible

    def update(self, input, mouse):
        pass

    def render(self, surface):
        pass

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
        self.resize_grabbed_offset = (0, 0)
        self.size_offset = (0, 0)
        self.scroll_grabbed = False
        self.scroll_grabbed_offset = (0, 0)
        self.colors = [(0, 0, 0, 255), (255, 255, 255, 255), (255, 255, 255, 255)]
        self.outline = True
        self.atlas = Spr.UIAtlas(atlas)
        self.font = Txt.Font("uifont.png", 8, 8, ("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-*!.\uE00D "), 14)
        self.widgets = []
        self.surface = pygame.Surface((width,height))
        self.scroll_x = 0
        self.max_scroll_x = 0
        self.enable_scroll_x = False
        self.scroll_y = 0
        self.max_scroll_y = 0
        self.enable_scroll_y = False
        self.padding = 6
        self.last_input = []
        self.pressed_inputs = []
        self.Mouse = Mou.Mouse()

    def get_button_sprites(self):
        return [self.atlas.button_spr, self.atlas.button_high_spr, self.atlas.button_click_spr]

    def set_theme(self, colors, outline: bool = True):
        self.colors = colors
        self.outline = outline

    def render(self, surface: pygame.Surface):
        
        internal_x = self.x
        internal_y = self.y
        internal_w = self.width
        internal_h = self.height
        

        if not self.frameless:
            internal_y += 8
            internal_h -= 8
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
           #if Txt.txt_len(self.title) > self.width // 8 - 2:
           #    truncated_title = Txt.txt_trun(self.title, self.width // 8 - 2)
           #else:
           #   truncated_title = self.title
            truncated_title = self.title[:self.width // 8 - 2].strip()
            if len(truncated_title) < len(self.title):
                truncated_title += ":elipses:"
            self.font.draw(surface, truncated_title, internal_x + 2, self.y + 1, 1, self.colors[2], 0, 0)
        if (internal_w, internal_h) != self.surface.get_width():
            self.surface = pygame.Surface((internal_w - self.padding, internal_h - self.padding)) 
        self.surface.fill((255,255,255,255))
        self.surface.set_colorkey((255,255,255,255))
        for widget in self.widgets:
            if widget.visible and widget.x < internal_x + internal_w and widget.y < internal_y + internal_h:
                widget.render(self.surface)

        if self.enable_scroll_x:
            self.atlas.horizontal_scroll_spr.draw(self.x,self.y + self.height - 4, self.width, surface)
            surface.blit(self.atlas.scroll_button_spr.get_image(0), (self.x + (self.scroll_x / self.max_scroll_x) * self.width, self.y + self.height - 4))
            #self.atlas.scroll_button_spr.draw(self.x + (self.scroll_x / self.max_scroll_x) * self.width, self.y, surface)
        surface.blit(self.surface, (internal_x + self.padding // 2, internal_y + self.padding // 2))

    def find_mouse_pos(self, real_screen, game_screen, game_width, game_height, sub_screen_pos):
        mouse_x = (pygame.mouse.get_pos()[0] - (real_screen.get_width() - game_screen.get_size()[0]) / 2) * game_width / game_screen.get_size()[0]
        mouse_y = (pygame.mouse.get_pos()[1] - (real_screen.get_height() - game_screen.get_size()[1]) / 2) * game_height / game_screen.get_size()[1]
        mouse_x -= sub_screen_pos[0]
        mouse_y -= sub_screen_pos[1]
        return (mouse_x, mouse_y)
    #Input example:
    # [(mouse_x, mouse_y), (mouse_leftclick, mouse_midclick, mouse_rightclick)]
    def update(self, input, screen_size, surface: pygame.Surface, pos, game_screen):
        #mouse_x, mouse_y = input[0]
        #print(surface.get_rect())
        #mouse_x -= surface.get_rect().topleft[0]
        #mouse_y -= surface.get_rect().topleft[1]
        input[0] = self.find_mouse_pos(pygame.display.get_surface(), game_screen, 256, 240, pos)
        self.pressed_inputs = [False,False,False]
        if input != self.last_input:
            if input[1][0] == True and self.last_input[1][0] == False:
                self.pressed_inputs[0] = True
            if input[1][1] == True and self.last_input[1][1] == False:
                self.pressed_inputs[1] = True
            if input[1][2] == True and self.last_input[1][2] == False:
                self.pressed_inputs[2] = True
            self.last_input = input
        internal_x = self.x
        internal_y = self.y
        if not self.frameless:
            internal_y += 8
        if not input[1][0]:
            self.grabbed = False
            self.resize_grabbed = False
        if not self.grabbed and not self.resize_grabbed and not self.frameless  and input[0][0] > self.x and input[0][0] < self.x + self.width and input[0][1] > self.y and input[0][1] < self.y + 8:
            if self.pressed_inputs[0]:
                self.grabbed = True
                self.grabbed_offset = (input[0][0] - self.x,input[0][1] - self.y)
            else:
                self.Mouse.state = "GrabHover"
        if not self.resize_grabbed and not self.frameless  and input[0][0] > self.x + self.width - self.padding // 2 and input[0][0] < self.x + self.width and input[0][1] > self.y + self.height - self.padding // 2 and input[0][1] < self.y + self.height:
            if self.pressed_inputs[0]:
                self.resize_grabbed = True
                self.resize_grabbed_offset = (input[0][0], input[0][1])
                self.size_offset = (self.width, self.height)
            else:
                self.Mouse.state = "DMove"
        if self.grabbed:
            self.x = input[0][0] - self.grabbed_offset[0]
            self.y = input[0][1] - self.grabbed_offset[1]
            self.Mouse.state = "Grabbing"
        elif self.resize_grabbed:
            self.width = self.size_offset[0] + input[0][0] - self.resize_grabbed_offset[0]
            self.height = self.size_offset[1] + input[0][1] - self.resize_grabbed_offset[1]
            self.Mouse.state = "DMove"
        self.width = round(min(max(32, self.width), screen_size[0]))
        self.height = round(min(max(32, self.height), screen_size[1]))
        self.x = round(min(max(0, self.x), screen_size[0] - self.width))
        self.y = round(min(max(0, self.y), screen_size[1] - self.height))
        
        windowed_input = ((input[0][0] - internal_x - self.padding // 2, input[0][1] - internal_y - self.padding // 2), input[1])
        if input[0][0] > internal_x and input[0][0] < internal_x + self.width and input[0][1] > internal_y and input[0][1] < internal_y + self.height and not self.grabbed and not self.resize_grabbed:
            for widget in self.widgets:
                if widget.visible:
                    if widget.x + widget.width >= internal_x + self.width:
                        self.enable_scroll_x = True
                        self.max_scroll_x = widget.x + widget.width - self.width
                    if widget.y + widget.height >= internal_y + self.height:
                        self.enable_scroll_y = True
                        self.max_scroll_y = widget.y + widget.height - self.height
                widget.update(windowed_input, self.Mouse)

    def set_atlas(self, atlas):
        self.atlas = Spr.UIAtlas(atlas)

    def add_widget(self, widget: Widget):
        self.widgets.append(widget)

class Frame:
    def __init__():
        pass



class Button(Widget):
    def __init__(self, x, y, width, height, sprites: list):
        super().__init__(x, y, width, height)
        self.sprite = sprites[0]
        self.highlight_spr = sprites[1]
        self.click_spr = sprites[2]
        self.end_point = self.endpoint()
        self.state = "Norm"

    def update(self, input, mouse):
        mouse_x, mouse_y = input[0]
        if mouse_x <= self.end_point[0] and mouse_x >= self.x and mouse_y >= self.y and mouse_y <= self.end_point[1]:
            if input[1][0]:
                self.state = "Click"
                mouse.state = "Point"
            else:
                mouse.state = "Point"
                self.state = "Highlight"
        else:
            self.state = "Norm"

    def render(self, screen):
        if self.state == "Norm":
            self.sprite.draw(self.x, self.y, self.width, self.height, screen)
        elif self.state == "Highlight":
            self.highlight_spr.draw(self.x, self.y, self.width, self.height, screen)
        elif self.state == "Click":
            self.click_spr.draw(self.x, self.y, self.width, self.height, screen)
        
    def endpoint(self):
        return (self.x + self.width, self.y + self.height)

class Panel:
    def __init__():
        pass

class ScrollPanel:
    def __init__():
        pass

class Label:
    def __init__():
        pass

class TextBox:
    def __init__():
        pass

class Slider:
    def __init__():
        pass

class Checkbox:
    def __init__():
        pass

class RadioButtons:
    def __init__():
        pass

class Dropdown:
    def __init__():
        pass

class ProgressBar:
    def __init__():
        pass

class ColorPicker:
    def __init__():
        pass

class Image:
    def __init__():
        pass

class RotaryBoxes:
    def __init__():
        pass