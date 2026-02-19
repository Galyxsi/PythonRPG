import json
import math

import Maphandlers as Map
import Spritehandlers as Spr

class Pathfinder:    
    @staticmethod
    def Pathfind(startCoordinates, end, tiles, move_type="8-dir", limit=10):
        openList = []
        closedList = []
        
        count = 0

        openList.append({"x": startCoordinates[0], "y": startCoordinates[1], "f": 0, "g": 0, "h":0, "p": None, "c": 0})
        
        W = tiles.width
        H = tiles.height

        def in_bounds(x, y):
            return 0 <= x < W and 0 <= y < H
        
        def is_blocked(x, y):
            #print(Map.Maps.tiles[tiles.get(x, y)])
            return Map.Maps.tiles[tiles.get(x, y)]["block"]
        
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
            count += 1
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
                step_cost = Map.Maps.tiles[tiles.get(nx, ny)]["move"]
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
                
                if curNode["c"] + step_cost > limit:
                    continue
                openList.append({"x": nx, "y": ny, "f": f_cost, "g": g_cost, "h": h_cost, "p": curNode, "c": curNode["c"] + step_cost})
            
                
        return []
    

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
        self.movementVec = (0,0)
        
        self.level = 100

    def set_xy(self, x, y):
        self.x = x
        self.y = y

    def overworld_collide(self, movementVec, map):
        newX = movementVec[0]
        newXi = round(movementVec[0])
        curX = round(self.x)
        newY = movementVec[1]
        newYi = round(movementVec[1])
        curY = round(self.y)
        if movementVec[0] != 0:
            if map.get((curX + newXi + 8) // 16, (curY + 8) // 16) != -1:
                map_tile = map.tiles[map.get((curX + newXi + 8) // 16, (curY + 8) // 16)]
                if  map_tile["block"]:
                    newX = 0
                else:
                    newX *= 1/map_tile["move"]
        if movementVec[1] != 0:
            if map.get((curX + 8) // 16, (curY + newYi + 8) // 16) != -1:
                map_tile = map.tiles[map.get((curX + 8) // 16, (curY + newYi + 8) // 16)]
                if map_tile["block"]:
                    newY = 0
                else:
                    newY *= 1/map_tile["move"]
        return newX, newY

    def overworld_movement(self, input, map):
        movement = (input[0], input[1])
        self.movementVec = movement
        if math.floor(movement[1]) > 0:
            self.dir = 2
        elif math.floor(movement[1]) < 0:
            self.dir = 0
        elif math.floor(movement[0]) > 0:
            self.dir = 1
        elif math.floor(movement[0]) < 0:
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
    def walk(self, path, map, walkSpeed):
        target = (round(path[0][0]) * 16, round(path[0][1]) * 16)
        curX = round(self.x)
        curY = round(self.y)
        if abs(target[0] - curX) - 0.5 < walkSpeed:
            xMove = target[0] - self.x
        elif target[0] > curX:
            xMove = walkSpeed
        elif target[0] < curX:
            xMove = -walkSpeed
        else:
            xMove = 0
        if abs(target[1] - curY) - 0.5 < walkSpeed:
            yMove = target[1] - self.y
        elif target[1] > curY:
            yMove = walkSpeed
        elif target[1] < curY:
            yMove = -walkSpeed
        else:
            yMove = 0
        movementVec = (xMove, yMove)
        #print(movementVec)
        self.overworld_movement(movementVec, map)

            
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
            
        #print(self.movementVec)
        if self.movementVec == (0,0):
            state = "Idle" + state
        else:
            state = "Walk" + state
        screen.blit(self.sheet.animation(state, frame, 6), (self.x - cam[0], self.y - cam[1] - self.sheet.height // 2))