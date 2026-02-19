import pygame


class Font:
    characters = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        ".!?,:;'\"-_"
        "0123456789"
        "[]/\\"
        "\uE000\uE001\uE002\uE004\uE003\uE005\uE006\uE008\uE007\uE009\uE00A\uE00B"
        " \uE00C"

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
        ":cRed:": (255,0,0),
        ":cGreen:": (0,255,0),
        ":cBlue:": (0,0,255),
        ":cMagenta:": (255,0,255),
        ":cCyan:": (0,255,255),
        ":cYellow:": (255,255,0),
        ":cWhite:": (255,255,255),
    }
    def __init__(self, image_path, char_w, char_h, chars, cols):
        self.sheet = pygame.image.load("sprites/ui/font/" + image_path).convert_alpha()
        self.char_w = char_w
        self.char_h = char_h
        self.cols = cols
        self.glyphs = {}
        self.color_changes = []

        for i, char_i in enumerate(chars):
            x = i % cols * char_w
            y = i // cols * char_h
            character_image = pygame.Surface((char_w, char_h), pygame.SRCALPHA).convert_alpha()
            character_image.blit(self.sheet, (0, 0), (x, y, char_w, char_h))
            self.glyphs[char_i] = character_image

        self.fallback = self.glyphs.get("?", pygame.Surface((char_w, char_h), pygame.SRCALPHA))

    def create_colored_glyph(self, char, color):
        base = self.glyphs.get(char, self.fallback)
        image = base.copy()
        for xi in range(image.get_width()):
            for yi in range (image.get_height()):
                if image.get_at((xi, yi)) != (0, 0, 0, 0):
                    image.set_at((xi, yi), (color[0], color[1], color[2], round(abs(max(min(image.get_at((xi, yi))[3] * color[3], 255), 0)))))
        return image

    def draw(self, surface, text, x, y, scale=1, color=(255, 255, 255, 255), spacing=-1, linespacing=8):
        self.sheet = pygame.image.load("sprites/ui/font/font.png").convert_alpha()
        cx, cy = x, y
        altered_text = Font.emoji(text)
        altered_text = self.color(altered_text, color[3])
        cur_color = color
        i = 0
        for char in altered_text:
            if len(self.color_changes) != 0 and self.color_changes[0]["index"] == i:
                cur_color = self.color_changes[0]["color"]
                self.color_changes.pop(0)
            if char == "\n":
                cx = x
                cy += (self.ch + linespacing) * scale
                continue
            base = self.glyphs.get(char, self.fallback)
            image = base

            image.set_alpha(color[3])
            if cur_color != (255, 255, 255, 255):
                image = self.create_colored_glyph(char, cur_color)
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
    def color(self, text, opacity):
        for color, rgb in Font.COLORS.items():
            index = text.find(color)
            if index != -1:
                self.color_changes.append({"color": (rgb[0], rgb[1], rgb[2], opacity), "index": index})
            text = text.replace(color, "\uE00C")
        return text
    

class Debug:
    debug_messages = True
    map_editor = False
    map_tile = 0
    debug_message_fade = 60
    editorMapMode = "Visual"

    font = None

    debug_messages_list = [{"text": "", "time": 0, "time_limit": 0}]
    

    @staticmethod
    def __init__():
        Debug.font = Font("font.png", 8, 8, Font.characters, 8)

    def debug_print(text, time=debug_message_fade):
        time = max(1, time)
        if Debug.debug_messages:
            #print(text + " (" + str(time) + ")")
            Debug.debug_messages_list.append({"text": text, "time": 0, "time_limit": time})

    def render_debug_text(screen):
        #print(Debug.debug_messages_list)
        if len(Debug.debug_messages_list) == 0 or Debug.font == None:
            return
        for i in range(len(Debug.debug_messages_list)):
            
            Debug.debug_messages_list[i]["time"] += 1
            Debug.debug_messages_list[i]["time_limit"] = max(1, Debug.debug_messages_list[i]["time_limit"])
            Debug.font.draw(screen, ":right:" + Debug.debug_messages_list[i]["text"], 0, i * 16, 1, (255, 255, 255, 255 - (Debug.debug_messages_list[i]["time"] / Debug.debug_messages_list[i]["time_limit"]) * 255))
            
        for i in range(len(Debug.debug_messages_list) - 1, -1, -1):
            if Debug.debug_messages_list[i]["time"] > Debug.debug_messages_list[i]["time_limit"]:
                del Debug.debug_messages_list[i]
                break