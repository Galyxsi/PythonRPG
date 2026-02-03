import pygame

import json
import os

import math
import random

pygame.init()

game_width, game_height = 256, 240

real_screen = pygame.display.set_mode((game_width * 2, game_height * 2), pygame.RESIZABLE)

game_screen = pygame.Surface((game_width, game_height))

mini_snake_screen = pygame.Surface((32,32))

pygame.display.set_caption("PythonRPG")


class Font:
    characters = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        ".!?,:;'\"-_"
        "0123456789"
        "[]/\\"
        "\uE000\uE001\uE002\uE004\uE003\uE005\uE006\uE008\uE007\uE009\uE00A\uE00B"
        " \uE000"

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
        ":cRed:": {255,0,0},
        ":cGreen:": {0,255,0},
        ":cBlue:": {0,0,255},
        ":cMagenta:": {255,0,255},
        ":cCyan:": {0,255,255},
        ":cYellow:": {255,255,0},
        ":cWhite:": {255,255,255},
    }
    def __init__(self, image_path, char_w, char_h, chars, cols):
        self.sheet = pygame.image.load("sprites/ui/font/" + image_path).convert_alpha()
        self.char_w = char_w
        self.char_h = char_h
        self.cols = cols
        self.glyphs = {}
        self.color_changes = {}

        for i, char_i in enumerate(chars):
            x = i % cols * char_w
            y = i // cols * char_h
            character_image = pygame.Surface((char_w, char_h), pygame.SRCALPHA).convert_alpha()
            character_image.blit(self.sheet, (0, 0), (x, y, char_w, char_h))
            self.glyphs[char_i] = character_image

        self.fallback = self.glyphs.get("?", pygame.Surface((char_w, char_h), pygame.SRCALPHA))

    def draw(self, surface, text, x, y, scale=1, color=(255, 255, 255, 255), spacing=-1, linespacing=8):
        cx, cy = x, y
        text = Font.emoji(text)
        text = self.color(text)
        i = 0
        for char in text:
            if char == "\n":
                cx = x
                cy += (self.ch + linespacing) * scale
                continue
            image = self.glyphs.get(char, self.fallback)
            image.set_alpha(color[3])
            if color != (255, 255, 255, 255):
                for xi in range(image.get_width()):
                    for yi in range (image.get_height()):
                        if image.get_at((xi, yi)) != (0, 0, 0, 0):
                            image.set_at((xi, yi), (color[0], color[1], color[2], image.get_at((xi, yi))[3]))
            #if i == 
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
    def color(self, text):
        for color, rgb in Font.COLORS.items():
            index = text.find(color)
            if index != -1:
                self.color_changes.append({"color": rbg, "index": index})
            text = text.replace(color, "\uE00C")
        if len(self.color_changes) > 0:
            self.color_changes.sort(key="index")
        return text
    
class Spritesheet:
    def __init__(self, filename, frame_width, frame_height):

        self.frame_width = frame_width
        self.frame_height = frame_height

        self.sheet = pygame.image.load(filename).convert_alpha()

        self.image_width = self.sheet.get_width()
        self.image_height = self.sheet.get_height()

        self.image_cols = self.image_width // self.frame_width
        self.image_rows = self.image_height // self.frame_height
        self.frame_count = self.image_cols * self.image_rows

    def get_image(self, frame_num):
        frame_num %= self.frame_count
        image = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA).convert_alpha()
        x = frame_num % self.image_cols * self.frame_width
        y = frame_num // self.image_cols * self.frame_height
        image.blit(self.sheet, (0, 0), (x, y, self.frame_width, self.frame_height))
        return image
    def get_image_xy(self, col, row):
        x = col * self.frame_width
        y = row * self.frame_height
        image = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), (x, y, self.frame_width, self.frame_height))
        return image
    
class LayeredSprite():

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

    font = None

    debug_messages_list = [{"text": "", "time": 0, "time_limit": 0}]
    

    @staticmethod
    def __init__():
        Debug.font = Font("font.png", 8, 8, Font.characters, 8)

    def debug_print(text, time=debug_message_fade):
        time = max(1, time)
        if Debug.debug_messages:
            print(text + " (" + str(time) + ")")
            Debug.debug_messages_list.append({"text": text, "time": 0, "time_limit": time})

    def render_debug_text():
        if len(Debug.debug_messages_list) == 0 or Debug.font == None:
            return
        for i in range(len(Debug.debug_messages_list)):
            Debug.debug_messages_list[i]["time"] += 1
            Debug.debug_messages_list[i]["time_limit"] = max(1, Debug.debug_messages_list[i]["time_limit"])
            Debug.font.draw(game_screen, ":right:" + Debug.debug_messages_list[i]["text"], 0, i * 16, 1, (255, 255, 255, 255 - (Debug.debug_messages_list[i]["time"] / Debug.debug_messages_list[i]["time_limit"]) * 255))
            
        for i in range(len(Debug.debug_messages_list)):
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

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = [-1] * (self.width * self.height)
    def idx(self, x, y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return None
        return x + y * self.width
    
    def get(self, x, y, default=-1):
        if self.idx(x, y) == None:
            return default
        return self.map[self.idx(x, y)]
    
    def set(self, x, y, value):
        if self.idx(x, y) == None:
            return False
        self.map[self.idx(x, y)] = value
        return True

    def render(self, surface, tileset, cam_x, cam_y, tile_size=16):
        start_x = max(0, cam_x // tile_size)
        end_x = min(self.width, (cam_x + game_width) // tile_size + 1)

        start_y = max(0, cam_y // tile_size)
        end_y = min(self.height, (cam_y + game_height) // tile_size + 1)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.get(x, y)
                if tile != -1:
                    surface.blit(tileset.get_image(tile), (x * tile_size - cam_x, y * tile_size - cam_y))

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
    
    

    def to_list(self, name):
        return {
            "version": 2,
            "name": name,
            "width": self.width,
            "height": self.height,
            "map": Map.rle_encode_map(self.map, self.width, self.height),
            "tilemap": "",
            "tilemap_tiles": {},
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
            Debug.debug_print(":emptybox: Failed to load map " + filename + ".json", 200)
            filename = "!default_test_map"
        with open("maps/" + filename + ".json", "r") as f:
            loadedMap = json.load(f)
            Debug.debug_print(":checkbox: Loaded map " + loadedMap["name"], 200)
            
            if len(Map.map_from_list(loadedMap).map) != loadedMap["width"] * loadedMap["height"]:
                Debug.debug_print(":emptybox: Map has invalid dimensions or missing tiles", 2000)

            return Map.map_from_list(loadedMap)
        
    @staticmethod
    def unload_temp():
        for f in os.listdir("maps/"):
            if f.startswith("_"):
                os.remove("maps/" + f)
        
class Snake():
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

        #mini_snake_screen.fill((255,255,255))
        #pygame.draw.rect(mini_snake_screen, (0,0,0), (self.snakeHead[0], self.snakeHead[1], 1, 1))
        #for body in self.snakeBody:
        #    pygame.draw.rect(mini_snake_screen, (0,0,0), (body[0], body[1], 1, 1))
        #pygame.draw.rect(mini_snake_screen, (0,0,0), (self.apple[0], self.apple[1], 1, 1))
    
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

        if frame % 3 != 0 or not self.started:
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
        elif self.snakeHead[0] > 31:
            self.snakeHead = (0, self.snakeHead[1])
        elif self.snakeHead[1] < 0:
            self.snakeHead = (self.snakeHead[0], 31)        
        elif self.snakeHead[1] > 31:
            self.snakeHead = (self.snakeHead[0], 0)

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

        

        pass




clock = pygame.time.Clock()

spr_selected_tile = pygame.image.load('selectedtile.png').convert_alpha()

sprsh_tileset = Spritesheet('sprites/tilesets/bgtiles.png', 16, 16)

markers_full = Spritesheet('markers.png', 16, 32)
markers_icons = Spritesheet('markers.png', 16, 16)
marker = LayeredSprite([{"sprite": markers_full.get_image(0), "layer": 0, "color": None}, {"sprite":markers_full.get_image(1), "layer": 1, "color": (255,0,0,255)}, {"sprite":markers_icons.get_image(2), "layer": 2, "color": None}])

camera_x, camera_y = 0, 0
cam_speed = 1
map_width, map_height = 3000, 12

cur_map = Map(map_width, map_height)

frame = 0

cur_map = Map.load("!default_test_map")

cabinet = pygame.image.load("sprites/arcades/snake_cabinet.png").convert_alpha()
cabinet_curPos = (0,256)
cabinet_pos = (0,256)

snek = Snake()

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
                    Debug.map_tile = 0
                    Debug.debug_print("Set tile to [" + Map.tiles[0]["name"] + "]")
                elif event.key == pygame.K_1:
                    Debug.map_tile = 1
                    Debug.debug_print("Set tile to [" + Map.tiles[1]["name"] + "]")
                elif event.key == pygame.K_2:
                    Debug.map_tile = 2
                    Debug.debug_print("Set tile to [" + Map.tiles[2]["name"] + "]")
                elif event.key == pygame.K_3:
                    Debug.map_tile = 3
                    Debug.debug_print("Set tile to [" + Map.tiles[3]["name"] + "]")
                elif event.key == pygame.K_4:
                    Debug.map_tile = 4
                    Debug.debug_print("Set tile to [" + Map.tiles[4]["name"] + "]")
                elif event.key == pygame.K_5:
                    Debug.map_tile = 5
                    Debug.debug_print("Set tile to [" + Map.tiles[5]["name"] + "]")
                elif event.key == pygame.K_F1:
                    cur_map.save("_temp_save", "Local Save")
                elif event.key == pygame.K_F2:
                    if cabinet_pos == (0, 0):
                        cabinet_pos = (0, 256)
                    else:
                        cabinet_pos = (0, 0)
        if event.type == pygame.MOUSEWHEEL:
            if Debug.map_editor:
                Debug.map_tile += event.y
                Debug.map_tile %= len(Map.tiles)
                Debug.debug_print("Set tile to [" + Map.tiles[Debug.map_tile]["name"] + "]")
        if event.type == pygame.VIDEORESIZE:
            real_screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

    game_screen.fill((255, 0, 255))
    
    cur_map.render(game_screen, sprsh_tileset, camera_x, camera_y)
    
    #game_screen.blit(spr_selected_tile, spr_selected_tile.get_rect(center=(round((mouse_x - 8) / 16) * 16 + 8, round((mouse_y - 8) / 16) * 16 + 8)))
    
    if Debug.map_editor:
        if pygame.mouse.get_pressed()[0]:
            cur_map.set(round((mouse_x + camera_x) // 16), round((mouse_y + camera_y) // 16), Debug.map_tile)
        elif pygame.mouse.get_pressed()[2]:
            cur_map.set(round((mouse_x + camera_x) // 16), round((mouse_y + camera_y) // 16), -1)
        else:
            game_screen.blit(sprsh_tileset.get_image(Debug.map_tile), spr_selected_tile.get_rect(center=(round((mouse_x - 8 + camera_x % 16) / 16) * 16 + 8 - camera_x % 16, round((mouse_y - 8 + camera_y % 16) / 16) * 16 + 8 - camera_y % 16)))
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

    game_screen.blit(cabinet, cabinet_curPos)

    real_screen.blit(scaled_screen, scaled_screen.get_rect(center=real_screen.get_rect().center))

    if round(cabinet_curPos[1]) == 0:
        snek.update(frame, (pygame.key.get_pressed()[pygame.K_w], pygame.key.get_pressed()[pygame.K_a], pygame.key.get_pressed()[pygame.K_s], pygame.key.get_pressed()[pygame.K_d]))
        snek.draw(mini_snake_screen)
        real_screen.blit(scaled_snake, scaled_snake.get_rect(center=real_screen.get_rect().center))

    
    
    pygame.display.flip()