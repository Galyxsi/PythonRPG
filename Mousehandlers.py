import Spritehandlers as Spr

class Mouse:
    

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Mouse, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.state = "Default"
        if not hasattr(self, 'mouse_spr'):
            self.mouse_spr = Spr.AdvancedSpritesheet("ui/gui/cursor.png")

    def set_sprite(self, sprite: Spr.AdvancedSpritesheet):
        self.mouse_spr = sprite
    def render(self, surface, mouse_pos: list):
        surface.blit(self.mouse_spr.animation(self.state, 0), [mouse_pos[0] - self.mouse_spr.anim_offsets(self.state, 0)[0], mouse_pos[1] - self.mouse_spr.anim_offsets(self.state, 0)[1]])