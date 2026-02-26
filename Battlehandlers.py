import Charhandlers as Chr
import math
import pygame

class Battle:
    def __init__(self, character_list):
        self.character_list = character_list
        self.character_pos = {}
        self.character_paths = {}
        self.available_tiles = []
        for character in character_list:
            self.character_pos[character] = (character.x, character.y)
            self.character_paths[character] = []
        self.char_turn = 0
        self.turn = 0
        self.spr_available_tile = pygame.image.load("sprites/tilesets/available_tile.png").convert_alpha() 
        self.cam_target = (0,0)
    
    def init_turn(self, map):
        self.char_turn = 0
        cur_char = self.character_list[self.char_turn]
        self.cam_target = (cur_char.x, cur_char.y)
        self.available_tiles = self.load_available_movement(map)

    def load_available_movement(self, map):
        current_char = self.character_list[self.char_turn]
        start_tile = self.character_pos[current_char]
        start_tile = (start_tile[0] // 16, start_tile[1] // 16)
        available_tiles = []
        max_steps = (current_char.movement_speed + current_char.swim_speed) // 5
        #max_steps = current_char.movement_speed
        available_tiles = Chr.Pathfinder.FloodFill(start_tile, map, "4-dir", current_char.swim_speed, current_char.movement_speed)
        #for i in range(-max_steps, max_steps + 1):
        #    for j in range(-max_steps, max_steps + 1):
        #        if i == 0 and j == 0:
        #            continue
                
                #pathfound, costs = Chr.Pathfinder.Pathfind(start_tile, (start_tile[0] + i, start_tile[1] + j), map, "4-dir", current_char.swim_speed, max_steps)
                
        #        pathfound = Chr.Pathfinder.Pathfind(start_tile, (start_tile[0] + i, start_tile[1] + j), map, "4-dir", current_char.swim_speed, max_steps)
                
                #print("norm:" + str(costs["normal"]) + " water:" + str(costs["water"]) + " pos: (" + str(start_tile[0] + i) + ", " + str(start_tile[1] + j) + ")")
                
                #if pathfound and ( costs["normal"] <= current_char.movement_speed // 5 and costs["water"] <= current_char.swim_speed // 5):
                #    available_tiles.append((start_tile[0] + i, start_tile[1] + j))
        return available_tiles

    def next_turn(self, map):
        self.char_turn += 1
        if self.char_turn >= len(self.character_list):
            self.char_turn = 0
            self.turn += 1
        self.available_tiles = self.load_available_movement(map)



    def render(self, surface, camera, frame):
        
        for tile in self.available_tiles:
            surface.blit(self.spr_available_tile, (tile[0] * 16 - camera[0], tile[1] * 16 - camera[1]))
        for character in self.character_list:
            character.render(surface, camera, frame)
        

    def input(self, pos, input, map):
        if pos in self.available_tiles:
            self.move_character(pos, map)


    def move_character(self, pos, map):
        if pos in self.available_tiles:
            #self.character_pos[self.character_list[self.char_turn]] = (pos[0], pos[1])
            cur_path, costs =  Chr.Pathfinder.Pathfind((math.ceil((self.character_list[self.char_turn].x + 0.5) // 16), math.ceil((self.character_list[self.char_turn].y + 0.5) // 16)), (pos[0], pos[1]), map, "4-dir", self.character_list[self.char_turn].swim_speed)
            for path in cur_path:   
                self.character_paths[self.character_list[self.char_turn]].append(path)
            cur_path = self.character_paths[self.character_list[self.char_turn]]
            #print(cur_path, cost)
            if len(cur_path) != 0:     
                self.character_pos[self.character_list[self.char_turn]] = (cur_path[len(cur_path)-1][0] * 16, cur_path[len(cur_path)-1][1] * 16)
            self.next_turn(map)

    def tp_all_char(self, pos, map):
        for i, character in enumerate(self.character_list):
            self.character_pos[character] = pos
            self.character_list[i].set_xy(pos[0], pos[1])
            self.char_turn -= 1
            self.next_turn(map)

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
                self.character_list[i].walk(path, map, walkSpeed)
            else:
                if len(path) == 1:
                    self.character_list[i].x = target[0] * 16
                    self.character_list[i].y = target[1] * 16
                path.pop(0)
                if path:
                    self.character_list[i].walk(path, map, walkSpeed)