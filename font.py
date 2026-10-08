# ELSC Game — draws text with the NES font (assets/sprites/font.png).
# The letters in font.png are white. To get another color we make a tinted
# copy of the sheet once and remember it.

import os

import pygame

import sprites as sprite_loader

# NES colors used for text and the HUD (from the menu mockups).
BLACK = (0x00, 0x00, 0x00)
WHITE = (0xFC, 0xFC, 0xFC)
GRAY = (0xBC, 0xBC, 0xBC)
DARK_GRAY = (0x7C, 0x7C, 0x7C)
YELLOW = (0xF8, 0xB8, 0x00)
RED = (0xF8, 0x38, 0x00)
GREEN = (0x00, 0xA8, 0x00)
GOLD = (0xF8, 0xD8, 0x78)
SKY = (0x3C, 0xBC, 0xFC)
PINK = (0xF8, 0x78, 0xF8)
DARK_RED = (0xA8, 0x10, 0x00)     # shadow under red titles
DARKER_RED = (0x88, 0x14, 0x00)   # shadow under FAILED...
DARK_GREEN = (0x00, 0x58, 0x00)   # shadow under PASSED!
DARK_BROWN = (0x50, 0x30, 0x00)   # inside a tapped cell of the letter grid


class Font:
    def __init__(self):
        info = sprite_loader.read_json("font")
        self.sheet = pygame.image.load(
            os.path.join(sprite_loader.SPRITE_DIR, info["sheet"])).convert_alpha()
        self.glyph_w, self.glyph_h = info["glyph"]   # 5 x 7
        self.advance = info["advance"]               # 6 px from one letter to the next
        self.chars = info["chars"]                   # where each letter sits on the sheet
        self.tinted = {}                             # color -> tinted copy of the sheet

    def sheet_in(self, color):
        if color not in self.tinted:
            copy = self.sheet.copy()
            # white x color = color, transparent stays transparent
            copy.fill(color + (255,), special_flags=pygame.BLEND_RGBA_MULT)
            self.tinted[color] = copy
        return self.tinted[color]

    def width(self, text, scale=1):
        """How wide the text is in pixels."""
        return (len(text) * self.advance - (self.advance - self.glyph_w)) * scale

    def draw(self, surface, text, x, y, color=WHITE, scale=1, center=False, shadow=None):
        """Draw text with its top-left at (x, y). center=True centers it
        across the whole surface (x is then ignored). shadow = a color for a
        drop shadow one big-pixel down and to the right (for titles)."""
        text = text.upper()
        if center:
            x = (surface.get_width() - self.width(text, scale)) // 2
        if shadow is not None:
            self.draw(surface, text, x + scale, y + scale, shadow, scale)

        sheet = self.sheet_in(color)
        small = pygame.Surface((self.width(text), self.glyph_h), pygame.SRCALPHA)
        for i, ch in enumerate(text):
            spot = self.chars.get(ch, self.chars["?"])
            glyph = pygame.Rect(spot["x"], spot["y"], self.glyph_w, self.glyph_h)
            small.blit(sheet, (i * self.advance, 0), glyph)

        if scale != 1:
            # nearest-neighbor, so big letters stay blocky
            small = pygame.transform.scale(small, (small.get_width() * scale,
                                                   small.get_height() * scale))
        surface.blit(small, (x, y))
