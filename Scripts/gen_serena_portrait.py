# -*- coding: utf-8 -*-
"""Serena portrait from ref 2127 (blocky hair), palette locked to 2125, 177×232."""
from PIL import Image
import os

REF = (
    r"d:\Unity\神人事部\Docs\设定设计\真相\10-百科\人物\image\参考"
    r"\微信图片_20260513160635_2127_1494.png"
)
OUT = (
    r"d:\Unity\神人事部\Docs\设定设计\真相\10-百科\人物\image\CHR-SERENA-DAY"
    r"\CHR-SERENA-DAY-portrait.png"
)

# Locked to reference 2125 series
SKIN = (123, 124, 113)
SKIN_S = (115, 114, 102)
HAIR_HI = (122, 121, 108)
HAIR = (115, 114, 102)
HAIR_SH = (92, 94, 83)
EYE = (48, 48, 48)
EYE_HI = (81, 81, 81)
IRIS = (90, 82, 70)
RED = (148, 62, 56)
RED_SH = (118, 48, 44)
BLUE = (76, 124, 146)
BLUE_HI = (92, 148, 168)
METAL = (96, 98, 100)
METAL_SH = (78, 80, 82)

TARGET = (177, 232)
BANNER_Y = 175

# 2127 brown block tones
BROWN_MID = (103, 98, 92)
BROWN_HI = (120, 122, 108)
BROWN_PALE = (160, 161, 147)
BROWN_DK = (80, 77, 78)
BROWN_SET = {BROWN_MID, BROWN_HI, BROWN_PALE, BROWN_DK, (149, 148, 133), (159, 157, 141), (90, 85, 81)}


def is_banner(r, g, b, y):
    if y < BANNER_Y:
        return False
    if g > 160 and b > 160 and r < 120:
        return True
    if r < 28 and g < 28 and b < 28:
        return True
    return False


def in_face(x, y, w, h):
    """Face oval — keep readable features."""
    cx, cy = w * 0.49, h * 0.36
    return ((x - cx) / 22) ** 2 + ((y - cy) / 20) ** 2 < 1.0


def in_hair_cover(x, y, w):
    """Character left eye: image right; solid bang slab."""
    return x >= w * 0.54 and 62 <= y <= 92


def map_brown(rgb, x, y, w, h):
    if rgb not in BROWN_SET:
        return None
    if in_hair_cover(x, y, w):
        return HAIR_HI if y < 72 else HAIR
    if in_face(x, y, w, h):
        if rgb == BROWN_PALE or rgb == BROWN_HI:
            return SKIN
        return SKIN_S
    # hair / outer mass — two levels only (abstract)
    if rgb in (BROWN_DK, (90, 85, 81)):
        return HAIR_SH
    if rgb == BROWN_PALE or rgb in ((149, 148, 133), (159, 157, 141)):
        return HAIR_HI
    return HAIR


def main():
    img = Image.open(REF).convert("RGB")
    img = img.resize(TARGET, Image.NEAREST)
    w, h = img.size
    px = img.load()

    for y in range(BANNER_Y, h):
        src = 168 + (y - BANNER_Y) % 6
        for x in range(w):
            px[x, y] = px[x, src]
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if is_banner(r, g, b, y):
                px[x, y] = px[x, max(0, y - 1)]

    for y in range(h):
        for x in range(w):
            if y >= BANNER_Y:
                continue
            rgb = px[x, y]
            nc = map_brown(rgb, x, y, w, h)
            if nc:
                px[x, y] = nc

    # Solid cover slab (char left eye) — one flat block + shadow edge
    for y in range(60, 90):
        for x in range(98, w - 8):
            if in_hair_cover(x, y, w):
                px[x, y] = HAIR if x < w - 22 else HAIR_SH

    # Visible right eye (viewer left) — simple block
    for x, y, c in [
        (78, 78, EYE),
        (79, 78, EYE),
        (80, 78, EYE),
        (77, 79, EYE),
        (78, 79, EYE_HI),
        (79, 79, IRIS),
        (80, 79, EYE),
        (81, 79, EYE),
        (78, 80, EYE),
        (79, 80, EYE),
        (80, 80, EYE),
    ]:
        px[x, y] = c

    # Cyber peek
    for x, y, c in [
        (108, 76, RED_SH),
        (109, 76, RED),
        (110, 76, RED),
        (107, 77, RED_SH),
        (108, 77, RED),
        (109, 77, BLUE_HI),
        (110, 77, RED),
        (109, 78, BLUE),
    ]:
        px[x, y] = c

    # Mouth + seams
    my = 92
    for x in range(84, 90):
        px[x, my] = EYE
    px[83, my] = EYE
    px[90, my] = EYE

    def line(x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            px[x0, y0] = c
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    line(83, my, 80, 102, METAL)
    line(90, my, 93, 102, METAL)
    px[86, 103] = METAL_SH
    px[87, 104] = METAL_SH

    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if g > 160 and b > 160 and r < 120:
                px[x, y] = px[x, max(0, y - 1)]

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print("saved", OUT, img.size)


if __name__ == "__main__":
    main()
