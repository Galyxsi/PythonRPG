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
            return math.floor(0.01 * (2 * self.base + math.floor(0.25 * self.boost)) * self.level) + self.level + 10
        return math.floor(0.01 * (self.base + math.floor(0.25 * self.boost)) * self.level) + self.level + 5
        
    def __str__(self):
        return (self.name).upper() + ": " + str(self.calc_stat())

class Character:
    
    def __init__(self, names=["","",""], pos=(0,0), sheet=Spr.Spritesheet("sprites/characters/placeholderNew.png", 16,16)):
        self.names = names
        self.x = pos[0]
        self.y = pos[1]
        self.sheet = sheet
        self.movement_speed = 30
        self.stats = {}
        
        self.level = 100
        
    def load_from_json(self, filename):
        with open("characters/" + filename + ".json", "r") as f:
            data = json.load(f)
            self.sheet = data["sprite"]
            self.names = [data["first_name"], data["mid_name"], data["last_name"]]
            self.stats = {}
            for i in data["stats"]:
                if i != "move":
                    self.stats[i] = Stat(i, data["stats"][i]["base"], data["stats"][i]["enhanced"], self.level)
                    print(self.stats[i])
                #print(i)