import pygame

import os

import math
import random

import copy

# Spritesheet, Adv Spritesheet, & Layered Sprites. 
import Spritehandlers as Spr
# Maps.
import Maphandlers as Map
# Font & Debug.
import Texthandlers as Txt
# Characters, Players, Enemies, etc.
import Charhandlers as Chr
# Snek & da mines
import Arcades as Arc
# Battle System
import Battlehandlers as Bat
os.environ['SDL_AUDIODRIVER'] = 'dsp'

pygame.init()


# Screen initialisation
game_width, game_height = 256, 240

#pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 0)

# This is the actual Pygame window, split from the game screen to allow for any size window without any stretching
desktop_size = pygame.display.get_desktop_sizes()[0]
real_screen = pygame.display.set_mode((desktop_size[0] // 2, desktop_size[1] // 2), pygame.RESIZABLE)
#real_screen = pygame.display.set_mode(pygame.display.list_modes()[0])

# What the game actually gets rendered on
game_screen = pygame.Surface((game_width, game_height))
# Currently for Snake minigame, likely to be repurposed for many minigames
mini_snake_screen = pygame.Surface((32,32))


# Used for testing an idea with the UI, unsure whether or not this will be kept
hud_screen = pygame.Surface((64, game_height))
spr_hud_bg = Spr.NineSlice("nine_slice_test.png", 16)
hud_alpha = 64
hud_x = 8
cur_hud_alpha = 64
cur_hud_x = 8

pygame.display.set_caption("PythonRPG")

debug = Txt.Debug()
            
# Two testing characters, New and Sandbag
char = Chr.Character()
char.load_from_json("misti")
char.set_tilexy(5, 5)

sandbag = Chr.Character()
#enemy.load_from_json("sandbag")
sandbag.load_from_json("sandbag")
sandbag.set_tilexy(8, 8)

badbag = Chr.Character()
badbag.load_from_json("badbag")
badbag.set_tilexy(6,6)

character_list = [char, sandbag, badbag]
character_turn = 0

# This can either be overworld or battle.
game_mode = "battle"

clock = pygame.time.Clock()

sprsh_tileset = Spr.Spritesheet('sprites/tilesets/testtiles2.png', 16, 16)

# Layered Sprite testing, unused
markers_full = Spr.Spritesheet('markers.png', 16, 32)
markers_icons = Spr.Spritesheet('markers.png', 16, 16)
marker = Spr.LayeredSprite([{"sprite": markers_full.get_image(0), "layer": 0, "color": None}, {"sprite":markers_full.get_image(1), "layer": 1, "color": (255,0,0,255)}, {"sprite":markers_icons.get_image(2), "layer": 2, "color": None}])

# Camera variables
camera_x, camera_y = 0, 0
cam_ix, cam_iy = 0, 0
cam_target = (-1, -1)
reached_target = True
cam_speed = 1

map_width, map_height = 0, 0

# The current map. initialises to blank 12x12 map
cur_map = Map.Maps(map_width, map_height)


# Frame counter
frame = 0

# Map cycler for debug
map_list = [
    "!default_test_map",
    "!lines",
    #"ai_testing/!river_outpost",
    #"ai_testing/!demo16x16",
    #"ai_testing/!windsurf_test",
    #"ai_testing/!island_outpost",
    #"ai_testing/!custom_island",
    #"ai_testing/!ruined_courtyard32x32",
    #"ai_testing/!custom_map_rle",
    #"ai_testing/!custom64",
    "ai_testing/!obsidian_oasis",
    #"ai_testing/!dungeon"
]
curMapID = 0
cur_map = Map.Maps.load("a")

# Battle begin
cur_battle = Bat.Battle(character_list)
cur_battle.init_turn(cur_map)

# Arcade begin
cabinet = pygame.image.load("sprites/arcades/snake_cabinet.png").convert_alpha()
cabinet_curPos = (0,256)
cabinet_pos = (0,256)

snek = Arc.Snake()
mine = Arc.Minesweeper()

# For debug map randomizer
last_few_maps = []

path = None
pathHighlight = None
lastPathTarget = (-1,-1)

test2 = Spr.AdvancedSpritesheet("sprites/characters/playable/Witch.png")

# Main game loop
while True:
    
    

    # Some arcade minigame stuff
    pygame.display.set_icon(mini_snake_screen)
    cabinet_curPos = (cabinet_curPos[0] + (cabinet_pos[0] - cabinet_curPos[0]) * 0.1, cabinet_curPos[1] + (cabinet_pos[1] - cabinet_curPos[1]) * 0.1)

    # Frame counter
    frame += 1
    
    # The handler that deals with keeping the game at a consistant resolution while the window resizes
    scaled_screen = pygame.transform.scale(game_screen, real_screen.get_size())
    if real_screen.get_width() > real_screen.get_height():
        scaled_screen = pygame.transform.scale(game_screen, (real_screen.get_height(), real_screen.get_height()))
        scaled_snake = pygame.transform.scale(mini_snake_screen, (real_screen.get_height() // 2, real_screen.get_height() // 2))
    else:
        scaled_screen = pygame.transform.scale(game_screen, (real_screen.get_width(), real_screen.get_width()))
        scaled_snake = pygame.transform.scale(mini_snake_screen, (real_screen.get_width() // 2, real_screen.get_width() // 2))

    # game-space mouse positions
    mouse_x = (pygame.mouse.get_pos()[0] - (real_screen.get_width() - scaled_screen.get_size()[0]) / 2) * game_width / scaled_screen.get_size()[0] 
    mouse_y = (pygame.mouse.get_pos()[1] - (real_screen.get_height() - scaled_screen.get_size()[1]) / 2) * game_height / scaled_screen.get_size()[1]

    # More UI testing
    if mouse_x < game_width - 64:
        hud_x = 8
        hud_alpha = 64
    else:
        hud_x = 64
        hud_alpha = 255
        
    if cur_hud_alpha != hud_alpha:
        cur_hud_alpha += (hud_alpha - cur_hud_alpha) * 0.1
        hud_screen.set_alpha(cur_hud_alpha)
    if cur_hud_x != hud_x:
        cur_hud_x += (hud_x - cur_hud_x) * 0.1
        

    # Pygame events
    for event in pygame.event.get():
        # Turns out you need to code the ability to close the game
        if event.type == pygame.QUIT:
            # Delete temporary maps upon quitting
            Map.Maps.unload_temp()
            exit()
        if event.type == pygame.KEYDOWN:
            # Esc also closes the game
            if event.key == pygame.K_ESCAPE:
                # Delete temporary maps upon quitting
                Map.Maps.unload_temp()
                exit()
            #if event.key == pygame.K_F11:
            #    #game_width, game_height = 256, 240
            #    fullSize = pygame.display.list_modes()[0]
            #    print(pygame.display.get_surface().get_width() == fullSize[0] and pygame.display.get_surface().get_height() == fullSize[1])
            #    if pygame.display.get_surface().get_width() == fullSize[0] and pygame.display.get_surface().get_height() == fullSize[1]:
            #        pygame.display.set_mode((game_width, game_height), pygame.RESIZABLE)
            #    else:
            #        game_width, game_height = pygame.display.get_surface().get_width(), pygame.display.get_surface().get_height()
            #        pygame.display.set_mode(fullSize, pygame.FULLSCREEN)
                #pygame.display.toggle_fullscreen()
                #print(full)
            if event.key == pygame.K_SPACE:
                cur_battle.lock_in()
                #cur_battle.next_turn(cur_map)
            # 4 cycles the map for debug purposes
            elif event.key == pygame.K_4:
                    curMapID += 1
                    cur_map = Map.Maps.load(map_list[curMapID % len(map_list)])
                    cur_battle.init_turn(cur_map)
            # 9 teleports all characters to the mouse position
            elif event.key == pygame.K_9:
                cur_battle.tp_all_char((round(mouse_x + cam_ix), round(mouse_y + cam_iy)), cur_map)
            # 8 toggles map editor/debug stuff
            elif event.key == pygame.K_8:
                Txt.Debug.map_editor = not Txt.Debug.map_editor
            # Map editor/debug stuff
            if Txt.Debug.map_editor:
                # 0 sets the maps to display logic tiles
                if event.key == pygame.K_0:
                    Txt.Debug.editorMapMode = "Logic"
                    cur_map.showVisMap = False
                # 1 sets the maps to display visual tiles
                elif event.key == pygame.K_1:
                    Txt.Debug.editorMapMode = "Visual"
                    cur_map.showVisMap = True
                # 2 Changes what the currently selected tile to draw with is
                elif event.key == pygame.K_2:
                    Txt.Debug.map_tile += 1
                    if Txt.Debug.editorMapMode == "Logic":
                        Txt.Debug.map_tile %= len(Map.Maps.tiles)
                        Txt.Debug.debug_print("Set tile to [" + Map.Maps.tiles[Txt.Debug.map_tile]["name"] + "]")
                    elif Txt.Debug.editorMapMode == "Visual":
                        Txt.Debug.map_tile %= cur_map.cur_total_tiles
                # 3 is for pathfinding tests
                elif event.key == pygame.K_3:
                    path = Chr.Pathfinder.Pathfind((math.ceil((char.x + 0.5) // 16), math.ceil((char.y + 0.5) // 16)), ((mouse_x + cam_ix) // 16, (mouse_y + cam_iy) // 16), cur_map, "4-dir", 5)
                    
                

                # 5 reshuffles Minesweeper minigame
                elif event.key == pygame.K_5:
                    mine = Arc.Minesweeper()
                    mine.countMines()
                    
                # 6 places the first test character at the mouse position
                elif event.key == pygame.K_6:
                    char.x = mouse_x
                    char.y = mouse_y
                # 7 was used for animation testing
                elif event.key == pygame.K_7:
                    cur_bf_anim += 1
                    cur_bf_anim %= 6
                # R saves a temporary file of the currently loaded map
                elif event.key == pygame.K_r:
                    cur_map.save("_temp_save", "Local Save")
                # Minus brings up the snake arcade minigame
                elif event.key == pygame.K_MINUS:
                    if cabinet_pos == (0, 0):
                        cabinet_pos = (0, 256)
                    else:
                        cabinet_pos = (0, 0)
                # Y cycles between logic and visual tiles
                elif event.key == pygame.K_y:
                    cur_map.showVisTiles = not cur_map.showVisTiles
                    if Txt.Debug.editorMapMode == "Logic":
                        Txt.Debug.editorMapMode = "Visual"
                    elif Txt.Debug.editorMapMode == "Visual":
                        Txt.Debug.editorMapMode = "Logic"
                    if cur_map.showVisTiles:
                        sprsh_tileset = Spr.Spritesheet('sprites/tilesets/testtiles2.png', 16, 16)
                    else:
                        sprsh_tileset = Spr.Spritesheet('sprites/tilesets/bgtiles.png', 16, 16)
                
                # Numpad 6 reshuffles the map
                elif event.key == pygame.K_KP_6:
                    last_few_maps.append(copy.deepcopy(cur_map))
                    cur_map.dualLogMapA = [[random.randint(0,2) for _ in range(cur_map.width + 1)] for _ in range(cur_map.height + 1)] 
                # Numpad 9 brings back the previously loaded map
                elif event.key == pygame.K_KP_9:
                    #print(last_few_maps)
                    if len(last_few_maps) > 0:
                        cur_map = last_few_maps.pop()
        # Mousewheel goes between available map tiles to draw with in debug mode
        if event.type == pygame.MOUSEWHEEL:
            if Txt.Debug.map_editor:
                Txt.Debug.map_tile += event.y
        # The window is resizable
        if event.type == pygame.VIDEORESIZE:
            real_screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
        
        # You can command a unit to go towards a clicked position when clicking with left mouse button
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if Txt.Debug.map_editor:
                pass
            else:
                cur_battle.click(((mouse_x + cam_ix) // 16, (mouse_y + cam_iy) // 16), cur_map)
         
        # Makes sure selected debug tiles are within bounds
        if Txt.Debug.editorMapMode == "Visual":
            if cur_map.cur_total_tiles != 0:
                Txt.Debug.map_tile %= cur_map.cur_total_tiles
        elif Txt.Debug.editorMapMode == "Logic":
            if len(Map.Maps.tiles) != 0:
                Txt.Debug.map_tile %= len(Map.Maps.tiles)

    # BG fill
    real_screen.fill((0, 0, 0))
    game_screen.fill(cur_map.bg_color)
    hud_screen.fill((0, 0, 0))
    
    # Render the currently loaded map
    cur_map.render(game_screen, sprsh_tileset, cam_ix, cam_iy, game_width, game_height, frame)
        
    # Drawing tiles to the current map while in debug mode
    if Txt.Debug.map_editor:
        if pygame.mouse.get_pressed()[0]:
            #print(cur_map.dualLogMapA)
            cur_map.set(round((mouse_x + cam_ix) // 16), round((mouse_y + cam_iy) // 16), Txt.Debug.map_tile, Txt.Debug.editorMapMode)
        elif pygame.mouse.get_pressed()[2]:
            if Txt.Debug.editorMapMode == "Logic":
                cur_map.set(round((mouse_x + cam_ix) // 16), round((mouse_y + cam_iy) // 16), -1, Txt.Debug.editorMapMode)
        else:
            spr_selected_tile = sprsh_tileset.get_image(Txt.Debug.map_tile)
            if Txt.Debug.editorMapMode == "Visual":
                if Txt.Debug.map_tile <= len(cur_map.cur_tile_indices):
                    
                    spr_selected_tile = sprsh_tileset.get_image(cur_map.cur_tile_indices[Txt.Debug.map_tile])
            game_screen.blit(spr_selected_tile, spr_selected_tile.get_rect(center=(round((mouse_x - 8 + cam_ix % 16) / 16) * 16 + 8 - cam_ix % 16, round((mouse_y - 8 + cam_iy % 16) / 16) * 16 + 8 - cam_iy % 16)))
            
    else:
        pass
        
    # Left or right shift speeds up the camera and character speeds
    if pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]:
        if game_mode == "battle":
            cam_speed = 4
        elif game_mode == "overworld":
            cam_speed = 2
    else:
        cam_speed = 1


    # WASD input used for character movement in the overworld.
    # Arrow keys are used for camera movement in battles
    input = (cam_speed * (pygame.key.get_pressed()[pygame.K_d] - pygame.key.get_pressed()[pygame.K_a]), cam_speed * (pygame.key.get_pressed()[pygame.K_s] - pygame.key.get_pressed()[pygame.K_w]))
    # Debug camera movement
    if game_mode == "debug":
        if pygame.key.get_pressed()[pygame.K_UP]:
            camera_y -= cam_speed
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            camera_y += cam_speed
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            camera_x -= cam_speed
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            camera_x += cam_speed
    # Overworld camera movement
    elif game_mode == "overworld":
        cur_character = cur_battle.character_list[cur_battle.char_turn]
        camera_x = (camera_x + (input[0] * 24 + cur_character.x - camera_x - game_width / 2) / 20)
        camera_y = (camera_y + (input[1] * 24 + cur_character.y - camera_y - game_height / 2) / 20)
        camera_x = max(0, min(camera_x, cur_map.width * 16 - game_width))
        camera_y = max(0, min(camera_y, cur_map.height * 16 - game_height))
    # Battle camera movement
    elif game_mode == "battle":
        if cam_target != cur_battle.cur_cam_target():
            cam_target = cur_battle.cur_cam_target()
            reached_target = False
        if reached_target == False:
            camera_x = (camera_x + (cam_target[0] - camera_x - game_width / 2) / 20)
            camera_y = (camera_y + (cam_target[1] - camera_y - game_height / 2) / 20)
            if abs((cam_target[0] - camera_x - game_width / 2)) < 1 and abs((cam_target[1] -camera_y - game_height / 2)) < 1:
                camera_x = cam_target[0] - game_width / 2
                camera_y = cam_target[1] - game_height / 2
                reached_target = True
        if pygame.key.get_pressed()[pygame.K_UP]:
            reached_target = True
            camera_y -= cam_speed
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            reached_target = True
            camera_y += cam_speed
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            reached_target = True
            camera_x -= cam_speed
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            reached_target = True
            camera_x += cam_speed
        limited_camera_x = max(0, min(camera_x, cur_map.width * 16 - game_width))
        limited_camera_y = max(0, min(camera_y, cur_map.height * 16 - game_height))
        if limited_camera_x != camera_x and limited_camera_y != camera_y:
            reached_target = True
        if limited_camera_x != camera_x:
            camera_x = limited_camera_x
        if limited_camera_y != camera_y:
            camera_y = limited_camera_y

    # Integer camera values, because sometimes stuff doesn't like floats :(
    cam_ix = math.floor(camera_x)
    cam_iy = math.floor(camera_y)
    
    # Render debug text. ...I feel like it's kinda in the name here
    Txt.Debug.render_debug_text(game_screen)

    # 60 FPS game
    clock.tick(60)
    

    # Debug A* testing
    if path != None and len(path) != 0:
        #print(path)
        char.walk(path, cur_map, cam_speed)
        if (char.x + 0.5) // 16 == path[0][0] and (char.y + 0.5) // 16 == path[0][1]:
            path.pop(0)
        if Txt.Debug.map_editor:
            for i in path:
                #print(i)
                #marker.draw(i["x"] * 16 - camera_x, i["y"] * 16 - camera_y - 16)
                game_screen.blit(pygame.image.load("sprites/characters/placeholderNew.png"), (i[0] * 16 - cam_ix, i[1] * 16 - cam_iy))

    # Battle updates + rendering
    cur_battle.update(cur_map, cam_speed)
    cur_battle.render(game_screen, (cam_ix, cam_iy), frame)

    # Draw the arcade to the game screen
    game_screen.blit(cabinet, cabinet_curPos)
    
    # Draw the test UI to the game screen
    
    spr_hud_bg.draw(0,0,64,240,hud_screen)
    for i in range(9):
        spr_hud_bg.draw(8, 16 + i * 24, 48, 24, hud_screen)

    hud_screen.set_alpha(cur_hud_alpha)
    game_screen.blit(hud_screen, (game_width - cur_hud_x, 0))

    # Draw the game screen to the window
    real_screen.blit(scaled_screen, scaled_screen.get_rect(center=real_screen.get_rect().center))

    # Draw Snake
    if round(cabinet_curPos[1]) == 0:
        snek.update(frame, (pygame.key.get_pressed()[pygame.K_w], pygame.key.get_pressed()[pygame.K_a], pygame.key.get_pressed()[pygame.K_s], pygame.key.get_pressed()[pygame.K_d]))
        snek.draw(mini_snake_screen)
        real_screen.blit(scaled_snake, scaled_snake.get_rect(center=real_screen.get_rect().center))

    #mine.update(frame, {"x": }
    #mine.draw(mini_snake_screen)
    
    
    # Update Display
    pygame.display.flip()