import pygame

import random

import Texthandlers as Txt

class Snake:
    snakeBody = []
    validLocations = []

    snakeColors = [
        [(0,90,0), (50,200,50), (255,0,0), (255,255,255), (0,0,0)],
        [(95,123,118), (135,157,163), (95,123,118), (135,157,163), (50,57,70)],
        [(255, 0, 255), (255, 100, 255), (255, 0, 255), (255, 100, 255), (50, 0, 50)],
        [(0, 255, 255), (100, 255, 255), (0, 255, 255), (100, 255, 255), (0, 50, 50)],
        [(255, 255, 0), (255, 255, 100), (255, 255, 0), (255, 255, 100), (50, 50, 0)],
    ]

    font = Txt.Font("arcadefont.png", 3,4, "1234567890", 5)

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
        
class Minesweeper:
    sweeperColors = [
        [(255, 255, 255), (0,0,0), (128, 128, 128), (255,0,0), (0,255,0), (0,0,255), (255,0,255), (255,255,0), (0,255,255), (128,0,128)],
        [(0,0,0), (0,0,255), (20, 190, 20), (200,40,40), (10,10,180), (185, 15, 15), (0, 90, 180), (255,255,255), (128, 128, 128), (255,255,255), (255,0,0)]
    ]

    def __init__(self):
        self.minefield = [[(-1 if random.randint(0,100) - 10 <= 0 else 0) for _ in range(32)] for _ in range(32)]
        #print(minefield)
        for i in range(32):
            for j in range(32):
                if self.minefield[i][j] != -1:
                    nearby_mines = 0
                    for k in range(3):
                        for l in range(3):
                            if (k == 0 and i == 0) or (k == 2 and i == 31):
                                pass
                            elif (l == 0 and j == 0) or (l == 2 and j == 31):
                                pass
                            elif self.minefield[i + k - 1][j + l - 1] == -1:
                                nearby_mines += 1
                    self.minefield[i][j] = nearby_mines
    
    def countMines(self):
        mines = 0
        for i in range(32):
            for j in range(32):
                if self.minefield[i][j] == -1:
                    mines += 1
        print(mines)
    
    def update(self, frame, input):
        print(str(input["x"]) + ", " + str(input["y"]))
        
    def draw(self, screen):
        color_index = 1
        screen.fill(self.sweeperColors[color_index][0])
        for i in range(32):
            for j in range(32):
                if self.minefield[i][j] != 0:
                    pygame.draw.rect(screen, self.sweeperColors[color_index][self.minefield[i][j]], (i,j, 1, 1))
                #elif self.minefield[i][j] == -1:
                #    pygame.draw.rect(screen, self.sweeperColors[])