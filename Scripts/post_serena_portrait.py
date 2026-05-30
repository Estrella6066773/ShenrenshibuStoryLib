"""Post-process generated portrait to reference spec: 177x232, palette, pixel snap."""
from PIL import Image

gen_path = r"C:\Users\C3542\.cursor\projects\d-Unity\assets\CHR-SERENA-DAY-portrait-gen.png"
out_path = (
    r"d:\Unity\神人事部\Docs\设定设计\真相\10-百科\人物\image\CHR-SERENA-DAY"
    r"\CHR-SERENA-DAY-portrait.png"
)
TARGET = (177, 232)

# Reference palette (2125 series)
PALETTE = [
    (56, 56, 55),
    (63, 63, 63),
    (48, 48, 48),
    (61, 59, 60),
    (74, 75, 75),
    (81, 81, 81),
    (86, 85, 81),
    (92, 94, 83),
    (105, 104, 96),
    (115, 114, 102),
    (122, 121, 108),
    (123, 124, 113),
    (127, 127, 120),
    (148, 62, 56),
    (118, 48, 44),
    (76, 124, 146),
    (92, 148, 168),
    (96, 98, 100),
    (78, 80, 82),
    (90, 82, 70),
]


def nearest_color(rgb, palette):
    r, g, b = rgb[:3]
    best = palette[0]
    best_d = 1e9
    for c in palette:
        d = (r - c[0]) ** 2 + (g - c[1]) ** 2 + (b - c[2]) ** 2
        if d < best_d:
            best_d = d
            best = c
    return best


im = Image.open(gen_path).convert("RGB")
gw, gh = im.size
# Center-crop to target aspect (w/h = 177/232)
target_aspect = TARGET[0] / TARGET[1]
current_aspect = gw / gh
if current_aspect > target_aspect:
    new_w = int(gh * target_aspect)
    left = (gw - new_w) // 2
    im = im.crop((left, 0, left + new_w, gh))
else:
    new_h = int(gw / target_aspect)
    top = (gh - new_h) // 2
    im = im.crop((0, top, gw, top + new_h))

im = im.resize(TARGET, Image.NEAREST)

px = im.load()
for y in range(TARGET[1]):
    for x in range(TARGET[0]):
        px[x, y] = nearest_color(px[x, y], PALETTE)

im.save(out_path)
print("saved", out_path, im.size)
