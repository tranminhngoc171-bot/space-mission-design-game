"""Build the 5 opening-scene plates for the NASA Space Apps game.

Source plates are NASA public-domain images from images.nasa.gov. Each is
cropped to 16:9, graded toward the game's amber/brown palette, vignetted,
grained and darkened so it sinks into the #07090d page background instead of
glowing like clean stock art.

Run: python scripts/build-scene-plates.py
"""

import math
import os
import random

from PIL import Image, ImageEnhance, ImageFilter

SRC = os.path.join(os.environ["LOCALAPPDATA"], "hermes", "cache", "scratch", "nasasrc")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

TARGET_W, TARGET_H = 1600, 900
TINT = (0x6B, 0x34, 0x13)      # warm brown-orange wash
TINT_ALPHA = 0.30
SATURATION = 0.35              # keep ~35% => ~65% desaturation
BRIGHTNESS = 0.80
CONTRAST = 1.06
VIGNETTE = 0.45
GRAIN = 6
MAX_BYTES = 400_000


def crop_16x9(im, box=None, focus=0.5):
    """Crop to 16:9 then resize. `box` is an explicit (l, t, r, b) pre-crop."""
    im = im.convert("RGB")
    if box:
        im = im.crop(box)
    w, h = im.size
    want = TARGET_W / TARGET_H
    if w / h > want:                       # too wide -> trim the sides
        new_w = int(round(h * want))
        x0 = int(round((w - new_w) * focus))
        im = im.crop((x0, 0, x0 + new_w, h))
    else:                                  # too tall -> trim top/bottom
        new_h = int(round(w / want))
        y0 = int(round((h - new_h) * focus))
        im = im.crop((0, y0, w, y0 + new_h))
    return im.resize((TARGET_W, TARGET_H), Image.LANCZOS)


def vignette_mask(size, strength):
    """White where the frame goes black, black in the middle."""
    sw, sh = max(2, size[0] // 8), max(2, size[1] // 8)
    mask = Image.new("L", (sw, sh))
    px = mask.load()
    cx, cy = (sw - 1) / 2.0, (sh - 1) / 2.0
    max_d = math.hypot(cx, cy)
    for y in range(sh):
        for x in range(sw):
            d = math.hypot(x - cx, y - cy) / max_d
            v = 0.0 if d < 0.45 else (d - 0.45) / 0.55
            px[x, y] = int(round(255 * strength * (v ** 1.6)))
    return mask.resize(size, Image.BICUBIC)


def grain_layer(size, amplitude, seed):
    """Grey-centred noise, spread compressed to roughly +/- amplitude levels."""
    rng = random.Random(seed)
    w, h = size
    noise = Image.new("L", size)
    noise.putdata([rng.randint(0, 255) for _ in range(w * h)])
    noise = noise.filter(ImageFilter.GaussianBlur(0.5))
    return noise.point(lambda v: int(128 + (v - 128) * (amplitude / 64.0)))


def apply_grain(im, amplitude, seed):
    """Add signed grain: lighten where noise > mid, darken where noise < mid."""
    noise = grain_layer(im.size, amplitude, seed)
    light = Image.composite(Image.new("RGB", im.size, (255, 255, 255)), im,
                            noise.point(lambda v: max(0, v - 128) * 2))
    return Image.composite(Image.new("RGB", im.size, (0, 0, 0)), light,
                           noise.point(lambda v: max(0, 128 - v) * 2))


def grade(im, tint=TINT, tint_alpha=TINT_ALPHA, brightness=BRIGHTNESS,
          contrast=CONTRAST, saturation=SATURATION, sharpen=0):
    im = ImageEnhance.Color(im).enhance(saturation)
    if tint_alpha:
        im = Image.blend(im, Image.new("RGB", im.size, tint), tint_alpha)
    im = ImageEnhance.Brightness(im).enhance(brightness)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    if sharpen:
        # low-contrast haze plates lose their ridge line to the grade; a gentle
        # unsharp pass puts the silhouette back without making it look HDR
        im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=sharpen, threshold=2))
    return Image.composite(Image.new("RGB", im.size, (6, 7, 10)), im,
                           vignette_mask(im.size, VIGNETTE))


def build(name, src_file, box=None, focus=0.5, seed=1, **grade_kw):
    im = Image.open(os.path.join(SRC, src_file))
    im = crop_16x9(im, box, focus)
    im = grade(im, **grade_kw)
    im = apply_grain(im, GRAIN, seed)

    os.makedirs(OUT, exist_ok=True)
    dest = os.path.join(OUT, name)
    q = 86
    while True:
        im.save(dest, "JPEG", quality=q, optimize=True, progressive=True)
        size = os.path.getsize(dest)
        if size <= MAX_BYTES or q <= 70:
            break
        q -= 2
    print(f"{name:20s} {im.size[0]}x{im.size[1]}  {size/1024:6.1f} KB  q={q}")
    return dest


SCENES = [
    # 1. surface work scene: two astronauts + rover under a dusty ochre sky
    ("mars-surface.jpg", "PIA24031.jpg", None, 0.5, 11, {}),
    # 2. storm rolling in: Curiosity's Jun 7 2018 view (dust tau ~1.5),
    #    bottom-anchored on the ground band so the ridge + near ground still
    #    read through the haze - "the storm is coming", not "the storm is here"
    ("storm-coming.jpg", "PIA22520.jpg", (40, 828, 40 + 1672, 1808), 0.5, 22,
     {"contrast": 1.7, "brightness": 0.92, "tint_alpha": 0.22, "sharpen": 120}),
    # 3. storm impact: Curiosity's Jun 10 2018 view (tau ~8) bottom-anchored so
    #    the last strip of ground stays in frame - horizon swallowed, not the set
    ("storm-impact.jpg", "PIA22520.jpg", (2240, 808, 2240 + 1778, 1808), 0.5, 33,
     {"brightness": 0.86}),
    # 4. departure: Mars Ascent Vehicle lifting off (NASA artist concept).
    #    Crop from the top so the whole rocket body stays inside the frame.
    ("departure.jpg", "PIA23496.jpg", (0, 0, 1920, 1080), 0.5, 44,
     {"brightness": 0.78}),
    # 5. awake: Buzz Aldrin inside the Apollo 11 LM - real cabin, single hard
    #    window light. Cool tint instead of amber so the cyan halo survives.
    ("awake.jpg", "as11-36-5390.jpg", (0, 362, 1896, 1428), 0.5, 55,
     {"tint": (0x22, 0x2a, 0x33), "tint_alpha": 0.22, "brightness": 0.72,
      "contrast": 1.10, "saturation": 0.40}),
]


if __name__ == "__main__":
    for name, src, box, focus, seed, kw in SCENES:
        build(name, src, box, focus, seed, **kw)
