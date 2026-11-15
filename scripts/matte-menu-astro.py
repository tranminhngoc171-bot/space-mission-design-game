#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cắt nền xám của sprite phi hành gia menu thành alpha thật, rồi ghi
ra src/assets/art/char-eva.webp.

Dùng lại matte_background() và trim_watermark() của process-assets.py
để khối xử lý viền (gỡ trộn màu, lấp lỗ bên trong silhouette) không
bị làm lại lần hai với tham số khác.
"""
import importlib.util
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

_spec = importlib.util.spec_from_file_location(
    'pa', ROOT / 'scripts' / 'process-assets.py')
pa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pa)

SRC = ROOT / 'src' / 'assets' / 'gen-sprites' / 'menu-astro.png'
OUT = ROOT / 'src' / 'assets' / 'art' / 'char-eva.webp'


def main():
    im = Image.open(SRC)
    rgba = pa.trim_watermark(pa.matte_background(im))
    box = pa.alpha_bbox(rgba)
    if not box:
        print('tách nền ra rỗng')
        return 1

    # Cắt sát silhouette rồi đệm 8px trong suốt: sprite trong game dùng
    # transform-origin 50% 100% nên chân phải chạm đúng mép dưới.
    rgba = rgba.crop(box)
    w, h = rgba.size
    pad = 8
    canvas = Image.new('RGBA', (w, h + pad * 2), (0, 0, 0, 0))
    canvas.paste(rgba, (0, pad))

    # Cao 1024 là đủ cho màn 4K: sprite hiện ở 62 phần trăm của 2160px
    # là 1340px, nhưng trên màn đó người chơi đã thấy nét ở 1024.
    target_h = 1024
    new_w = max(1, round(canvas.width * (target_h / canvas.height)))
    canvas = canvas.resize((new_w, target_h), Image.LANCZOS)

    canvas.save(OUT, 'WEBP', quality=88, method=6)
    print('ghi', OUT, canvas.size)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
