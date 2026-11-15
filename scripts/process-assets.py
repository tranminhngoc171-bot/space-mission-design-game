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

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src' / 'assets' / 'gen'
OUT = ROOT / 'src' / 'assets' / 'art'

# Ảnh nền: 16:9, không cần trong suốt
SCENE_W, SCENE_H = 1600, 900
SCENE_QUALITY = 82

# Icon: vuông 128x128 đúng đặc tả, chừa 8px đệm quanh vật thể để
# viền tối 2px không bị cắt khi icon hiển thị trong khung nhỏ.
ICON_SIZE = 128
ICON_PAD = 8
ICON_QUALITY = 88


def find_watermark(im, search_ratio=0.22):
    """Dò watermark ngôi sao ở góc dưới phải.

    Vì sao phải dò thay vì cắt cứng một vùng: model đặt watermark ở
    khoảng cách khác nhau tuỳ ảnh (đo thật thấy tâm cách mép phải 7
    phần trăm và cách đáy 13 phần trăm, chứ không sát góc), và kích
    thước cũng đổi. Cắt cứng 10 phần trăm như bản trước để lại dấu.

    Cách dò: watermark gần như trắng xám nên độ bão hoà rất thấp,
    trong khi cảnh Sao Hỏa thì nâu cam bão hoà cao. Tìm cụm pixel
    sáng và ít màu trong góc dưới phải rồi lấy khung bao của cụm lớn
    nhất. Không thấy gì thì trả None, và ảnh giữ nguyên.
    """
    a = np.array(im.convert('RGB')).astype(int)
    h, w, _ = a.shape
    lum = a.mean(axis=2)
    sat = a.max(axis=2) - a.min(axis=2)

    region = np.zeros((h, w), bool)
    region[int(h * (1 - search_ratio)):, int(w * (1 - search_ratio)):] = True

    cand = region & (lum > 52) & (sat < 30)
    ys, xs = np.nonzero(cand)
    if len(ys) < 40:
        return None

    # cụm thật thường nằm gần nhau; lấy vùng bao quanh trung vị để
    # loại pixel sáng lẻ tẻ của chi tiết cảnh
    cx, cy = int(np.median(xs)), int(np.median(ys))
    keep = (np.abs(xs - cx) < w * 0.13) & (np.abs(ys - cy) < h * 0.20)
    xs, ys = xs[keep], ys[keep]
    if len(xs) < 30:
        return None

    # nới rộng thêm 40 phần trăm kích thước cụm để phủ hết phần mờ
    # toả ra quanh ngôi sao
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    pad = int(max(x1 - x0, y1 - y0) * 0.55)
    return (
        max(0, x0 - pad), max(0, y0 - pad),
        min(w, x1 + pad), min(h, y1 + pad),
    )


def sample_background(im, box):
    """Lấy màu nền đại diện cho vùng cần che.

    Không lấy trung bình cả vùng, vì vùng đó có thể chứa cả vật thể
    sáng lẫn nền tối. Thay vào đó lấy một dải ngay trên và bên trái
    watermark, nơi gần như chắc chắn chỉ có nền.
    """
    x0, y0, x1, y1 = box
    w, h = im.size
    strip_top = im.crop((max(0, x0 - 10), max(0, y0 - 26), x1, max(1, y0 - 8)))
    strip_left = im.crop((max(0, x0 - 26), max(0, y0 - 10), max(1, x0 - 8), y1))
    samples = []
    for strip in (strip_top, strip_left):
        if strip.size[0] > 0 and strip.size[1] > 0:
            samples.append(strip.resize((1, 1), Image.LANCZOS).getpixel((0, 0)))
    if not samples:
        return (10, 14, 20)
    r = sum(c[0] for c in samples) // len(samples)
    g = sum(c[1] for c in samples) // len(samples)
    b = sum(c[2] for c in samples) // len(samples)
    return (r, g, b)


def trim_watermark(im):
    """Bỏ dải chứa watermark bằng cách cắt mép, rồi để bước sau phóng lại.

    Đã thử ba cách tô đè và cả ba đều để lại dấu: tô màu phẳng làm mất
    độ sần, trừ nền cục bộ để sót phần mờ, lọc trung vị không xoá hết
    ngôi sao cỡ 50px. Watermark bán trong suốt nằm đè lên chi tiết nên
    không có cách nào khôi phục đúng chi tiết bên dưới.

    Cắt mép là cách sạch nhất: watermark nằm trong 6 phần trăm ngoài
    cùng của ảnh, cắt bỏ dải đó không mất chi tiết kể chuyện nào, và
    bước phóng về 16:9 phía sau lo phần bù kích thước. Không có vết
    can thiệp nào để nhìn ra.
    """
    box = find_watermark(im)
    if not box:
        return im

    x0, y0, _, _ = box
    w, h = im.size

    # cắt bỏ đúng phần từ mép trái của khung watermark tới mép phải,
    # và từ mép trên khung watermark tới mép dưới
    cut_w = max(0, w - x0)
    cut_h = max(0, h - y0)

    # giới hạn: không cắt quá 12 phần trăm mỗi chiều, nếu không ảnh
    # mất bố cục và phóng lên sẽ vỡ nét
    cut_w = min(cut_w, int(w * 0.12))
    cut_h = min(cut_h, int(h * 0.14))

    if cut_w < 4 and cut_h < 4:
        return im

    return im.crop((0, 0, w - cut_w, h - cut_h))


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


def content_bbox(im, thresh_ratio=0.55):
    """Tìm khung bao của vật thể dựa trên độ sáng.

    Nền ảnh là gradient tối, vật phẩm sáng hơn hẳn, nên lấy mức sáng
    trung bình của ảnh rồi coi pixel sáng hơn ngưỡng là vật thể. Cách
    này chịu được nền gradient, khác với getbbox() chỉ ăn với nền
    trong suốt.
    """
    grey = im.convert('L')
    # mức sáng nền: lấy trung bình bốn góc, vì vật thể gần như không
    # bao giờ chạm cả bốn góc cùng lúc
    w, h = grey.size
    corners = [
        grey.getpixel((2, 2)), grey.getpixel((w - 3, 2)),
        grey.getpixel((2, h - 3)), grey.getpixel((w - 3, h - 3)),
    ]
    bg = sum(corners) / 4.0
    thresh = bg + (255 - bg) * thresh_ratio

    mask = grey.point(lambda v: 255 if v > thresh else 0)
    bbox = mask.getbbox()
    return bbox


def process_icon(path):
    """Icon: cắt sát vật thể, canh giữa, đệm 8px, viền tối 2px, 128x128.

    Đặc tả đòi viền ngoài đậm để nhìn lướt là nhận ra vật phẩm, và
    đệm đều quanh vật thể để icon không bị cắt khi hiển thị trong ô
    nhỏ. Viền vẽ sau khi thu nhỏ nên nét luôn đúng 2px.
    """
    im = Image.open(path).convert('RGB')
    im = trim_watermark(im)

    # Cắt sát vật thể rồi canh giữa lại. Nếu dò không ra khung bao
    # (ảnh quá tối hoặc vật thể chạm cả bốn cạnh) thì lùi về cắt
    # vuông quanh tâm như cũ.
    bbox = content_bbox(im)
    if bbox:
        x0, y0, x1, y1 = bbox
        # nới thêm 6 phần trăm mỗi phía để không cắt sát mép vật thể
        pad_x = int((x1 - x0) * 0.06)
        pad_y = int((y1 - y0) * 0.06)
        x0 = max(0, x0 - pad_x)
        y0 = max(0, y0 - pad_y)
        x1 = min(im.size[0], x1 + pad_x)
        y1 = min(im.size[1], y1 + pad_y)
        im = im.crop((x0, y0, x1, y1))

    # đưa về vuông bằng cách đệm nền tối ở cạnh ngắn hơn, giữ nguyên
    # tỉ lệ vật thể
    w, h = im.size
    side = max(w, h)
    square = Image.new('RGB', (side, side), (18, 24, 32))
    square.paste(im, ((side - w) // 2, (side - h) // 2))
    im = square

    # Vật thể chỉ chiếm 82 phần trăm khung, phần còn lại là đệm.
    # Nếu cho nó lấp đầy thì đệm dọc gần như bằng không, icon chạm
    # sát mép và trông như bị cắt dù không mất chi tiết nào.
    inner = int((ICON_SIZE - ICON_PAD * 2) * 0.82)
    im = im.resize((inner, inner), Image.LANCZOS)

    canvas = Image.new('RGB', (ICON_SIZE, ICON_SIZE), (18, 24, 32))
    off = (ICON_SIZE - inner) // 2
    canvas.paste(im, (off, off))

    draw = ImageDraw.Draw(canvas)
    draw.rectangle(
        [0, 0, ICON_SIZE - 1, ICON_SIZE - 1],
        outline=(10, 14, 20),
        width=2,
    )

    out = OUT / path.name.replace('.png', '.webp')
    canvas.save(out, 'WEBP', quality=ICON_QUALITY, method=6)
    return out, canvas.size


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

    # Ghi manifest để phía web biết chính xác từng file kèm kích thước,
    # khỏi phải mò đường dẫn hay đoán ảnh nào đã xử lý.
    manifest = {
        'generated': __import__('datetime').datetime.now().isoformat(timespec='seconds'),
        'scenes': [],
        'icons': [],
    }
    for p in scenes:
        out = OUT / p.name.replace('.png', '.jpg')
        if out.exists():
            manifest['scenes'].append({
                'id': out.stem,
                'path': f'assets/art/{out.name}',
                'width': SCENE_W,
                'height': SCENE_H,
                'bytes': out.stat().st_size,
            })
    for p in icons:
        out = OUT / p.name.replace('.png', '.webp')
        if out.exists():
            manifest['icons'].append({
                'id': out.stem,
                'path': f'assets/art/{out.name}',
                'width': ICON_SIZE,
                'height': ICON_SIZE,
                'bytes': out.stat().st_size,
            })

    manifest_path = OUT / 'asset-manifest.json'
    manifest_path.write_text(
        __import__('json').dumps(manifest, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print('')
    print(f'Manifest: {manifest_path}')

    print('')
    print(f'Trước: {total_before // 1024} KB')
    print(f'Sau:   {total_after // 1024} KB')
    if total_before:
        print(f'Giảm:  {100 - total_after * 100 // total_before} phần trăm')
    print(f'Ra:    {OUT}')


if __name__ == '__main__':
    main()
