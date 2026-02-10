import pygame
import json
import os


"""
    So, for some reason, this class is loaded before 
    Pygame starts in main.py, so uhh... Yeah, don't mind
    all this.
"""

os.environ['SDL_AUDIODRIVER'] = 'dsp'


pygame.init()

game_width, game_height = 256, 240

real_screen = pygame.display.set_mode((game_width * 2, game_height * 2), pygame.RESIZABLE)

game_screen = pygame.Surface((game_width, game_height))

"""
    Consistant Tile-based spritesheets, used for tilemaps, fonts, etc.
"""
class Spritesheet:

    '''
    Example Anim Data

    (
    # Frame 1 tiles list
    # Frame 2 tiles list, corresponding to frame 1
    # Frame n tiles list, corresponding to frame n-1
    )

    (
    [16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31],
    [32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47],
    [48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63]
    )

    '''

    def __init__(self, filename, frame_width, frame_height, anim_data=None):

        self.frame_width = frame_width
        self.frame_height = frame_height

        self.sheet = pygame.image.load(filename).convert_alpha()

        self.image_width = self.sheet.get_width()
        self.image_height = self.sheet.get_height()

        self.image_cols = self.image_width // self.frame_width
        self.image_rows = self.image_height // self.frame_height
        self.frame_count = self.image_cols * self.image_rows

        self.anim_data = anim_data

        self.extra_data = {}
        
        if os.path.exists(filename.split(".")[0] + ".json"):
            with open(filename.split(".")[0] + ".json", "r") as f:
                self.extra_data = json.load(f)

    def get_image(self, frame_num, anim_frame=0):
        frame_num %= self.frame_count
        if self.anim_data != None and frame_num in self.anim_data[0]:
            anim_frame %= len(self.anim_data[0])
            frame_num = self.anim_data[anim_frame][self.anim_data[anim_frame].index(frame_num)]
        image = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA).convert_alpha()
        x = frame_num % self.image_cols * self.frame_width 
        y = frame_num // self.image_cols * self.frame_height

        image.blit(self.sheet, (0, 0), (x , y, self.frame_width, self.frame_height))
        return image
    def get_image_xy(self, col, row, anim_frame=0):
        if self.anim_data != None and col + row * self.image_cols in self.anim_data[0]:
            anim_frame %= len(self.anim_data[0])
            frame_num = self.anim_data[anim_frame][self.anim_data[anim_frame].index(frame_num)]
        else:
            frame_num = col + row * self.image_cols
        x = frame_num % self.image_cols * self.frame_width
        y = frame_num // self.image_cols * self.frame_height
        image = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), (x, y, self.frame_width, self.frame_height))
        return image
    
    def get_extra_data(self, key):
        return self.extra_data.get(key, None)
    
"""
    More flexible spritesheet, for use with .xml files, intended for characters, enemies, etc. Not fully implemented yet.
"""
class AdvancedSpritesheet():

    def __init__(self, filename):
        self.image = None
        self.data = None
        if os.path.exists(filename):
            with open(filename, "r") as f:
                self.image = pygame.image.load(filename).convert_alpha()
        if os.path.exists(filename.split(".")[0] + ".xml"):
            with open(filename.split(".")[0] + ".xml", "r") as f:
                self.data = f.read()
                #print(self.data)

    def loadXML(self, xml):
        pass

class LayeredSprite:

    sprite_list = [{"sprite": None, "color": None, "layer": 0}]

    @staticmethod
    def sort_sprites(sprite):
        return sprite["layer"]
    
    def __init__(self, sprites):
        self.sprite_list = []
        for sprite in sprites:
            self.sprite_list.append(sprite)
        self.sprite_list.sort(key=LayeredSprite.sort_sprites)

    def set_color(self, layer, color):
        self.sprite_list[layer]["color"] = color

    def draw(self, x, y, screen):
        for sprite in self.sprite_list:
            if sprite["sprite"] != None:
                if sprite["color"] != None:
                    for xi in range(sprite["sprite"].get_width()):
                        for yi in range (sprite["sprite"].get_height()):
                            if sprite["sprite"].get_at((xi, yi)) != (0, 0, 0, 0):
                                sprite["sprite"].set_at((xi, yi), sprite["color"])
                screen.blit(sprite["sprite"], (x, y))