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

import argparse
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

# Khung truyện tranh của màn mở đầu: cùng khổ 16:9 với ảnh nền nhưng xuất
# WebP chất lượng 82 thay vì JPEG, vì tranh comic có mảng màu lớn và nét
# mực sắc, WebP giữ nét đen tốt hơn JPEG ở cùng dung lượng.
PANEL_QUALITY = 82

# Khung 11 cố ý có dải đen dày hai phía làm mí mắt, không phải lỗi viền.
PANEL_KEEP_BANDS = {'screen-11'}

# ---- sprite trong suốt của màn căn cứ ----
# Ảnh gốc của sprite để ở thư mục riêng, KHÔNG nằm trong gen/: nếu để chung
# thì vòng quét gen/icon-*.png ở main() sẽ đem icon trong suốt đi qua
# process_icon (đệm nền tối đục, vẽ khung chữ nhật) và xoá mất alpha.
SPRITE_SRC = ROOT / 'src' / 'assets' / 'gen-sprites'

# Nhân vật: cao 512px cho tư thế đứng, giữ tỉ lệ người đứng. Chiều rộng suy
# ra từ khung bao silhouette nên ba tư thế cùng tỉ lệ, khác bề ngang tuỳ dáng.
#
# Tư thế NGỒI BÓ GỐI không được ép cao 512 như tư thế đứng: ảnh gốc luôn là
# một nhân vật lấp đầy khung, ép cùng chiều cao thì người ngồi bị phóng to
# gấp rưỡi và đứng cạnh người đứng trông như người khổng lồ. Người ngồi bó
# gối cao khoảng 0.70 lần người đứng, nên đặt riêng chiều cao đích.
CHAR_H = 512
CHAR_H_PER = {
    'char-healthy': 512,
    'char-cold': 505,      # đứng nhưng hơi khom, thấp hơn người đứng thẳng
    'char-tired': 358,     # ngồi bó gối: 0.70 lần tư thế đứng
}
# Chừa 2px trong suốt quanh viền để không pixel nào chạm mép khung.
CHAR_MARGIN = 2
CHAR_QUALITY = 90

# Icon vật phẩm mới dùng đúng đặc tả icon hiện có: 128x128, đệm 8px, vật thể
# chiếm 82 phần trăm khung trong, viền tối 2px bám silhouette.
ICON_FILL = 0.82
OUTLINE_W = 2
OUTLINE_RGB = (10, 14, 20)


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


def _sample_bg(rgb):
    """Màu nền: trung vị của dải viền ngoài cùng. Trung vị chịu được vài
    pixel vật thể lọt ra mép, còn trung bình thì bị kéo lệch."""
    h, w, _ = rgb.shape
    band = max(3, min(w, h) // 40)
    edges = np.concatenate([
        rgb[:band].reshape(-1, 3), rgb[-band:].reshape(-1, 3),
        rgb[:, :band].reshape(-1, 3), rgb[:, -band:].reshape(-1, 3),
    ])
    return np.median(edges, axis=0)


def _components(mask):
    """Nhãn thành phần liên thông 4 hướng, trả list (diện tích, ys, xs)."""
    from collections import deque

    h, w = mask.shape
    seen = np.zeros((h, w), bool)
    out = []
    for sy in range(h):
        if not mask[sy].any():
            continue
        for sx in np.nonzero(mask[sy] & ~seen[sy])[0]:
            if seen[sy, sx]:
                continue
            q = deque([(sy, int(sx))])
            seen[sy, sx] = True
            ys, xs = [], []
            while q:
                y, x = q.popleft()
                ys.append(y)
                xs.append(x)
                for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        q.append((ny, nx))
            out.append((len(ys), np.array(ys), np.array(xs)))
    return out


def matte_background(im, keep_ratio=0.10):
    """Tách nền xám phẳng thành alpha, trả ảnh RGBA.

    Cùng nguyên lý với gen-icon-sprite.py: model không xuất alpha thật nên
    phải xin nền xám phẳng rồi đo khoảng cách màu từng pixel tới màu nền,
    lấy ngưỡng mềm để cạnh không răng cưa.

    Khác một chỗ quan trọng: ở đây giữ MỌI thành phần liên thông đủ lớn chứ
    không chỉ thành phần lớn nhất. Nhân vật đứng có thể bị đứt ở cổ tay hay
    mắt cá do ngưỡng, bỏ phần nhỏ là mất bàn tay. Rác lơ lửng của model
    (chấm sáng, mảnh vụn) thì nhỏ hơn ngưỡng nên vẫn bị loại.
    """
    rgb = np.array(im.convert('RGB')).astype(np.float32)
    h, w, _ = rgb.shape
    bg = _sample_bg(rgb)

    dist = np.sqrt(((rgb - bg) ** 2).sum(axis=2))
    lo, hi = 14.0, 40.0
    alpha = np.clip((dist - lo) / (hi - lo), 0.0, 1.0)

    solid = alpha > 0.5
    comps = _components(solid)
    if comps:
        biggest = max(c[0] for c in comps)
        keep = np.zeros((h, w), bool)
        for n, ys, xs in comps:
            if n >= biggest * keep_ratio:
                keep[ys, xs] = True
        alpha = alpha * keep.astype(np.float32)

    # Lấp lỗ bên trong silhouette: lỗ alpha 0 nằm trong thân (khoảng trống
    # giữa cánh tay và sườn, khe giữa hai chân khi đứng khép) sẽ thành đốm
    # trong suốt nhìn xuyên qua người khi đặt sprite lên nền tối.
    #
    # Phải lấp bằng cách loang từ MÉP ảnh vào chứ không phải giãn mặt nạ ra
    # rồi lấy phần bù: bản trước giãn mặt nạ 46 vòng nên cả vành nền rộng
    # 46px quanh người bị coi là "lỗ bên trong" và bị tô alpha đục, sprite
    # ra một quầng xám hình bóng người. Loang từ mép chỉ chạm tới vùng nền
    # thật sự thông ra ngoài, lỗ kín thì không tới được.
    from collections import deque

    bgmask = alpha < 0.05
    outside = np.zeros((h, w), bool)
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if bgmask[y, x] and not outside[y, x]:
                outside[y, x] = True
                dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if bgmask[y, x] and not outside[y, x]:
                outside[y, x] = True
                dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and bgmask[ny, nx] and not outside[ny, nx]:
                outside[ny, nx] = True
                dq.append((ny, nx))

    holes = bgmask & ~outside
    # Chỉ lấp lỗ NHỎ (vết đứt của ngưỡng, khe hở vài chục pixel). Lỗ lớn là
    # khoảng trống thật giữa cánh tay và sườn, phải để trong suốt; lấp nó
    # thì bóng người thành một khối đặc.
    if holes.any():
        for n, ys, xs in _components(holes):
            if n <= max(64, int(h * w * 0.004)):
                alpha[ys, xs] = 1.0

    # Khử màu nền còn sót ở rìa và trong lỗ: pixel có alpha nhưng màu vẫn
    # gần màu xám nền sẽ hiện thành viền xám khi đặt lên panel tối. Lan màu
    # của pixel vật thể thật vào các pixel đó vài vòng.
    edge = (alpha > 0.05) & (dist < 45)
    if edge.any():
        known = (alpha > 0.05) & ~edge
        col = rgb.copy()
        for _ in range(10):
            if not edge.any():
                break
            acc = np.zeros_like(col)
            cnt = np.zeros((h, w), np.float32)
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ys = slice(max(0, dy), h + min(0, dy))
                xs_ = slice(max(0, dx), w + min(0, dx))
                ys2 = slice(max(0, -dy), h + min(0, -dy))
                xs2 = slice(max(0, -dx), w + min(0, -dx))
                acc[ys, xs_] += col[ys2, xs2] * known[ys2, xs2][..., None]
                cnt[ys, xs_] += known[ys2, xs2]
            fill = edge & (cnt > 0)
            if not fill.any():
                break
            col[fill] = acc[fill] / cnt[fill][:, None]
            known = known | fill
            edge = edge & ~fill
        rgb = col

    arr = np.dstack([rgb, alpha * 255.0]).astype(np.uint8)
    res = Image.fromarray(arr, 'RGBA')
    a = res.getchannel('A').filter(ImageFilter.GaussianBlur(0.6))
    res.putalpha(a)
    return res


def alpha_bbox(im, thresh=24):
    a = np.array(im.getchannel('A'))
    ys, xs = np.nonzero(a > thresh)
    if len(ys) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def process_char(path):
    """Sprite nhân vật: tách nền, cắt sát silhouette, ép chiều cao đích.

    Chiều cao đích lấy theo tên file (CHAR_H_PER), không dùng một con số cho
    cả ba: tư thế ngồi bó gối thấp hơn hẳn tư thế đứng, ép cùng chiều cao
    là biến người ngồi thành người khổng lồ khi đặt cạnh nhau.
    """
    im = Image.open(path)
    rgba = trim_watermark(matte_background(im))
    # trim_watermark cắt mép phải/đáy; trên ảnh RGBA thì nó vẫn chạy được vì
    # find_watermark tự convert sang RGB. Cắt xong mới dò khung bao.

    box = alpha_bbox(rgba)
    if not box:
        raise RuntimeError(f'{path.stem}: tách nền ra rỗng')
    rgba = rgba.crop(box)

    # Đệm 2px trong suốt đều bốn phía: khung bao vừa khít silhouette thì
    # pixel đầu tiên và cuối cùng nằm đúng mép, kiểm alpha ở góc vẫn qua
    # nhưng đặt sprite sát nhau trong game sẽ chạm vào hình bên cạnh.
    w, h = rgba.size
    padded = Image.new('RGBA', (w + CHAR_MARGIN * 2, h + CHAR_MARGIN * 2), (0, 0, 0, 0))
    padded.paste(rgba, (CHAR_MARGIN, CHAR_MARGIN))
    rgba = padded

    w, h = rgba.size
    target_h = CHAR_H_PER.get(path.stem, CHAR_H)
    new_w = max(1, round(w * (target_h / h)))
    rgba = rgba.resize((new_w, target_h), Image.LANCZOS)

    out = OUT / path.name.replace('.png', '.webp')
    rgba.save(out, 'WEBP', quality=CHAR_QUALITY, method=6)
    return out, rgba.size


def process_icon_sprite(path):
    """Icon vật phẩm mới: y hệt đặc tả icon hiện có nhưng nền trong suốt.

    Khác process_icon ở hai điểm: không đệm nền tối (giữ alpha), và viền tối
    2px vẽ bằng cách giãn chính silhouette chứ không vẽ khung chữ nhật quanh
    canvas, vì khung chữ nhật sẽ làm bốn góc hết trong suốt.
    """
    im = Image.open(path)
    rgba = trim_watermark(matte_background(im))

    box = alpha_bbox(rgba)
    if not box:
        raise RuntimeError(f'{path.stem}: tách nền ra rỗng')
    rgba = rgba.crop(box)

    w, h = rgba.size
    side = max(w, h)
    sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    sq.paste(rgba, ((side - w) // 2, (side - h) // 2))

    inner = int((ICON_SIZE - ICON_PAD * 2) * ICON_FILL)
    sq = sq.resize((inner, inner), Image.LANCZOS)

    canvas = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    off = (ICON_SIZE - inner) // 2
    canvas.paste(sq, (off, off))

    a = np.array(canvas.getchannel('A'))
    mask = a > 40
    grown = mask.copy()
    for _ in range(OUTLINE_W):
        g = grown.copy()
        g[1:, :] |= grown[:-1, :]
        g[:-1, :] |= grown[1:, :]
        g[:, 1:] |= grown[:, :-1]
        g[:, :-1] |= grown[:, 1:]
        grown = g
    ring = grown & ~mask
    arr = np.array(canvas)
    arr[ring, 0] = OUTLINE_RGB[0]
    arr[ring, 1] = OUTLINE_RGB[1]
    arr[ring, 2] = OUTLINE_RGB[2]
    arr[ring, 3] = 255
    canvas = Image.fromarray(arr, 'RGBA')

    out = OUT / path.name.replace('.png', '.webp')
    canvas.save(out, 'WEBP', quality=ICON_QUALITY, method=6)
    return out, canvas.size


def fill_letterbox(im, skip=False):
    """Xoá dải đen tuyền ở mép do model tự vẽ thêm.

    Vì sao không cắt bỏ: cắt rồi ép lại 16:9 là phải phóng hoặc cắt bên,
    làm lệch bố cục (khung 12 có Hab sát mép trái, cắt bên là mất Hab).
    Thay vào đó lấp dải đen bằng chính nội dung kế bên lật gương lên, rồi
    làm mờ nhẹ đường nối. Với ảnh bầu trời hoặc đất trơn thì mắt thường
    không thấy mối nối, mà khung hình vẫn nguyên hình học.

    Khung 11 cố ý có dải đen làm mí mắt nên phải bỏ qua, xem skip_names.
    """
    if skip:
        return im

    a = np.array(im.convert('L')).astype(int)
    h, w = a.shape
    rows = a.mean(axis=1)
    cols = a.mean(axis=0)

    def band_len(vals):
        n = 0
        while n < len(vals) and vals[n] < 6:
            n += 1
        return n

    top, bottom = band_len(rows), band_len(rows[::-1])
    left, right = band_len(cols), band_len(cols[::-1])

    # Chỉ coi là dải viền khi nó mỏng (dưới 20 phần trăm chiều cao) và gần
    # đen tuyệt đối. Model hay đóng khung trên lẫn dưới cùng lúc, nên xét
    # riêng từng phía chứ không đòi phía đối diện phải sạch.
    thin = lambda n, total: 8 < n < total * 0.20

    out = im
    if thin(top, h):
        src = out.crop((0, top, w, top + top))
        out = out.copy()
        out.paste(src.transpose(Image.FLIP_TOP_BOTTOM), (0, 0))
    if thin(bottom, h):
        src = out.crop((0, h - 2 * bottom, w, h - bottom))
        out = out.copy()
        out.paste(src.transpose(Image.FLIP_TOP_BOTTOM), (0, h - bottom))
    if thin(left, w):
        src = out.crop((left, 0, left + left, h))
        out = out.copy()
        out.paste(src.transpose(Image.FLIP_LEFT_RIGHT), (0, 0))
    if thin(right, w):
        src = out.crop((w - 2 * right, 0, w - right, h))
        out = out.copy()
        out.paste(src.transpose(Image.FLIP_LEFT_RIGHT), (w - right, 0))

    if out is not im:
        # Làm mờ nhẹ đúng đường nối để mắt không bắt được vệt gương.
        blur = out.filter(ImageFilter.GaussianBlur(6))
        mask = Image.new('L', out.size, 0)
        d = ImageDraw.Draw(mask)
        feather = 10
        for n, box in (
            (top, (0, 0, out.size[0], top + feather)),
            (bottom, (0, out.size[1] - bottom - feather, out.size[0], out.size[1])),
            (left, (0, 0, left + feather, out.size[1])),
            (right, (out.size[0] - right - feather, 0, out.size[0], out.size[1])),
        ):
            if n:
                d.rectangle(box, fill=255)
        out = Image.composite(blur, out, mask)

    return out


def process_panel(path):
    """Khung truyện tranh: cắt về 16:9, xuất WebP chất lượng 82.

    Không dùng chung process_scene vì hàm đó xuất JPEG. Hàm này giữ
    nguyên cách cắt tâm và cách dò watermark để cả bộ ảnh đồng bộ.
    """
    im = Image.open(path).convert('RGB')
    im = fill_letterbox(im, skip=path.stem in PANEL_KEEP_BANDS)
    im = trim_watermark(im)

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
    out = OUT / path.name.replace('.png', '.webp')
    im.save(out, 'WEBP', quality=PANEL_QUALITY, method=6)
    return out, im.size


def main():
    if not SRC.is_dir():
        print(f'Không thấy thư mục ảnh gốc: {SRC}')
        print('Chạy scripts/gen-assets.py --all trước.')
        sys.exit(1)

    ap = argparse.ArgumentParser(description='Chuẩn hoá ảnh sinh ra từ model')
    ap.add_argument(
        '--only', choices=['scenes', 'icons', 'panels', 'chars', 'iconsprite'],
        help='chỉ xử lý một nhóm, mặc định xử lý cả năm',
    )
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)

    all_scenes = sorted(SRC.glob('bg-*.png'))
    all_icons = sorted(SRC.glob('icon-*.png'))
    all_panels = sorted(SRC.glob('screen-*.png'))
    # Sprite nằm ở thư mục riêng, xem SPRITE_SRC. Ảnh popup-* cũng ở đó vì
    # chúng không phải cảnh màn chơi mà là tranh trong hộp thoại.
    all_chars = sorted(SPRITE_SRC.glob('char-*.png')) if SPRITE_SRC.is_dir() else []
    all_iconsprite = sorted(SPRITE_SRC.glob('icon-*.png')) if SPRITE_SRC.is_dir() else []
    all_popups = sorted(SPRITE_SRC.glob('popup-*.png')) if SPRITE_SRC.is_dir() else []

    scenes = [] if args.only not in (None, 'scenes') else all_scenes
    icons = [] if args.only not in (None, 'icons') else all_icons
    panels = [] if args.only not in (None, 'panels') else all_panels
    chars = [] if args.only not in (None, 'chars') else all_chars
    iconsprites = [] if args.only not in (None, 'iconsprite') else all_iconsprite
    # Tranh popup xử lý như khung truyện: 16:9, WebP, cắt tâm. Gộp vào danh
    # sách panel để dùng chung process_panel.
    # Không lọc theo --only panels: popup là bộ art màn căn cứ, chạy riêng
    # sẽ dễ quên. Chỉ bỏ qua khi người dùng đã chỉ định nhóm khác.
    popups = all_popups if args.only in (None, 'panels') else []

    print(f'Xử lý {len(scenes)} ảnh nền, {len(icons)} icon, {len(panels)} khung truyện, '
          f'{len(chars)} sprite nhân vật, {len(iconsprites)} icon sprite, {len(popups)} tranh popup')
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

    for p in panels:
        total_before += p.stat().st_size
        out, size = process_panel(p)
        total_after += out.stat().st_size
        print(f'  {out.name:24} {size[0]}x{size[1]}  {out.stat().st_size // 1024} KB')

    for p in popups:
        total_before += p.stat().st_size
        out, size = process_panel(p)
        total_after += out.stat().st_size
        print(f'  {out.name:24} {size[0]}x{size[1]}  {out.stat().st_size // 1024} KB')

    for p in chars:
        total_before += p.stat().st_size
        out, size = process_char(p)
        total_after += out.stat().st_size
        print(f'  {out.name:24} {size[0]}x{size[1]}  {out.stat().st_size // 1024} KB')

    for p in iconsprites:
        total_before += p.stat().st_size
        out, size = process_icon_sprite(p)
        total_after += out.stat().st_size
        print(f'  {out.name:24} {size[0]}x{size[1]}  {out.stat().st_size // 1024} KB')

    # Ghi manifest để phía web biết chính xác từng file kèm kích thước,
    # khỏi phải mò đường dẫn hay đoán ảnh nào đã xử lý.
    # Quét thẳng thư mục ra thay vì dựa vào danh sách vừa xử lý: khi chạy
    # --only panels thì danh sách cảnh và icon rỗng, ghi theo danh sách sẽ
    # xoá mất phần đã có trong manifest.
    manifest = {
        'generated': __import__('datetime').datetime.now().isoformat(timespec='seconds'),
        'scenes': [],
        'icons': [],
        'panels': [],
        'chars': [],
        'popups': [],
    }

    # Icon do gen-icon-sprite.py ghi vào manifest có thêm cờ 'transparent' và
    # 'note'. Dựng lại danh sách icons từ đĩa sẽ nuốt mất hai trường đó, nên
    # đọc manifest cũ rồi giữ lại phần phụ trợ theo id.
    old_icons = {}
    old_path = OUT / 'asset-manifest.json'
    if old_path.exists():
        try:
            old = __import__('json').loads(old_path.read_text(encoding='utf-8'))
            old_icons = {i.get('id'): i for i in old.get('icons', [])}
        except Exception:
            old_icons = {}

    def entry(path, w, h, extra=None):
        e = {
            'id': path.stem,
            'path': f'assets/art/{path.name}',
            'width': w,
            'height': h,
            'bytes': path.stat().st_size,
        }
        if extra:
            e.update(extra)
        return e

    # Cảnh và icon từng được xuất JPEG ở bản cũ, nay là WebP. Lấy file nào
    # thực sự có trên đĩa, ưu tiên WebP, để manifest không trỏ vào file ma.
    # Nếu cả hai cùng tồn tại thì chỉ ghi WebP, nếu không manifest sẽ có hai
    # mục trùng id cho cùng một cảnh.
    scene_files = {}
    for p in sorted(OUT.glob('bg-*')):
        if p.suffix.lower() not in ('.webp', '.jpg'):
            continue
        cur = scene_files.get(p.stem)
        if cur is None or (p.suffix.lower() == '.webp' and cur.suffix.lower() != '.webp'):
            scene_files[p.stem] = p
    for p in sorted(scene_files.values()):
        manifest['scenes'].append(entry(p, SCENE_W, SCENE_H))
    for p in sorted(OUT.glob('icon-*.webp')):
        prev = old_icons.get(p.stem, {})
        extra = {k: v for k, v in prev.items() if k in ('transparent', 'note')}
        with Image.open(p) as im:
            extra['transparent'] = im.mode == 'RGBA'
        manifest['icons'].append(entry(p, ICON_SIZE, ICON_SIZE, extra))
    for p in sorted(OUT.glob('screen-*.webp')):
        manifest['panels'].append(entry(p, SCENE_W, SCENE_H))
    for p in sorted(OUT.glob('popup-*.webp')):
        manifest['popups'].append(entry(p, SCENE_W, SCENE_H))
    for p in sorted(OUT.glob('char-*.webp')):
        with Image.open(p) as im:
            w, h = im.size
            alpha = im.mode == 'RGBA'
        manifest['chars'].append(entry(p, w, h, {'transparent': alpha}))

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
