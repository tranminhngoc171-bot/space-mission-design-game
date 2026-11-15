#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiem tra ky thuat icon sprite: RGBA, 128x128, alpha 4 goc = 0, bbox cach mep >= 6px,
khong co pixel lac ngoai vung vat the.

Chay: python scripts/check-icon-sprite.py [--sheet out.png]
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / 'src' / 'assets' / 'art'

NAMES = [
    'icon-mro-satellite',
    'icon-dsn-dish',
    'icon-uhf-transmitter',
    'icon-hex-packet',
]

MIN_MARGIN = 6


def probe(path):
    im = Image.open(path)
    mode = im.mode
    size = im.size
    rgba = im.convert('RGBA')
    a = np.array(rgba.getchannel('A'))
    corners = [int(a[0, 0]), int(a[0, -1]), int(a[-1, 0]), int(a[-1, -1])]

    ys, xs = np.nonzero(a > 0)
    if len(xs) == 0:
        return dict(mode=mode, size=size, corners=corners, bbox=None,
                    margins=None, islands=0, stray=0, filled=0.0, ok=False)

    x0, x1 = int(xs.min()), int(xs.max()) + 1
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    w, h = size
    margins = dict(left=x0, top=y0, right=w - x1, bottom=h - y1)

    # thanh phan lien thong cua alpha > 0
    from collections import deque
    mask = a > 0
    seen = np.zeros(mask.shape, bool)
    comps = []
    H, W = mask.shape
    for sy in range(H):
        row = mask[sy]
        if not row.any():
            continue
        for sx in np.nonzero(row & ~seen[sy])[0]:
            if seen[sy, sx]:
                continue
            q = deque([(sy, int(sx))])
            seen[sy, sx] = True
            n = 0
            while q:
                y, x = q.popleft()
                n += 1
                for ny, nx in ((y-1, x), (y+1, x), (y, x-1), (y, x+1)):
                    if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        q.append((ny, nx))
            comps.append(n)
    comps.sort(reverse=True)
    islands = len(comps)
    stray = int(sum(comps[1:])) if islands > 1 else 0

    bbox_area = (x1 - x0) * (y1 - y0)
    filled = float((a > 0).sum()) / bbox_area if bbox_area else 0.0

    ok = (
        mode == 'RGBA'
        and size == (128, 128)
        and all(c == 0 for c in corners)
        and min(margins.values()) >= MIN_MARGIN
        and islands == 1
    )
    return dict(mode=mode, size=size, corners=corners, bbox=(x0, y0, x1, y1),
                margins=margins, islands=islands, stray=stray, filled=filled,
                bytes=path.stat().st_size, ok=ok)


def checker_sheet(names, scale=3, pad=10):
    cell = 128 * scale
    cols = 2
    rows = (len(names) + cols - 1) // cols
    W = cols * cell + (cols + 1) * pad
    H = rows * cell + (rows + 1) * pad
    sheet = Image.new('RGB', (W, H), (24, 26, 30))
    arr = np.array(sheet)
    b = 8  # o caro
    for y in range(H):
        for x in range(W):
            v = 90 if ((x // b) + (y // b)) % 2 == 0 else 140
            arr[y, x] = (v, v, v)
    sheet = Image.fromarray(arr)
    for i, n in enumerate(names):
        p = ART / f'{n}.webp'
        im = Image.open(p).convert('RGBA').resize((cell, cell), Image.NEAREST)
        cx = pad + (i % cols) * (cell + pad)
        cy = pad + (i // cols) * (cell + pad)
        sheet.paste(im, (cx, cy), im)
    return sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sheet', default=None)
    args = ap.parse_args()

    report = {}
    for n in NAMES:
        p = ART / f'{n}.webp'
        if not p.exists():
            print(f'{n}: THIEU FILE')
            continue
        r = probe(p)
        report[n] = r
        print(f'{n}')
        print(f'  mode={r["mode"]}  size={r["size"][0]}x{r["size"][1]}  bytes={r["bytes"]}')
        print(f'  alpha 4 goc TL/TR/BL/BR = {r["corners"]}')
        print(f'  bbox={r["bbox"]}  lep trai/tren/phai/duoi={r["margins"]}')
        print(f'  so dao={r["islands"]}  pixel lac={r["stray"]}  do dac={r["filled"]*100:.1f}%')
        print(f'  KET LUAN: {"DAT" if r["ok"] else "KHONG DAT"}')
        print('')

    if args.sheet:
        sh = checker_sheet([n for n in NAMES if (ART / f'{n}.webp').exists()])
        sh.save(args.sheet)
        print(f'sheet: {args.sheet} {sh.size}')

    (ROOT / '.icon-check.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
