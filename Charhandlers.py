import json
import math

import Spritehandlers as Spr

class Stat:
    
    def __init__(self, id, base, enhanced=False, level=1, boost=0):
        self.name = id
        self.base = base
        self.level = level
        self.boost = boost
        self.enhanced = enhanced
        
    def calc_stat(self):
        if self.enhanced:
            return math.floor(((2 * self.base + math.floor(0.25 * self.boost)) * self.level / 100) + self.level + 10)
        return math.floor((((2 * self.base + math.floor(0.25 * self.boost)) * self.level) / 100) + 5)
        
    def __str__(self):
        return (self.name).upper() + ": " + str(self.calc_stat())

class Character:
    
    def __init__(self, names=["","",""], pos=(0,0), sheet=""):
        self.names = names
        self.x = pos[0]
        self.y = pos[1]
        self.sheet = Spr.AdvancedSpritesheet(sheet)
        self.movement_speed = 30
        self.stats = {}
        
        self.dir = 0
        self.moveVec = (0,0)
        
        self.level = 100

    def set_xy(self, x, y):
        self.x = x
        self.y = y

    def overworld_collide(self, movementVec, map):
        newX = movementVec[0]
        curX = round(self.x)
        newY = movementVec[1]
        curY = round(self.y)
        if movementVec[0] != 0:
            if map.get((curX + newX + 8) // 16, (curY + 8) // 16) != -1:
                map_tile = map.tiles[map.get((curX + newX + 8) // 16, (curY + 8) // 16)]
                if  map_tile["block"]:
                    newX = 0
                else:
                    newX *= 1/map_tile["move"]
        if movementVec[1] != 0:
            if map.get((curX + 8) // 16, (curY + newY + 8) // 16) != -1:
                map_tile = map.tiles[map.get((curX + 8) // 16, (curY + newY + 8) // 16)]
                if map_tile["block"]:
                    newY = 0
                else:
                    newY *= 1/map_tile["move"]
        return newX, newY

    def overworld_movement(self, input, map):
        movement = (input[0], input[1])
        self.movementVec = movement
        if movement[1] > 0:
            self.dir = 2
        elif movement[1] < 0:
            self.dir = 0
        elif movement[0] > 0:
            self.dir = 1
        elif movement[0] < 0:
            self.dir = 3
        newX, newY =  self.overworld_collide(movement, map)
        self.x += newX
        self.y += newY
        
    def load_from_json(self, filename):
        with open("characters/" + filename + ".json", "r") as f:
            data = json.load(f)
            self.sheet = Spr.AdvancedSpritesheet(data["sprite"])
            self.names = [data["first_name"], data["mid_name"], data["last_name"]]
            self.stats = {}
            for i in data["stats"]:
                if i != "move":
                    self.stats[i] = Stat(i, data["stats"][i]["base"], data["stats"][i]["enhanced"], self.level)
                    print(self.stats[i])
                #print(i)
    def render(self, screen, cam, frame=0):
        if self.dir == 0: # North
            state = "Up"
        elif self.dir == 1: # East
            state = "Right"
        elif self.dir == 2: # South
            state = "Down"
        elif self.dir == 3: # West
            state = "Left"
        else:
            state = ""
            
        if self.movementVec == (0,0):
            state = "Idle" + state
        else:
            state = "Walk" + state
        screen.blit(self.sheet.animation(state, frame, 6), (self.x - cam[0], self.y - cam[1] - self.sheet.height))