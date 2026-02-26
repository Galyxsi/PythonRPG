import Spritehandlers as Spr
import pygame
import json
import os

import Texthandlers as Txt

class Maps():

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
        0: {"name": "grass", "move": 1, "map_move": 1, "block": False},
        1: {"name": "water", "move": 1, "map_move": 1, "swim": 1, "map_swim": 1, "block": True},
        2: {"name": "lava", "move": 1.5, "map_move": 1.5, "block": True},
        3: {"name": "cover", "move": 0.75, "map_move": 0.5, "block": False},
        4: {"name": "rough", "move": 2, "map_move": 2, "block": False},
        5: {"name": "wall", "move": 0, "map_move": 0, "block": True},
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
    defaultDualTilemap = Spr.Spritesheet("sprites/tilesets/testtiles2.png", 16, 16)


    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = [-1] * (self.width * self.height)
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

    def render(self, surface, tileset, cam_x, cam_y, window_width, window_height, anim_frame=0, tile_size=16):
        
        
        start_x = max(-1, (cam_x - tile_size) // tile_size)
        end_x = min(self.width, (cam_x + window_width + tile_size) // tile_size)

        start_y = max(-1, (cam_y - tile_size) // tile_size)
        end_y = min(self.height, (cam_y + window_height + tile_size) // tile_size)

        self.dualVismapUpdate(anim_frame, tileset, (start_x, end_x, start_y, end_y)) 

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                    if self.showVisTiles:
                        if x < self.width and y < self.height:
                            tiles = self.dualVisMapA[y + 1][x + 1]
                        #print(tiles)
                        if tiles != 0 and tiles != None:
                            for i in tiles:
                                surface.blit(tileset.get_image(tiles[i], anim_frame), (tile_size/2 + x * tile_size - cam_x ,tile_size/2 + y * tile_size - cam_y))
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
            rows.append(Maps.rle_encode_row(row))
        return rows

    def rle_decode_row(encoded_row):
        row = []
        for tile, count in encoded_row:
            row.extend([tile] * count)
        return row
    
    def rle_decode_map(rows, width, height):
        flat_map = []
        for encoded_row in rows:
            row = Maps.rle_decode_row(encoded_row)
            if len(row) != width:
                raise ValueError("Decoded row has wrong width")
            flat_map.extend(row)

        if len(flat_map) != width * height:
            raise ValueError("Decoded map has wrong size")

        return flat_map
    
    def rle_encode_tilemap(map):
        encoded_map = []
        for row in map:
            encoded_map.append(Maps.rle_encode_row(row))
        return encoded_map
    
    def rle_decode_tilemap(encoded_map):
        decoded_map = []
        for encoded_row in encoded_map:
            decoded_map.append(Maps.rle_decode_row(encoded_row))
        return decoded_map


    def to_list(self, name):
        return {
            "version": 3,
            "name": name,
            "width": self.width,
            "height": self.height,
            "map": Maps.rle_encode_map(self.map, self.width, self.height),
            "tilemap": "",
            "tilemap_tiles": Maps.rle_encode_tilemap(self.dualLogMapA),
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
            self.map = Maps.rle_decode_map(
                data["map"],
                self.width,
                self.height
            )
        elif data["version"] == 3:
            self.map = Maps.rle_decode_map(
                data["map"],
                self.width,
                self.height
            )
            self.dualLogMapA = Maps.rle_decode_tilemap(data["tilemap_tiles"])
            self.bg_color = data["bg-color"]
        

    
    @staticmethod
    def map_from_list(data):
        map = Maps(data["width"], data["height"])
        map.from_list(data)
        return map
    
    @staticmethod
    def map_to_list(map):
        return map.to_list()
    
    def save(self, filename, internalName=""):
        with open("maps/" + filename + ".json", "w") as f:
            json.dump(self.to_list(internalName), f, indent=4)
            Txt.Debug.debug_print(":checkbox: Saved map " + filename + ".json", 200)

    @staticmethod
    def load(filename):
        if not os.path.exists("maps/" + filename + ".json"):
            Txt.Debug.debug_print(":cRed::emptybox::cWhite: Failed to load map " + filename + ".json", 200)
            return Maps.map_from_list(default_map)
        
        with open("maps/" + filename + ".json", "r") as f:
            loadedMap = json.load(f)
            Txt.Debug.debug_print(":checkbox: Loaded map " + loadedMap["name"], 200)
            
            if len(Maps.map_from_list(loadedMap).map) != loadedMap["width"] * loadedMap["height"]:
                Txt.Debug.debug_print(":cRed::emptybox::cWhite: Map has invalid dimensions or missing tiles", 2000)

            return Maps.map_from_list(loadedMap)
        
    @staticmethod
    def unload_temp():
        for f in os.listdir("maps/"):
            if f.startswith("_"):
                os.remove("maps/" + f)
                
                
default_map = {
    "version": 3,
    "name": "Default",
    "author": "Ecliptic",
    "comment": "Wonder if I can add comments on here like this OoO",
    "width": 12,
    "height": 12,
    "map": [
        [
            [5,12]
        ],
        [
            [5,1],
            [2,3],
            [0,4],
            [1,3],
            [5,1]
        ],
        [
            [5,1],
            [2,3],
            [0,4],
            [1,3],
            [5,1]
        ],
        [
            [5,1],
            [2,3],
            [0,4],
            [1,3],
            [5,1]
        ],
        [
            [5,1],
            [0,10],
            [5,1]
        ],
        [
            [5,1],
            [0,10],
            [5,1]
        ],
        [
            [5,1],
            [0,10],
            [5,1]
        ],
        [
            [5,1],
            [0,10],
            [5,1]
        ],
        [
            [5,1],
            [4,3],
            [0,4],
            [3,3],
            [5,1]
        ],
        [
            [5,1],
            [4,3],
            [0,4],
            [3,3],
            [5,1]
        ],
        [
            [5,1],
            [4,3],
            [0,4],
            [3,3],
            [5,1]
        ],
        [
            [5,12]
        ]
    ],
    "tilemap": "",
    "tilemap_tiles": [
        [
            [8,13]
        ],
        [
            [8,1],
            [5,3],
            [0,4],
            [4,3],
            [8,2]
        ],
        [
            [8,1],
            [5,3],
            [0,4],
            [4,3],
            [8,2]
        ],
        [
            [8,1],
            [5,3],
            [0,4],
            [4,3],
            [8,2]
        ],
        [
            [8,1],
            [0,10],
            [8,2]
        ],
        [
            [8,1],
            [0,10],
            [8,2]
        ],
        [
            [8,1],
            [0,10],
            [8,2]
        ],
        [
            [8,1],
            [0,10],
            [8,2]
        ],
        [
            [8,1],
            [6,3],
            [0,4],
            [7,3],
            [8,2]
        ],
        [
            [8,1],
            [6,3],
            [0,4],
            [7,3],
            [8,2]
        ],
        [
            [8,1],
            [6,3],
            [0,4],
            [7,3],
            [8,2]
        ],
        [
            [8,13]
        ],
        [
            [8,13]
        ]
    ],
    "bg-color": "#757986",
    "units": [],
    "objects": []
}