import Charhandlers as Chr
import math
import pygame
import os
import json

class Battle:
    def __init__(self, character_list):
        self.state = "MOVE"
        self.character_list = character_list
        self.character_pos = {}
        self.character_paths = {}
        self.available_tiles = []
        self.attack_tiles = []
        self.attack_target_tiles = []
        for character in character_list:
            self.character_pos[character] = (character.x, character.y)
            self.character_paths[character] = []
        self.char_turn = 0
        self.turn = 0
        self.spr_available_tile = pygame.image.load("sprites/tilesets/available_tile.png").convert_alpha() 
        self.spr_attack_tile = pygame.image.load("sprites/tilesets/attack_tile.png").convert_alpha() 
        self.cam_target = (0,0)
        self.map = None
        self.all_attacks = {}
        self.load_all_attacks()
    
    def load_all_attacks(self):
        all_atk_files = [f for f in os.listdir("characters/attacks/") if os.path.isfile("characters/attacks/" + f)]
        for atk in all_atk_files:
            with open("characters/attacks/" + atk, "r") as f:
                data = json.load(f)
                self.all_attacks[data["id"]] = {"name": data["name"], "category": data["category"], "range": data["range"], "effects": data["effects"]}
        print(self.all_attacks)
        
    
    def init_turn(self, map=None):
        map = map or self.map
        self.state = "MOVE"
        self.char_turn = 0
        for character in self.character_list:
            self.character_paths[character] = []
        cur_char = self.character_list[self.char_turn]
        self.cam_target = (cur_char.x, cur_char.y)
        self.available_tiles = self.load_available_movement(map)

    def load_available_movement(self, map=None):
        map = map or self.map
        current_char = self.character_list[self.char_turn]
        start_tile = self.character_pos[current_char]
        start_tile = (start_tile[0] // 16, start_tile[1] // 16)
        available_tiles = []
        max_steps = (current_char.movement_speed + current_char.swim_speed) // 5
        #max_steps = current_char.movement_speed
        available_tiles = Chr.Pathfinder.FloodFill(start_tile, map, "4-dir", current_char.swim_speed, current_char.movement_speed, current_char.float_speed)
        for char in self.character_pos:
            cur_pos = self.character_pos[char]
            cur_pos = (cur_pos[0] // 16, cur_pos[1] // 16)
            #print(self.character_pos[char])
            if cur_pos in available_tiles:
                available_tiles.remove(cur_pos)
        return available_tiles
    
    def load_available_attack_range(self, attack, map=None):
        map = map or self.map
        self.attack_tiles = []
        current_char = self.character_list[self.char_turn]
        cur_atk = self.all_attacks[current_char.currentAttacks[0]]
        start_tile = self.character_pos[current_char]
        start_tile = (start_tile[0] // 16, start_tile[1] // 16)
        available_tiles = []
        attackable_tiles = []
        if cur_atk["range"]["type"] == "flood":
            available_tiles = Chr.Pathfinder.FloodFill(start_tile, map, "4-dir", 0, 0, cur_atk["range"]["max"], cur_atk["range"]["min"] // 5)
        elif cur_atk["range"]["type"] == "touch":
            for i in range(-1,2):
                for j in range(-1,2):
                    if abs(i) != abs(j):
                        cur_tile = (start_tile[0] + i, start_tile[1] + j)
                        cur_tile_id = map.get(cur_tile[0], cur_tile[1])
                        if not cur_tile_id == -1 and not cur_tile_id == 5:
                            available_tiles.append(cur_tile)
        for char in self.character_pos:
                pos = self.character_pos[char]
                pos = (pos[0] // 16, pos[1] // 16)
                if pos in available_tiles:
                    attackable_tiles.append(pos)
        return attackable_tiles, available_tiles

    def next_turn(self, map=None):
        map = map or self.map
        self.state = "MOVE"
        self.char_turn += 1
        if self.char_turn >= len(self.character_list):
            self.char_turn = 0
            self.turn += 1
        self.available_tiles = self.load_available_movement(map)



    def render(self, surface, camera, frame):
        if self.state == "MOVE":
            for tile in self.available_tiles:
                surface.blit(self.spr_available_tile, (tile[0] * 16 - camera[0], tile[1] * 16 - camera[1]))
        elif self.state == "ATK":
            for tile in self.attack_tiles:
                surface.blit(self.spr_available_tile, (tile[0] * 16 - camera[0], tile[1] * 16 - camera[1]))
            for tile in self.attack_target_tiles:
                surface.blit(self.spr_attack_tile, (tile[0] * 16 - camera[0], tile[1] * 16 - camera[1]))
        for character in self.character_list:
            character.render(surface, camera, frame)
        

    def click(self, pos, map=None):
        map = map or self.map
        if self.state == "MOVE" and pos in self.available_tiles:
            cur_pos = self.character_pos[self.character_list[self.char_turn]]
            self.available_tiles.append((cur_pos[0] // 16, cur_pos[1] // 16))
            self.move_character(pos, map)
            self.available_tiles.remove(pos)
        elif self.state == "ATK" and pos in self.attack_target_tiles:
            self.next_turn()
            

    def move_character(self, pos, map=None):
        map = map or self.map
        if pos in self.available_tiles:
            #self.character_pos[self.character_list[self.char_turn]] = (pos[0], pos[1])
            cur_pos = self.character_pos[self.character_list[self.char_turn]] 
            cur_path, costs =  Chr.Pathfinder.Pathfind((cur_pos[0] // 16, cur_pos[1] // 16), (pos[0], pos[1]), map, "4-dir", self.character_list[self.char_turn].swim_speed, 100, self.character_list[self.char_turn].float_speed > 0)
            #print(cur_pos, cur_path)
            for path in cur_path:   
                self.character_paths[self.character_list[self.char_turn]].append(path)
            cur_path = self.character_paths[self.character_list[self.char_turn]]
            #print(cur_path, costs)
            if len(cur_path) != 0:     
                self.character_pos[self.character_list[self.char_turn]] = (cur_path[len(cur_path)-1][0] * 16, cur_path[len(cur_path)-1][1] * 16)
            #self.next_turn(map)

    def tp_all_char(self, pos, map=None):
        map = map or self.map
        for i, character in enumerate(self.character_list):
            self.character_pos[character] = pos
            self.character_list[i].set_xy(pos[0], pos[1])
            self.char_turn -= 1
            self.next_turn(map)
            self.character_paths[character] = []

    def char_tile_pos(self, character):
        return (round((character.x) / 16), round((character.y) / 16))

    def cur_cam_target(self):
        path_count = 0
        for char in self.character_list:
            path = self.character_paths[char]
            if path and len(path) > 0:
                path_count += 1
                self.cam_target = (char.x, char.y)
        if path_count == 0:
            cur_char = self.character_list[self.char_turn]
            self.cam_target = (cur_char.x, cur_char.y)
        return self.cam_target

    def update(self, map, walkSpeed):
        for i, character in enumerate(self.character_list):
            path = self.character_paths[character]
            if not path:
                self.character_list[i].overworld_movement((0, 0), map)
                continue
            target = path[0]
            #cur_tile = (character.x, character.y)
            cur_tile = self.char_tile_pos(character)
            if target != cur_tile:
                self.character_list[i].walk(path, map, walkSpeed, False)
            else:
                if len(path) == 1:
                    self.character_list[i].x = target[0] * 16
                    self.character_list[i].y = target[1] * 16
                path.pop(0)
                if path:
                    self.character_list[i].walk(path, map, walkSpeed, False)
    
    def lock_in(self, map=None):
        map = map or self.map
        if self.state == "MOVE":
            self.attack_target_tiles, self.attack_tiles = self.load_available_attack_range(self.character_list[self.char_turn].currentAttacks[0], map)
            self.state = "ATK"
        elif self.state == "ATK":
            self.state = "MOVE"
            
    def set_map(self, map):
        self.map = map
        
    