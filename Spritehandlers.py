import pygame
import json
import os
import re

import xml.etree.ElementTree as ET


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

    def __init__(self, filename: str, frame_width, frame_height, anim_data=None):

        self.frame_width = frame_width
        self.frame_height = frame_height
        if type(filename) == str:
            self.sheet = pygame.image.load(filename).convert_alpha()
        else:
            self.sheet = filename

        self.image_width = self.sheet.get_width()
        self.image_height = self.sheet.get_height()

        self.image_cols = self.image_width // self.frame_width
        self.image_rows = self.image_height // self.frame_height
        self.frame_count = self.image_cols * self.image_rows

        self.anim_data = anim_data

        self.extra_data = {}
        
        if type(filename) == str and os.path.exists(filename.split(".")[0] + ".json"):
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
    More flexible spritesheet, for use with .xml and .json files, intended for characters, enemies, etc.
"""
class AdvancedSpritesheet():

    def __init__(self, filename):
        self.image = None
        self.data = []
        self.animData = {}
        self.current_anim = None
        self.animStartFrame = 0
        self.height = 0
        self.width = 0
        if os.path.exists(filename):
            with open(filename, "r") as f:
                self.image = pygame.image.load(filename).convert_alpha()

        if os.path.exists(filename.split(".")[0] + ".xml"):
            self.loadXML(filename.split(".")[0] + ".xml")
        if os.path.exists(filename.split(".")[0] + ".xml2"):
            self.loadXML(filename.split(".")[0] + ".xml2")
        elif os.path.exists(filename.split(".")[0] + ".json"):
            self.loadJSON(filename.split(".")[0] + ".json")


    def loadXML(self, xml):
        image_data = ET.parse(xml)
        #print(image_data)
        root = image_data.getroot()
        for child in root:
            self.data.append(child.attrib)
        self.animData = self.getAnimData()

    def loadJSON(self, json_file):
        with open(json_file, "r") as f:
            json_data = json.load(f)

        frames = json_data["frames"]


        self.data = []
        for frame in frames:
            rect = frames[frame]["frame"]
            sourceSize = frames[frame]["sourceSize"]
            spriteSourceSize = frames[frame]["spriteSourceSize"]
            self.data.append({
                "x": rect["x"],
                "y": rect["y"],
                "width": rect["w"],
                "height": rect["h"],
                "frameX": -spriteSourceSize["x"],
                "frameY": -spriteSourceSize["y"],
                "frameWidth": sourceSize["w"],
                "frameHeight": sourceSize["h"],
                "name": "frame"
            })
        self.animData = {}
        for tag in json_data["meta"]["frameTags"]:
            name = tag["name"]
            start = tag["from"]
            end = tag["to"]

            self.animData[name] = list(range(start, end + 1))
    
    def getAnimData(self):
        animData = {}
        for _, i in enumerate(self.data):
            name = i["name"]
            split_name = re.split("^(\D*)", name)
            #print(split_name)
            if not split_name[1] in animData:
                animData[split_name[1]] = []
            animData[split_name[1]].append(_)
        return animData
            
    
    def get_image(self, index):
        cur_data = self.data[index]
        image = pygame.Surface((int(cur_data["frameWidth"]), int(cur_data["frameHeight"])), pygame.SRCALPHA).convert_alpha()
        image.blit(self.image, (0,0), (int(cur_data["x"]), int(cur_data["y"]), int(cur_data["width"]), int(cur_data["height"])))
        self.height = int(cur_data["frameHeight"]) + int(cur_data["frameY"])
        self.width = int(cur_data["frameWidth"]) + int(cur_data["frameX"])
        #image = pygame.transform.scale(image, (64, 64))
        offsets = [int(cur_data["frameX"]), int(cur_data["frameY"])]
        return image
        
    def animation(self, anim_name, frame, fps=12):
        if not anim_name in self.animData:
            return pygame.Surface((0,0))
        if anim_name != self.current_anim:
            self.current_anim = anim_name
            self.animStartFrame = frame

        cur_anim = self.animData[anim_name]
        local_frame = frame - self.animStartFrame
        #
        #frame %= 60
        index = int((local_frame / 60) * fps) % len(cur_anim)
        return self.get_image(cur_anim[index])
        
    def anim_offsets(self, anim_name, frame, fps=12):
        if not anim_name in self.animData:
            return [0, 0]
        if anim_name != self.current_anim:
            self.current_anim = anim_name
            self.animStartFrame = frame

        cur_anim = self.animData[anim_name]
        local_frame = frame - self.animStartFrame
        #
        #frame %= 60
        index = int((local_frame / 60) * fps) % len(cur_anim)
        return [self.data[cur_anim[index]]["frameX"], self.data[cur_anim[index]]["frameY"]]
    

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
                
class NineSlice:

    def __init__(self, image, tile_size):
        self.tile_size = tile_size
        self.sprite_list = {}
        self.sheet = image
        for i in range(self.sheet.get_width() // tile_size):
            for j in range(self.sheet.get_height() // tile_size):
                self.sprite_list[(i, j)] = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA).convert_alpha()
                self.sprite_list[(i, j)].blit(self.sheet, (0,0), (i * tile_size, j * tile_size, tile_size, tile_size))
        
    
    def __init__(self, filename, tile_size, image=None):
        self.tile_size = tile_size
        self.sprite_list = {}
        if image != None:
            self.sheet = image
        else:
            self.sheet = pygame.image.load("sprites/ui/nine_slice/" + filename).convert_alpha()
        #print(self.sheet.get_width())
        for i in range(self.sheet.get_width() // tile_size):
            for j in range(self.sheet.get_height() // tile_size):
                #print((i, j))
                self.sprite_list[(i, j)] = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA).convert_alpha()
                self.sprite_list[(i, j)].blit(self.sheet, (0,0), (i * tile_size, j * tile_size, tile_size, tile_size))

    def set_image(self, image, coordinate):
        self.sprite_list[coordinate] = image

    def draw(self, x, y, width, height, screen):
        tile_width = max(1, width // self.tile_size - 1)
        tile_height = max(1, height // self.tile_size - 1)
        for i in range(tile_height):
            for j in range(tile_width):
                #if i != 0 and j != 0 and i != tile_height and j != tile_width:
                if i == tile_height - 1 and j == tile_width - 1:
                    screen.blit(self.sprite_list[(1,1)], (x + (j + 1) * self.tile_size - 1, y + (i + 1) * self.tile_size - 1))
                else:
                    screen.blit(self.sprite_list[(1,1)], (x + (j + 1) * self.tile_size, y + (i + 1) * self.tile_size))

                if i == 0:
                    if j != tile_width - 1:
                        screen.blit(self.sprite_list[(1,0)], (x + (j + 1) * self.tile_size, y))
                    else:
                        screen.blit(self.sprite_list[(1,0)], (x + (j + 1) * self.tile_size - 1, y))
                if i == tile_height - 1:
                    if j != tile_width - 1:
                        screen.blit(self.sprite_list[(1,2)], (x + (j + 1) * self.tile_size, y + height - self.tile_size))
                    else:
                        screen.blit(self.sprite_list[(1,2)], (x + (j + 1) * self.tile_size - 1, y + height - self.tile_size))
            if i != tile_height:
                screen.blit(self.sprite_list[(0,1)], (x, y + (i + 1) * self.tile_size - 1))
                screen.blit(self.sprite_list[(2,1)], (x + width - self.tile_size, y + (i + 1) * self.tile_size - 1))
            
        
        screen.blit(self.sprite_list[(0,0)], (x, y))
        screen.blit(self.sprite_list[(2,0)], (x + width - self.tile_size, y))
        screen.blit(self.sprite_list[(0,2)], (x, y + height - self.tile_size))
        screen.blit(self.sprite_list[(2,2)], (x + width - self.tile_size, y + height - self.tile_size))

class ThreeSlice:
    def __init__(self, image, tilesize: int, vertical: bool):
        self.sprite_list = {}
        self.vertical = vertical
        self.tilesize = tilesize
        if vertical:
            for i in range(image.get_height() // tilesize):
                self.sprite_list[i] = pygame.Surface((tilesize, tilesize), pygame.SRCALPHA).convert_alpha()
                self.sprite_list[i].blit(image, (0,0), (0, i * tilesize, tilesize, tilesize))
        else:
            for i in range(image.get_width() // tilesize):
                self.sprite_list[i] = pygame.Surface((tilesize, tilesize), pygame.SRCALPHA).convert_alpha()
                self.sprite_list[i].blit(image, (0,0), (i * tilesize, 0, tilesize, tilesize))

    def draw(self, x, y, length, screen):
        
        if self.vertical:
            for i in range(length // self.tilesize):
                screen.blit(self.sprite_list[1], (x, y + i * self.tilesize))
            screen.blit(self.sprite_list[2], (x, y + i * self.tilesize))
        else:
            for i in range(length // self.tilesize):
                screen.blit(self.sprite_list[1], (x + i * self.tilesize, y))
            screen.blit(self.sprite_list[2], (x + i * self.tilesize, y))
        screen.blit(self.sprite_list[0], (x, y))

class UIAtlas:
    def __init__(self, filename):
        self.atlas = pygame.image.load("sprites/ui/gui/" + filename).convert_alpha()
        self.window_spr = NineSlice(None, 8, self.atlas.subsurface(0,8, 24, 24))
        self.windowed_spr = NineSlice(None, 8, self.atlas.subsurface(0,8, 24, 24))
        self.windowed_spr.set_image(self.atlas.subsurface(0,0, 8, 8), (0,0))
        self.windowed_spr.set_image(self.atlas.subsurface(8,0, 8, 8), (1,0))
        self.windowed_spr.set_image(self.atlas.subsurface(16,0, 8, 8), (2,0))

        self.button_spr = NineSlice(None, 4, self.atlas.subsurface(24,16,12,12))
        self.button_high_spr = NineSlice(None, 4, self.atlas.subsurface(48,16,12,12))
        self.button_click_spr = NineSlice(None, 4, self.atlas.subsurface(36,16,12,12))

        self.horizontal_scroll_spr = ThreeSlice(self.atlas.subsurface(52,28, 12, 4), 4, False)
        #self.vertical_scroll_spr = ThreeSlice(self.atlas.subsurface(8,32, 8, 8), 8, True)

        self.scroll_button_spr = Spritesheet(self.atlas.subsurface(48, 28, 4, 4), 4, 4)

    def draw_window(self, x, y, width, height, screen, frameless=False):
        if frameless:
            self.window_spr.draw(x, y, width, height, screen)
        else:
            self.windowed_spr.draw(x, y, width, height, screen)