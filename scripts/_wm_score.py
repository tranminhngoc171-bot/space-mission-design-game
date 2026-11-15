#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_wm_score.py

Cham diem "con sao hay khong" cho tung phuong phap che, de chon phuong
phap bang so lieu thay vi doan bang mat.

Y tuong: ngoi sao la mot lop phu CO HINH DANG CO DINH (mat na trich tu
true-ending-03). Doi chieu vung nghi ngo voi dung hinh dang do:

    score = trung binh (diem - nen) tren cac diem co mat na
          - trung binh (diem - nen) tren cac diem khong co mat na

Neu sao con thi score lon (cac diem trong hinh sao sang hon han vung
trong). Neu da che sach thi score gan 0. "nen" la trung vi cuc bo, nen
phep do khong bi anh huong boi do sang chung cua buc tranh.

Chay: python scripts/_wm_score.py
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src' / 'assets' / 'gen'
CLEAN = ROOT / 'src' / 'assets' / 'gen-clean'

MASK_NPY = Path(__file__).parent / '_wm_star_mask.npy'
MASK_BOX = Path(__file__).parent / '_wm_star_box.txt'

# Moi truong hop la mot ham bien doi anh. Ngoai "khong che" dung lam moc.
SHIFT = 52      # cua so do rong 52


def star_score(im, mask, mx, my):
    """Chenh sang cua hinh sao so voi nen cuc bo, theo dung hinh dang."""
    w, h = im.size
    pad = 20
    x0, y0 = max(0, mx - pad), max(0, my - pad)
    x1, y1 = min(w, mx + SHIFT + pad), min(h, my + SHIFT + pad)

    crop = im.crop((x0, y0, x1, y1))
    lum = np.asarray(crop.convert('L')).astype(np.float32)
    bg = np.asarray(crop.convert('L').filter(ImageFilter.MedianFilter(31))).astype(np.float32)
    d = lum - bg

    cw, ch = x1 - x0, y1 - y0
    m = np.zeros((ch, cw), np.float32)
    m[my - y0:my - y0 + SHIFT, mx - x0:mx - x0 + SHIFT] = mask

    on = m > 0.55
    off = m < 0.02
    if on.sum() < 20 or off.sum() < 20:
        return float('nan')
    return float(d[on].mean() - d[off].mean())


def main():
    mask = np.load(MASK_NPY)
    x0, y0, _ = MASK_BOX.read_text().split()
    mx, my = int(x0), int(y0)

    print(f'{"anh":18} {"goc":>8} {"da che":>8} {"giam":>8}')
    print('-' * 48)
    for p in sorted(SRC.glob('true-ending-*.png')):
        o = Image.open(p).convert('RGB')
        c_path = CLEAN / p.name
        if not c_path.exists():
            print(f'{p.stem:18} {"?":>8}')
            continue
        c = Image.open(c_path).convert('RGB')

        so = star_score(o, mask, mx, my)
        sc = star_score(c, mask, mx, my)
        drop = 100 * (1 - sc / so) if so > 1e-6 else float('nan')
        print(f'{p.stem:18} {so:8.1f} {sc:8.1f} {drop:7.0f}%')

    print('')
    print('score = chenh sang cua hinh sao so voi nen cuc bo.')
    print('Giam 100% la sach hoan toan; con duoi 60% la con thay.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
