import pygame

import json
import os

import math
import random

import copy
pygame.init()

game_width, game_height = 256, 240

real_screen = pygame.display.set_mode((game_width * 2, game_height * 2), pygame.RESIZABLE)

game_screen = pygame.Surface((game_width, game_height))

mini_snake_screen = pygame.Surface((32,32))

pygame.display.set_caption("PythonRPG")


'''
Wow, 800+ lines in and I'm writing this just after finishing part 1.
=================================================
|                                               |
|                   ENGINE                      |
|                                               |
|       Map, Font, Sprite Handlers, Etc.        |
|                                               |
|                                               |
=================================================
'''
class Font:
    characters = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        ".!?,:;'\"-_"
        "0123456789"
        "[]/\\"
        "\uE000\uE001\uE002\uE004\uE003\uE005\uE006\uE008\uE007\uE009\uE00A\uE00B"
        " \uE00C"

    )

    PUA = {
        ":radioselected:": "\uE000",
        ":radiobutton:": "\uE001",
        ":heart:": "\uE002",
        ":emptyheart:": "\uE003",
        ":star:": "\uE004",
        ":left:": "\uE005",
        ":right:": "\uE006",
        ":up:": "\uE007",
        ":down:": "\uE008",
        ":emptybox:": "\uE009",
        ":checkbox:": "\uE00A",
        ":spark:": "\uE00B",
    }

    COLORS = {
        ":cRed:": (255,0,0),
        ":cGreen:": (0,255,0),
        ":cBlue:": (0,0,255),
        ":cMagenta:": (255,0,255),
        ":cCyan:": (0,255,255),
        ":cYellow:": (255,255,0),
        ":cWhite:": (255,255,255),
    }
    def __init__(self, image_path, char_w, char_h, chars, cols):
        self.sheet = pygame.image.load("sprites/ui/font/" + image_path).convert_alpha()
        self.char_w = char_w
        self.char_h = char_h
        self.cols = cols
        self.glyphs = {}
        self.color_changes = []

        for i, char_i in enumerate(chars):
            x = i % cols * char_w
            y = i // cols * char_h
            character_image = pygame.Surface((char_w, char_h), pygame.SRCALPHA).convert_alpha()
            character_image.blit(self.sheet, (0, 0), (x, y, char_w, char_h))
            self.glyphs[char_i] = character_image

        self.fallback = self.glyphs.get("?", pygame.Surface((char_w, char_h), pygame.SRCALPHA))

    def create_colored_glyph(self, char, color):
        base = self.glyphs.get(char, self.fallback)
        image = base.copy()
        for xi in range(image.get_width()):
            for yi in range (image.get_height()):
                if image.get_at((xi, yi)) != (0, 0, 0, 0):
                    image.set_at((xi, yi), (color[0], color[1], color[2], round(abs(max(min(image.get_at((xi, yi))[3] * color[3], 255), 0)))))
        return image

    def draw(self, surface, text, x, y, scale=1, color=(255, 255, 255, 255), spacing=-1, linespacing=8):
        self.sheet = pygame.image.load("sprites/ui/font/font.png").convert_alpha()
        cx, cy = x, y
        altered_text = Font.emoji(text)
        altered_text = self.color(altered_text, color[3])
        cur_color = color
        i = 0
        for char in altered_text:
            #print(self.color_changes)
            if len(self.color_changes) != 0 and self.color_changes[0]["index"] == i:
                cur_color = self.color_changes[0]["color"]
                self.color_changes.pop(0)
            if char == "\n":
                cx = x
                cy += (self.ch + linespacing) * scale
                continue
            base = self.glyphs.get(char, self.fallback)
            image = base

            image.set_alpha(color[3])
            if cur_color != (255, 255, 255, 255):
                image = self.create_colored_glyph(char, cur_color)
            if scale == 1:
                surface.blit(image, (cx, cy))
            else:
                surface.blit(pygame.transform.scale(image, (self.char_w * scale, self.char_h * scale)), (cx, cy))
            cx += (self.char_w + spacing) * scale 
            i += 1
    
    def emoji(text):
        for emote, char in Font.PUA.items():
            text = text.replace(emote, char)
        return text
    def color(self, text, opacity):
        for color, rgb in Font.COLORS.items():
            #print(Font.COLORS[color])
            index = text.find(color)
            if index != -1:
                self.color_changes.append({"color": (rgb[0], rgb[1], rgb[2], opacity), "index": index})
                #self.color_changes[len(self.color_changes)] = {"color": (rgb[0], rgb[1], rgb[2], opacity), "index": index}
            text = text.replace(color, "\uE00C")
        #if len(self.color_changes) > 0:
            #sorted(self.color_changes.items(), key=lambda item: item[1])
            #print(self.color_changes)
            #self.color_changes.sort(key="index")
        return text
    
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

    def draw(self, x, y):
        for sprite in self.sprite_list:
            if sprite["sprite"] != None:
                if sprite["color"] != None:
                    for xi in range(sprite["sprite"].get_width()):
                        for yi in range (sprite["sprite"].get_height()):
                            if sprite["sprite"].get_at((xi, yi)) != (0, 0, 0, 0):
                                sprite["sprite"].set_at((xi, yi), sprite["color"])
                game_screen.blit(sprite["sprite"], (x, y))

class Debug:
    debug_messages = True
    map_editor = True
    map_tile = 0
    debug_message_fade = 60
    editorMapMode = "Visual"

    font = None

    debug_messages_list = [{"text": "", "time": 0, "time_limit": 0}]
    

    @staticmethod
    def __init__():
        Debug.font = Font("font.png", 8, 8, Font.characters, 8)

    def debug_print(text, time=debug_message_fade):
        time = max(1, time)
        if Debug.debug_messages:
            #print(text + " (" + str(time) + ")")
            Debug.debug_messages_list.append({"text": text, "time": 0, "time_limit": time})

    def render_debug_text():
        #print(Debug.debug_messages_list)
        if len(Debug.debug_messages_list) == 0 or Debug.font == None:
            return
        for i in range(len(Debug.debug_messages_list)):
            
            Debug.debug_messages_list[i]["time"] += 1
            Debug.debug_messages_list[i]["time_limit"] = max(1, Debug.debug_messages_list[i]["time_limit"])
            Debug.font.draw(game_screen, ":right:" + Debug.debug_messages_list[i]["text"], 0, i * 16, 1, (255, 255, 255, 255 - (Debug.debug_messages_list[i]["time"] / Debug.debug_messages_list[i]["time_limit"]) * 255))
            
        for i in range(len(Debug.debug_messages_list) - 1, -1, -1):
            if Debug.debug_messages_list[i]["time"] > Debug.debug_messages_list[i]["time_limit"]:
                del Debug.debug_messages_list[i]
                break
debug = Debug()

class Map:

    '''
    Map Save Shorthand

    _ prefix means temporary file. Will be deleted on program close.
    ! prefix means it is used as a debug map.
    # prefix means it is used as a playable map.

    Map Tile Shorthand:
      0 = grass (Normal movement)
      1 = water (Harder to walk on, but can swim)
      2 = lava (Cannot walk on)
      3 = cover (Easier to walk on)
      4 = rough (harder to walk on)
      5 = wall (Wall.)

    '''

    tiles = {
        0: {"name": "grass", "move": 1, "block": False},
        1: {"name": "water", "move": 1, "swim": 1, "block": True},
        2: {"name": "lava", "move": 1.5, "block": True},
        3: {"name": "cover", "move": 0.75, "block": False},
        4: {"name": "rough", "move": 2, "block": False},
        5: {"name": "wall", "move": 0, "block": True},
    }
    
    dualTileFormat = {
        (1,1,0,1): 0,
        (1,0,1,0): 1,
        (0,1,0,0): 2,
        (1,1,0,0): 3,
        (0,1,1,0): 4,
        (1,0,0,0): 5,
        (0,0,0,0): 6,
        (0,0,0,1): 7,
        (1,0,1,1): 8,
        (0,0,1,1): 9,
        (0,0,1,0): 10,
        (0,1,0,1): 11,
        (1,1,1,1): 12,
        (1,1,1,0): 13,
        (1,0,0,1): 14,
        (0,1,1,1): 15
    }
    defaultDualTilemap = Spritesheet("sprites/tilesets/testtiles2.png", 16, 16)


    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = [-1] * (self.width * self.height)
        #self.dualLogMapA = [[random.randint(0,8) for _ in range(self.width + 1)] for _ in range(self.height + 1)]
        self.dualLogMapA = [[0 for _ in range(self.width + 1)] for _ in range(self.height + 1)]
        self.dualVisMapA = [[0 for _ in range(self.width + 1)] for _ in range(self.height + 1)]
        
        self.showVisTiles = True
        
        self.cur_total_tiles = 0
        self.cur_tile_indices = []
        
        self.bg_color = (0,0,0)

    def idx(self, x, y, tilemap_type="Logic"):
        if tilemap_type == "Logic":
            if x < 0 or y < 0 or x >= self.width or y >= self.height:
                return None
            return x + y * self.width
        elif tilemap_type == "Visual":
            if x < -1 or y < -1 or x >= len(self.dualLogMapA[0]) or y >= len(self.dualLogMapA):
                return None
            return (x, y)
    
    def get(self, x, y, default=-1):
        if self.idx(x, y) == None:
            return default
        return self.map[self.idx(x, y)]
    
    def set(self, x, y, value, tilemap_type="Logic"):
        if self.idx(x,y,tilemap_type) == None:
            return False
        if tilemap_type == "Logic":
            self.map[self.idx(x, y)] = value
            return True
        elif tilemap_type == "Visual":
            self.dualLogMapA[y][x] = value

    def dualVismapUpdate(self, anim_frame, tileset, bounds=(0, 0, 0, 0)):
        autotiles_info = tileset.get_extra_data("autotiles")
        if autotiles_info != None:
            autotiles_info.sort(key=lambda x: x["id"])
        for y in range(len(self.dualLogMapA)):
            for x in range(len(self.dualLogMapA[0])):
                if not (bounds[0] <= x < bounds[1] and bounds[2] <= y < bounds[3]):
                    continue
                
                if x == -1 or y == -1:
                    grid1 = 0
                else:
                    grid1 = self.dualLogMapA[y-1][x-1]

                if x == len(self.dualLogMapA[0]) or y == -1:
                    grid2 = 0
                else:
                    grid2 = self.dualLogMapA[y-1][x]

                if x == -1 or y == len(self.dualLogMapA):
                    grid3 = 0
                else:
                    grid3 = self.dualLogMapA[y][x-1]

                if x == len(self.dualLogMapA[0]) or y == len(self.dualLogMapA):
                    grid4 = 0
                else:
                    grid4 = self.dualLogMapA[y][x]
                
                tileGrid = (grid1,grid2,grid3,grid4)

                
                self.cur_tile_indices = []
                self.dualVisMapA[y][x] = {}
                if autotiles_info != None:
                    self.cur_total_tiles = len(autotiles_info)
                    #print(autotiles_info)
                    for i in range(len(autotiles_info)):
                
                        mask = (
                            1 if i == grid1 else 0,
                            1 if i == grid2 else 0,
                            1 if i == grid3 else 0,
                            1 if i == grid4 else 0
                        )
                        if grid1 == 0 or grid2 == 0 or grid3 == 0 or grid4 == 0:
                            self.dualVisMapA[y][x][-1] = autotiles_info[i]["bg-tile"]
                        
                        if autotiles_info[i]["type"] == "autotile":
                            shape = self.dualTileFormat.get(mask, 0)
                            if shape != 6:
                                tile_index = shape + autotiles_info[i]["start-tile"] 
                            else:
                                tile_index = -1
                            self.cur_tile_indices.append(autotiles_info[i]["start-tile"] + 6)

                        elif autotiles_info[i]["type"] == "single" :
                            if mask != (0,0,0,0):
                                tile_index = autotiles_info[i]["start-tile"]
                            else:
                                tile_index = -1
                            #print(autotiles_info[i]["start-tile"])
                            self.cur_tile_indices.append(autotiles_info[i]["start-tile"])
                        else:
                            tile_index = -1
                            
                        if "anim-offset" in autotiles_info[i] and "anim-time" in autotiles_info[i] and tile_index != -1:
                            if round(anim_frame / autotiles_info[i]["anim-time"]) % 2 == 0:
                                tile_index += autotiles_info[i]["anim-offset"]
                            
                        if tile_index != -1:
                            self.dualVisMapA[y][x][i] = tile_index
                        
                        
                else:
                    mask = (grid1, grid2, grid3, grid4)
                    tile_index = self.dualTileFormat.get(mask, 6)
                    self.dualVisMapA[y][x][0] = tile_index
                #print(self.dualVisMapA[y][x])

    def render(self, surface, tileset, cam_x, cam_y, anim_frame=0, tile_size=16):
        
        
        start_x = max(-1, (cam_x - tile_size) // tile_size)
        end_x = min(self.width, (cam_x + game_width + tile_size) // tile_size)

        start_y = max(-1, (cam_y - tile_size) // tile_size)
        end_y = min(self.height, (cam_y + game_height + tile_size) // tile_size)

        self.dualVismapUpdate(anim_frame, tileset, (start_x, end_x, start_y, end_y)) 

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                    if self.showVisTiles:
                        #if x == max(0,min(x, self.width)) and y == max(0, min(y, self.height)):
                        if x < self.width and y < self.height:
                            tiles = self.dualVisMapA[y + 1][x + 1]
                        #print(tiles)
                        if tiles != 0 and tiles != None:
                            for i in tiles:
                                #print(str(tileset.get_image(i, anim_frame)))
                                #print(tiles)
                                surface.blit(tileset.get_image(tiles[i], anim_frame), (tile_size/2 + x * tile_size - cam_x,tile_size/2 + y * tile_size - cam_y))
                    else:   
                        if x == max(0, min(x, self.width)) and y == max(0, min(y, self.height)):
                            tile = self.get(x, y)
                            if tile != -1:
                                surface.blit(tileset.get_image(tile, anim_frame), (x * tile_size - cam_x, y * tile_size - cam_y))

    def render_overlay(self, surface):
        pass
    
    def rle_encode_row(row):
        encoded = []
        last = row[0]
        count = 1

        for tile in row[1:]:
            if tile == last:
                count += 1
            else:
                encoded.append([last, count])
                last = tile
                count = 1

        encoded.append([last, count])
        return encoded

    def rle_encode_map(flat_map, width, height):
        rows = []
        for y in range(height):
            start = y * width
            end = start + width
            row = flat_map[start:end]
            rows.append(Map.rle_encode_row(row))
        return rows

    def rle_decode_row(encoded_row):
        row = []
        for tile, count in encoded_row:
            row.extend([tile] * count)
        return row
    
    def rle_decode_map(rows, width, height):
        flat_map = []
        for encoded_row in rows:
            row = Map.rle_decode_row(encoded_row)
            #print(row)
            if len(row) != width:
                raise ValueError("Decoded row has wrong width")
            flat_map.extend(row)

        if len(flat_map) != width * height:
            raise ValueError("Decoded map has wrong size")

        return flat_map
    
    def rle_encode_tilemap(map):
        encoded_map = []
        for row in map:
            encoded_map.append(Map.rle_encode_row(row))
        return encoded_map
    
    def rle_decode_tilemap(encoded_map):
        decoded_map = []
        for encoded_row in encoded_map:
            decoded_map.append(Map.rle_decode_row(encoded_row))
        return decoded_map


    def to_list(self, name):
        return {
            "version": 3,
            "name": name,
            "width": self.width,
            "height": self.height,
            "map": Map.rle_encode_map(self.map, self.width, self.height),
            "tilemap": "",
            "tilemap_tiles": Map.rle_encode_tilemap(self.dualLogMapA),
            "bg-color": self.bg_color,
            "units": [],
            "objects": [],
        }
    
    def from_list(self, data):
        self.width = data["width"]
        self.height = data["height"]
        if data["version"] == 1:
            self.map = data["map"]
        elif data["version"] == 2:
            self.map = Map.rle_decode_map(
                data["map"],
                self.width,
                self.height
            )
        elif data["version"] == 3:
            self.map = Map.rle_decode_map(
                data["map"],
                self.width,
                self.height
            )
            self.dualLogMapA = Map.rle_decode_tilemap(data["tilemap_tiles"])
            self.bg_color = data["bg-color"]
        

    
    @staticmethod
    def map_from_list(data):
        map = Map(data["width"], data["height"])
        map.from_list(data)
        return map
    
    @staticmethod
    def map_to_list(map):
        return map.to_list()
    
    def save(self, filename, internalName=""):
        with open("maps/" + filename + ".json", "w") as f:
            json.dump(self.to_list(internalName), f, indent=4)
            Debug.debug_print(":checkbox: Saved map " + filename + ".json", 200)

    @staticmethod
    def load(filename):
        if not os.path.exists("maps/" + filename + ".json"):
            Debug.debug_print(":cRed::emptybox::cWhite: Failed to load map " + filename + ".json", 200)
            filename = "!default_test_map"
        with open("maps/" + filename + ".json", "r") as f:
            loadedMap = json.load(f)
            Debug.debug_print(":checkbox: Loaded map " + loadedMap["name"], 200)
            
            if len(Map.map_from_list(loadedMap).map) != loadedMap["width"] * loadedMap["height"]:
                Debug.debug_print(":cRed::emptybox::cWhite: Map has invalid dimensions or missing tiles", 2000)

            return Map.map_from_list(loadedMap)
        
    @staticmethod
    def unload_temp():
        for f in os.listdir("maps/"):
            if f.startswith("_"):
                os.remove("maps/" + f)
                




'''
Phase 2, initiated.
=================================================
|                                               |
|                  GAMEPLAY                     |
|                                               |
|      Characters, Players, Enemies, etc.       |
|                                               |
|                                               |
=================================================
'''

class AStar:
    @staticmethod
    def Pathfind(startCoordinates, end, tiles, move_type="8-dir"):
        openList = []
        closedList = []
        
        openList.append({"x": startCoordinates[0], "y": startCoordinates[1], "f": 0, "g": 0, "h":0, "p": None})
        
        W = tiles.width
        H = tiles.height

        def in_bounds(x, y):
            return 0 <= x < W and 0 <= y < H
        
        def is_blocked(x, y):
            return tiles.get(x, y) == 5
        
        def heuristic(x, y):
            if move_type == "4-dir":
                return abs(x - end[0]) + abs(y - end[1])
            else:
                return math.sqrt(abs(x - end[0])**2 + abs(y - end[1])**2)
            
        def neighbors(x, y):
            out = []
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    if move_type == "4-dir" and dx != 0 and dy != 0:
                        continue
                    out.append((x + dx, y + dy, dx, dy))
            return out
        
        while openList:
            #print(sorted(openList, key=lambda x: x["f"]))
            openList = sorted(openList, key=lambda x: x["f"])
            curNode = openList.pop(0)
            curKey = (curNode["x"], curNode["y"])
    
            if curKey in closedList:
                continue
            closedList.append(curKey)

            if curKey == end:
                path = []
                n = curNode
                while n is not None:
                    path.append((n["x"], n["y"]))
                    n = n["p"]
                path.reverse()
                return path

            for nx, ny, dx, dy in neighbors(curNode["x"], curNode["y"]):
                if not in_bounds(nx, ny) or is_blocked(nx, ny):
                    continue
                step_cost = 1
                g_cost = curNode["g"] + step_cost
                h_cost = heuristic(nx, ny)
                f_cost = g_cost + h_cost

                worse = False
                for node in openList:
                    if node["x"] == nx and node["y"] == ny and g_cost >= node["g"]:
                        worse = True
                        break
                if worse:
                    continue

                openList.append({"x": nx, "y": ny, "f": f_cost, "g": g_cost, "h": h_cost, "p": curNode})
            
                
        return None
        #print(closedList)
                        

class Character:
    
    def __init__(self, pos=(0,0), sheet=Spritesheet("sprites/characters/placeholderNew.png", 16,16)):
        self.x = pos[0]
        self.y = pos[1]
        self.sheet = sheet
        


'''
snek
=================================================
|                                               |
|                   ARCADE                      |
|                                               |
|       Snek                                    |
|                                               |
|                                               |
=================================================
'''

class Snake:
    snakeBody = []
    validLocations = []

    snakeColors = [
        [(0,90,0), (50,200,50), (255,0,0), (255,255,255), (0,0,0)],
        [(95,123,118), (135,157,163), (95,123,118), (135,157,163), (50,57,70)],
    ]

    font = Font("arcadefont.png", 3,4, "1234567890", 5)

    def __init__(self):
        self.snakeBody = []
        for i in range(32 * 32):
            self.validLocations.append(i)
        self.snakeBodyLength = 5
        self.snakeHead = (16, 16)
        self.apple = (random.randint(0,31), random.randint(0,31))
        self.dir = -1
        self.curDir = -1
        self.started = False
        self.textFade = 0

    def reset(self):
        self.snakeBody = []
        self.snakeBodyLength = 5
        self.snakeHead = (16, 16)
        self.apple = (random.randint(0,31), random.randint(0,31))
        self.dir = -1
        self.curDir = -1
        self.started = False

    def update(self, frame, input):

        if input[0] and self.curDir != 3:
            self.started = True
            self.dir = 1
        elif input[1] and self.curDir != 0:
            self.started = True
            self.dir = 2
        elif input[2] and self.curDir != 1:
            self.started = True
            self.dir = 3
        elif input[3] and self.curDir != 2:
            self.started = True
            self.dir = 0

        if frame % 5 != 0 or not self.started:
            return

        self.curDir = self.dir

        self.snakeBody.append(self.snakeHead)
        if len(self.snakeBody) > self.snakeBodyLength:
            self.snakeBody.pop(0)

        if self.dir == 0:
            self.snakeHead = (self.snakeHead[0] + 1, self.snakeHead[1])
        elif self.dir == 1:
            self.snakeHead = (self.snakeHead[0], self.snakeHead[1] - 1)
        elif self.dir == 2:
            self.snakeHead = (self.snakeHead[0] - 1, self.snakeHead[1])
        elif self.dir == 3:
            self.snakeHead = (self.snakeHead[0], self.snakeHead[1] + 1)

        for body in self.snakeBody:
            if self.snakeHead == body:
                self.reset()

        if self.snakeHead[0] < 0:
            self.snakeHead = (31, self.snakeHead[1])
            self.reset()
        elif self.snakeHead[0] > 31:
            self.snakeHead = (0, self.snakeHead[1])
            self.reset()
        elif self.snakeHead[1] < 0:
            self.snakeHead = (self.snakeHead[0], 31) 
            self.reset()
        elif self.snakeHead[1] > 31:
            self.snakeHead = (self.snakeHead[0], 0)
            self.reset()

        if self.snakeHead == self.apple:
            for i in range(32 * 32):
                self.validLocations.append(i)
            for body in self.snakeBody:
                self.validLocations.pop(body[0] + body[1] * 32)
            appleLocation = random.choice(self.validLocations)
            self.apple = (appleLocation % 32, appleLocation // 32)
            self.snakeBodyLength = self.snakeBodyLength + 1
            self.textFade = 60
            
        

    def draw(self, screen):
        color_index = 1
        color1 = self.snakeColors[color_index][0]
        color2 = self.snakeColors[color_index][1]
        applecolor = self.snakeColors[color_index][2]
        text_color = self.snakeColors[color_index][3]
        screen.fill(self.snakeColors[color_index][4])

        if self.textFade > 0:
            self.font.draw(screen, str(self.snakeBodyLength - 5), 1, 1, 1, (text_color[0],text_color[1],text_color[2],255 * (self.textFade / 60)), 1)
            self.textFade -= 1

        pygame.draw.rect(screen, color1, (self.snakeHead[0], self.snakeHead[1], 1, 1))
        for i, body in enumerate(self.snakeBody):
            pygame.draw.rect(screen, (color2[0] - (color2[0] - color1[0]) * (i / len(self.snakeBody)), color2[1] - (color2[1] - color1[1]) * (i / len(self.snakeBody)), color2[2] - (color2[2] - color1[2]) * (i / len(self.snakeBody))), (body[0], body[1], 1, 1))
        pygame.draw.rect(screen, applecolor, (self.apple[0], self.apple[1], 1, 1))





clock = pygame.time.Clock()

#spr_selected_tile = pygame.image.load('selectedtile.png').convert_alpha()

sprsh_tileset = Spritesheet('sprites/tilesets/testtiles2.png', 16, 16)

markers_full = Spritesheet('markers.png', 16, 32)
markers_icons = Spritesheet('markers.png', 16, 16)
marker = LayeredSprite([{"sprite": markers_full.get_image(0), "layer": 0, "color": None}, {"sprite":markers_full.get_image(1), "layer": 1, "color": (255,0,0,255)}, {"sprite":markers_icons.get_image(2), "layer": 2, "color": None}])

camera_x, camera_y = 0, 0
cam_speed = 1
map_width, map_height = 3000, 12

cur_map = Map(map_width, map_height)

frame = 0

cur_map = Map.load("ai_testing/!dungeon")

cabinet = pygame.image.load("sprites/arcades/snake_cabinet.png").convert_alpha()
cabinet_curPos = (0,256)
cabinet_pos = (0,256)

snek = Snake()

last_few_maps = []

path = None

while True:
    pygame.display.set_icon(mini_snake_screen)
    cabinet_curPos = (cabinet_curPos[0] + (cabinet_pos[0] - cabinet_curPos[0]) * 0.1, cabinet_curPos[1] + (cabinet_pos[1] - cabinet_curPos[1]) * 0.1)


    marker.draw(5,5)

    frame += 1

    scaled_screen = pygame.transform.scale(game_screen, real_screen.get_size())
    if real_screen.get_width() > real_screen.get_height():
        scaled_screen = pygame.transform.scale(game_screen, (real_screen.get_height(), real_screen.get_height()))
        scaled_snake = pygame.transform.scale(mini_snake_screen, (real_screen.get_height() // 2, real_screen.get_height() // 2))
    else:
        scaled_screen = pygame.transform.scale(game_screen, (real_screen.get_width(), real_screen.get_width()))
        scaled_snake = pygame.transform.scale(mini_snake_screen, (real_screen.get_width() // 2, real_screen.get_width() // 2))

    mouse_x = (pygame.mouse.get_pos()[0] - (real_screen.get_width() - scaled_screen.get_size()[0]) / 2) * game_width / scaled_screen.get_size()[0] 
    mouse_y = (pygame.mouse.get_pos()[1] - (real_screen.get_height() - scaled_screen.get_size()[1]) / 2) * game_height / scaled_screen.get_size()[1]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Map.unload_temp()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Map.unload_temp()
                exit()
            if Debug.map_editor:
                if event.key == pygame.K_0:
                    Debug.editorMapMode = "Logic"
                    cur_map.showVisMap = False

                elif event.key == pygame.K_1:
                    Debug.editorMapMode = "Visual"
                    cur_map.showVisMap = True

                elif event.key == pygame.K_2:
                    Debug.map_tile += 1
                    if Debug.editorMapMode == "Logic":
                        Debug.map_tile %= len(Map.tiles)
                        Debug.debug_print("Set tile to [" + Map.tiles[Debug.map_tile]["name"] + "]")
                    elif Debug.editorMapMode == "Visual":
                        Debug.map_tile %= cur_map.cur_total_tiles
                    
                elif event.key == pygame.K_3:
                    path = AStar.Pathfind((1,1), ((mouse_x + camera_x) // 16, (mouse_y + camera_y) // 16), cur_map)
                    
                    
                elif event.key == pygame.K_4:
                    Debug.map_tile = 4
                    Debug.debug_print("Set tile to [" + Map.tiles[4]["name"] + "]")
                elif event.key == pygame.K_5:
                    Debug.map_tile = 5
                    Debug.debug_print("Set tile to [" + Map.tiles[5]["name"] + "]")
                elif event.key == pygame.K_r:
                    cur_map.save("_temp_save", "Local Save")
                elif event.key == pygame.K_f:
                    if cabinet_pos == (0, 0):
                        cabinet_pos = (0, 256)
                    else:
                        cabinet_pos = (0, 0)
                elif event.key == pygame.K_y:
                    cur_map.showVisTiles = not cur_map.showVisTiles
                    if Debug.editorMapMode == "Logic":
                        Debug.editorMapMode = "Visual"
                    elif Debug.editorMapMode == "Visual":
                        Debug.editorMapMode = "Logic"
                    if cur_map.showVisTiles:
                        sprsh_tileset = Spritesheet('sprites/tilesets/testtiles2.png', 16, 16)
                    else:
                        sprsh_tileset = Spritesheet('sprites/tilesets/bgtiles.png', 16, 16)

                elif event.key == pygame.K_KP_6:
                    last_few_maps.append(copy.deepcopy(cur_map))
                    cur_map.dualLogMapA = [[random.randint(0,2) for _ in range(cur_map.width + 1)] for _ in range(cur_map.height + 1)] 
                elif event.key == pygame.K_KP_9:
                    #print(last_few_maps)
                    if len(last_few_maps) > 0:
                        cur_map = last_few_maps.pop()
        if event.type == pygame.MOUSEWHEEL:
            if Debug.map_editor:
                Debug.map_tile += event.y
                #Debug.map_tile %= len(Map.tiles)
                #Debug.debug_print("Set tile to [" + Map.tiles[Debug.map_tile]["name"] + "]")
        if event.type == pygame.VIDEORESIZE:
            real_screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

         
        if Debug.editorMapMode == "Visual":
            if cur_map.cur_total_tiles != 0:
                Debug.map_tile %= cur_map.cur_total_tiles
        elif Debug.editorMapMode == "Logic":
            if len(Map.tiles) != 0:
                Debug.map_tile %= len(Map.tiles)

    #game_screen.fill((255, 0, 255))
    game_screen.fill(cur_map.bg_color)
    
    
    cur_map.render(game_screen, sprsh_tileset, camera_x, camera_y, frame)
    
    #game_screen.blit(spr_selected_tile, spr_selected_tile.get_rect(center=(round((mouse_x - 8) / 16) * 16 + 8, round((mouse_y - 8) / 16) * 16 + 8)))
    
    if Debug.map_editor:
        if pygame.mouse.get_pressed()[0]:
            #print(cur_map.dualLogMapA)
            cur_map.set(round((mouse_x + camera_x) // 16), round((mouse_y + camera_y) // 16), Debug.map_tile, Debug.editorMapMode)
        elif pygame.mouse.get_pressed()[2]:
            if Debug.editorMapMode == "Logic":
                cur_map.set(round((mouse_x + camera_x) // 16), round((mouse_y + camera_y) // 16), -1, Debug.editorMapMode)
        else:
            spr_selected_tile = sprsh_tileset.get_image(Debug.map_tile)
            if Debug.editorMapMode == "Visual":
                if Debug.map_tile <= len(cur_map.cur_tile_indices):
                    
                    spr_selected_tile = sprsh_tileset.get_image(cur_map.cur_tile_indices[Debug.map_tile])
            game_screen.blit(spr_selected_tile, spr_selected_tile.get_rect(center=(round((mouse_x - 8 + camera_x % 16) / 16) * 16 + 8 - camera_x % 16, round((mouse_y - 8 + camera_y % 16) / 16) * 16 + 8 - camera_y % 16)))
            #game_screen.blit(pygame.transform.scale(game_screen, (game_screen.get_size()[0] // 16, game_screen.get_size()[1] // 16)), spr_selected_tile.get_rect(center=(round((mouse_x - 8 + camera_x % 16) / 16) * 16 + 8 - camera_x % 16, round((mouse_y - 8 + camera_y % 16) / 16) * 16 + 8 - camera_y % 16)))
            #game_screen.blit(real_screen, spr_selected_tile.get_rect(center=(round((mouse_x - 8 + camera_x % 16) / 16) * 16 + 8 - camera_x % 16, round((mouse_y - 8 + camera_y % 16) / 16) * 16 + 8 - camera_y % 16)))
        

    if pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]:
        cam_speed = 4
    else:
        cam_speed = 1

    if pygame.key.get_pressed()[pygame.K_UP]:
        camera_y -= cam_speed
    if pygame.key.get_pressed()[pygame.K_DOWN]:
        camera_y += cam_speed
    if pygame.key.get_pressed()[pygame.K_LEFT]:
        camera_x -= cam_speed
    if pygame.key.get_pressed()[pygame.K_RIGHT]:
        camera_x += cam_speed
    
    #game_screen.blit(sprsh_tileset.get_image(round(frame / 16)), (16, 16))
    
    #pygame.draw.rect(game_screen, (0, 0, 0), (0, 0, game_width / 2, game_height / 2))

    #pygame.draw.rect(game_screen, (0, 0, 0), (game_width / 2, game_height / 2, game_width, game_height))

    Debug.render_debug_text()

    clock.tick(60)
    
    #if path == None:
        
    path = AStar.Pathfind((1,1), ((mouse_x + camera_x) // 16, (mouse_y + camera_y) // 16), cur_map)   

    if path != None:
        #print(path)
        
        for i in path:
            #print(i)
            #marker.draw(i["x"] * 16 - camera_x, i["y"] * 16 - camera_y - 16)
            game_screen.blit(pygame.image.load("sprites/characters/placeholderNew.png"), (i[0] * 16 - camera_x, i[1] * 16 - camera_y))
        

    game_screen.blit(cabinet, cabinet_curPos)

    real_screen.blit(scaled_screen, scaled_screen.get_rect(center=real_screen.get_rect().center))

    if round(cabinet_curPos[1]) == 0:
        snek.update(frame, (pygame.key.get_pressed()[pygame.K_w], pygame.key.get_pressed()[pygame.K_a], pygame.key.get_pressed()[pygame.K_s], pygame.key.get_pressed()[pygame.K_d]))
        snek.draw(mini_snake_screen)
        real_screen.blit(scaled_snake, scaled_snake.get_rect(center=real_screen.get_rect().center))

    
    
    pygame.display.flip()