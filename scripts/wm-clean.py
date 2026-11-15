#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wm-clean.py

Che watermark ngôi sao của API sinh ảnh trên tám tranh ending bằng cách
nhân bản vùng kết cấu lân cận (texture clone) thay vì làm mờ.

Bước này nằm GIỮA gen-assets.py và process-assets.py:
    gen-assets.py     -> src/assets/gen/*.png      (ảnh gốc, còn watermark)
    wm-clean.py       -> src/assets/gen-clean/*.png (đã che watermark)
    process-assets.py -> src/assets/art/*.webp     (1600x900, đã nén)

Chạy: python scripts/wm-clean.py [--debug]

Vì sao không dùng trim_watermark: hàm đó cắt mất một dải mép ảnh; với
tranh ending dải tối ở đáy bị nhận nhầm là watermark nên cắt vào bố cục
và mất chân nhân vật.

Vì sao không dùng inpaint lan truyền màu: vùng lấp 50 tới 90px trên nền
có vân sần và hạt phim, lan truyền màu cho ra một cục nhoè nhìn thấy
ngay. Nhân bản kết cấu giữ được hạt và vân, chỉ là dời một mảng nhỏ.

Ngôi sao nằm cố định ở khoảng (93.0%, 86.8%) khung, đường kính khoảng
55px trên ảnh rộng 1376px. Lấy mảng nguồn lệch sang trái và lên trên,
rồi trộn theo mặt nạ elip mềm để mép không hiện đường.

Đây là bước chỉ áp cho ảnh ending: ảnh nền và khung truyện cũ đi qua
trim_watermark vì bố cục của chúng chịu được việc cắt dải mép, còn ảnh
ending thì không (xem process_ending trong process-assets.py).
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src' / 'assets' / 'gen'
DST = ROOT / 'src' / 'assets' / 'gen-clean'

# Tâm watermark theo tỉ lệ khung, đo trên cả tám ảnh.
WM_X = 0.930
WM_Y = 0.868
# Bán kính vùng cần che, theo tỉ lệ chiều rộng. Cánh ngang của ngôi sao
# dài nhất, đo được khoảng 55px trên 1376px, cộng quầng mờ lấy 3.4%.
WM_RX = 0.040
WM_RY = 0.052   # theo tỉ lệ chiều cao


def clone_patch(im, dx=-150, dy=-90, feather=9):
    w, h = im.size
    cx, cy = int(w * WM_X), int(h * WM_Y)
    rx, ry = int(w * WM_RX), int(h * WM_RY)

    x0, x1 = max(0, cx - rx), min(w, cx + rx)
    y0, y1 = max(0, cy - ry), min(h, cy + ry)
    box_w, box_h = x1 - x0, y1 - y0

    # vùng nguồn: dời sang trái và lên trên, kẹp trong khung
    sx0 = min(max(0, x0 + dx), w - box_w)
    sy0 = min(max(0, y0 + dy), h - box_h)
    src = im.crop((sx0, sy0, sx0 + box_w, sy0 + box_h))

    # mặt nạ elip mềm: đặc ở giữa, mờ dần ra mép
    mask = Image.new('L', (box_w, box_h), 0)
    d = ImageDraw.Draw(mask)
    pad = feather
    d.ellipse((pad, pad, box_w - pad, box_h - pad), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather))

    out = im.copy()
    out.paste(src, (x0, y0), mask)
    return out


def main():
    DST.mkdir(parents=True, exist_ok=True)
    dbg = '--debug' in sys.argv
    for p in sorted(SRC.glob('ending_*.png')):
        im = Image.open(p).convert('RGB')
        out = clone_patch(im)
        out.save(DST / p.name)
        w, h = im.size
        print(f'{p.stem:22} {w}x{h} cloned at '
              f'({int(w * WM_X)},{int(h * WM_Y)}) r=({int(w * WM_RX)},{int(h * WM_RY)})')
        if dbg:
            cx, cy = int(w * WM_X), int(h * WM_Y)
            r = 90
            crop = out.crop((cx - r, cy - r, cx + r, cy + r))
            crop.resize((r * 4, r * 4), Image.LANCZOS).save(
                DST / ('_chk_' + p.stem + '.png'))


if __name__ == '__main__':
    main()
