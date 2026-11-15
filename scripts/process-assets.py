#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
process-assets.py
Chuẩn hoá ảnh sinh ra từ model: cắt viền thừa, cắt watermark, đổi
kích thước, nén lại cho nhẹ.

Vì sao cần bước này: model trả ảnh kích thước lung tung (có cái
1376x768, có cái vuông), và hay chèn watermark nhỏ ở góc dưới phải.
Đem nguyên vào game thì icon to nhỏ khác nhau, watermark hiện lên
màn hình, và tổng dung lượng phình to.

Chạy: python scripts/process-assets.py
"""

import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src' / 'assets' / 'gen'
OUT = ROOT / 'src' / 'assets' / 'art'

# Ảnh nền: 16:9, không cần trong suốt
SCENE_W, SCENE_H = 1600, 900
SCENE_QUALITY = 82

# Icon: vuông, có nền trong suốt
ICON_SIZE = 256
ICON_QUALITY = 88


def find_watermark_box(im):
    """Khoanh vùng góc dưới phải để cắt bỏ watermark.

    Model hay đặt watermark trong khoảng 8 phần trăm cạnh ngắn nhất
    ở góc dưới phải. Cắt thẳng vùng đó rẻ hơn và chắc hơn là dò
    theo mẫu, vì watermark mỗi ảnh một kiểu.
    """
    w, h = im.size
    pad = int(min(w, h) * 0.10)
    return (w - pad, h - pad, w, h)


def trim_watermark(im):
    """Xoá watermark bằng cách làm mờ vùng góc, giữ nguyên khung hình.

    Không cắt bỏ hẳn vì sẽ lệch bố cục. Thay vào đó lấy mẫu màu quanh
    vùng đó rồi tô đè, khiến watermark biến mất mà nền vẫn liền.
    """
    w, h = im.size
    box = find_watermark_box(im)
    region = im.crop(box)

    # màu trung bình của vùng rìa ngoài watermark
    small = region.resize((1, 1), Image.LANCZOS)
    fill = small.getpixel((0, 0))

    patch = Image.new('RGB', region.size, fill[:3])
    patch = patch.filter(ImageFilter.GaussianBlur(region.size[0] / 6))

    mask = Image.new('L', region.size, 0)
    d = ImageDraw.Draw(mask)
    # chỉ tô đậm dần vào góc, mép ngoài để nguyên
    md = int(min(region.size) * 0.45)
    d.ellipse([region.size[0] - md, region.size[1] - md,
               region.size[0] + md, region.size[1] + md], fill=210)
    mask = mask.filter(ImageFilter.GaussianBlur(md / 3))

    im.paste(patch, box, mask)
    return im


def process_scene(path):
    """Ảnh nền: cắt về 16:9, làm mờ watermark, nén."""
    im = Image.open(path).convert('RGB')
    im = trim_watermark(im)

    # cắt về tỉ lệ 16:9 quanh tâm
    w, h = im.size
    target = SCENE_W / SCENE_H
    if w / h > target:
        new_w = int(h * target)
        left = (w - new_w) // 2
        im = im.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target)
        top = (h - new_h) // 2
        im = im.crop((0, top, w, top + new_h))

    im = im.resize((SCENE_W, SCENE_H), Image.LANCZOS)
    out = OUT / path.name.replace('.png', '.jpg')
    im.save(out, 'JPEG', quality=SCENE_QUALITY, optimize=True, progressive=True)
    return out, im.size


def process_icon(path):
    """Icon: cắt về vuông, tách nền tối, phóng về 256, nén."""
    im = Image.open(path).convert('RGB')

    # cắt về vuông quanh tâm
    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    im = im.crop((left, top, left + side, top + side))

    im = trim_watermark(im)
    im = im.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)

    # Nền icon vốn đã tối, giữ nguyên thay vì tách nền: icon hiển thị
    # trong khung tối của game nên nền tối hoà vào, không cần alpha.
    # Tách nền tự động trên ảnh sinh ra hay ăn thủng chi tiết bóng.
    out = OUT / path.name.replace('.png', '.webp')
    im.save(out, 'WEBP', quality=ICON_QUALITY, method=6)
    return out, im.size


def main():
    if not SRC.is_dir():
        print(f'Không thấy thư mục ảnh gốc: {SRC}')
        print('Chạy scripts/gen-assets.py --all trước.')
        sys.exit(1)

    OUT.mkdir(parents=True, exist_ok=True)

    scenes = sorted(SRC.glob('bg-*.png'))
    icons = sorted(SRC.glob('icon-*.png'))

    print(f'Xử lý {len(scenes)} ảnh nền và {len(icons)} icon')
    print('')

    total_before = 0
    total_after = 0

    for p in scenes:
        total_before += p.stat().st_size
        out, size = process_scene(p)
        total_after += out.stat().st_size
        print(f'  {out.name:24} {size[0]}x{size[1]}  {out.stat().st_size // 1024} KB')

    for p in icons:
        total_before += p.stat().st_size
        out, size = process_icon(p)
        total_after += out.stat().st_size
        print(f'  {out.name:24} {size[0]}x{size[1]}  {out.stat().st_size // 1024} KB')

    print('')
    print(f'Trước: {total_before // 1024} KB')
    print(f'Sau:   {total_after // 1024} KB')
    if total_before:
        print(f'Giảm:  {100 - total_after * 100 // total_before} phần trăm')
    print(f'Ra:    {OUT}')


if __name__ == '__main__':
    main()
