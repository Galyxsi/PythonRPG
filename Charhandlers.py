import json
import math
import heapq

import Maphandlers as Map
import Spritehandlers as Spr



class Pathfinder:    
    @staticmethod
    def Pathfind(startCoordinates, end, tiles, move_type="8-dir", swim=0, limit=10):
        openList = []
        closedList = []
        
        count = 0

        openList.append({"x": startCoordinates[0], "y": startCoordinates[1], "f": 0, "g": 0, "h":0, "p": None, "c": 0, "cn": 0, "cw": 0, "w": False})
        
        W = tiles.width
        H = tiles.height

        def in_bounds(x, y):
            return 0 <= x < W and 0 <= y < H
        
        def is_blocked(x, y, swim=0):
            cur_tile = Map.Maps.tiles[tiles.get(x, y)]
            #print(Map.Maps.tiles[tiles.get(x, y)])
            if swim == 0:
                return cur_tile["block"]
            elif "swim" in cur_tile and swim > 0:
                return False
            else:
                return cur_tile["block"]
        
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
                c = {"normal": 0, "water": 0}
                while n is not None:
                    path.append((n["x"], n["y"]))
                    if n["w"]:
                        #print(n["c"])
                        c["water"] += n["cw"]
                    else:
                        c["normal"] += n["cn"]
                    n = n["p"]
                path.reverse()
                #print(c)
                return path, c

            for nx, ny, dx, dy in neighbors(curNode["x"], curNode["y"]):
                if not in_bounds(nx, ny) or is_blocked(nx, ny, swim):
                    continue
                cur_tile = Map.Maps.tiles[tiles.get(nx, ny)]
                wate_cost = 0
                norm_cost = 0
                if "swim" in cur_tile and swim != 0:
                    step_cost = cur_tile["map_swim"]
                    wate_cost = cur_tile["map_swim"]
                    water_tile = True
                else:
                    step_cost = cur_tile["map_move"]
                    norm_cost = cur_tile["map_move"]
                    water_tile = False
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
                
                openList.append({"x": nx, "y": ny, "f": f_cost, "g": g_cost, "h": h_cost, "p": curNode, "c": curNode["c"] + step_cost, "cn": norm_cost, "cw": wate_cost, "w": water_tile})
            
                
        return [], {"normal": 0, "water": 0}
    
    def FloodFill(start, tiles, move_type="4-dir", swim=0, limit=10):
        W, H = tiles.width, tiles.height
        
        def in_bounds(x, y):
            return 0 <= x < W and 0 <= y < H
        
        def tile_info(x, y):
            return Map.Maps.tiles[tiles.get(x, y)]
        
        def is_blocked(x, y):
            cur_tile = tile_info(x, y)
            if swim == 0:
                return cur_tile["block"]
            elif "swim" in cur_tile and swim > 0:
                return False
            else:
                return cur_tile["block"]
        
        def neighbors(x, y):
            if move_type == "4-dir":
                return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            else:
                out = []
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if dx == 0 and dy == 0:
                            continue
                        if dx != 0 and dy != 0:
                            continue
                        out.append((x + dx, y + dy))
                return out
        
        
        fullList = []
        fullStat = []
        limitedList = []
        limitedStat = []
        limitedList.append((start[0], start[1]))
        limitedStat.append(((0,0),(0,0)))
        validMovement = []
        vMStat = []
        
        #print("Limit:" + str(limit))
        #print("Swim:" + str(swim))
        while limitedList:
            curPos = limitedList.pop(0)
            curStt = limitedStat.pop(0)
            x, y, parent, counts = curPos[0], curPos[1], curStt[0], curStt[1]
            #print(counts)
            for nx, ny in neighbors(x, y):
                if not fullList.count((nx, ny)) > 50: 
                    info = tile_info(nx, ny)
                    fullList.append((nx, ny))
                    
                    moveCost = counts[0]
                    swimCost = counts[1]
                    if "swim" in info:
                        swimO = info["swim"]
                        fullStat.append(((x,y), (0, counts[1] + swimO)))
                        #print(swimO + counts[1])
                        if counts[1] + swimO > swim // 5:
                            continue
                        swimCost = info["swim"] + counts[1]
                    else:
                        fullStat.append(((x,y), (counts[0] + info["move"], 0)))
                        if counts[0] + info["move"] > limit // 5:
                            continue  
                        moveCost = info["move"] + counts[0]
                    if is_blocked(nx, ny):
                        continue
                    #if (nx, ny) in limitedList:
                        #if moveCost < limitedStat[limitedList.index((nx, ny))][1][0] or swimCost < limitedStat[limitedList.index((nx, ny))][1][1]:
                            #limitedStat[limitedList.index((nx, ny))] = ((x, y), (moveCost, swimCost))
                    #else:
                    #print((moveCost, swimCost))
                    limitedList.append((nx, ny))
                    limitedStat.append(((x, y), (moveCost, swimCost)))
                        
                    #print("added: " + str((nx, ny)))
                    if not (nx, ny) in validMovement:
                        validMovement.append((nx, ny))
                        #print("move: " + str(moveCost) + ", swim: " + str(swimCost))
                        vMStat.append(((x, y), (moveCost, swimCost)))
                    #print("added: " + str((nx, ny)))
                    
        return validMovement    
    

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
        self.swim_speed = 0
        self.stats = {}
        
        self.dir = 0
        self.movementVec = (0,0)
        
        self.level = 100

    def set_xy(self, x, y):
        self.x = x
        self.y = y

    def set_tilexy(self, x, y):
        self.x = x * 16
        self.y = y * 16

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
                if  map_tile["block"] and not ("swim" in map_tile and self.swim_speed > 0):
                    newX = 0
                else:
                    newX *= 1/map_tile["move"]
        if movementVec[1] != 0:
            if map.get((curX + 8) // 16, (curY + newYi + 8) // 16) != -1:
                map_tile = map.tiles[map.get((curX + 8) // 16, (curY + newYi + 8) // 16)]
                if map_tile["block"] and not ("swim" in map_tile and self.swim_speed > 0):
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
            self.movement_speed = data["move"]
            if "swim" in data:
                self.swim_speed = data["swim"]
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