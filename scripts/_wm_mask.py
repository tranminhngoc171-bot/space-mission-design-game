#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_wm_mask.py

Trich hinh dang that cua ngoi sao watermark tu true-ending-03 (nen le den
tuyet doi, nen ngoi sao chinh la toan bo phan sang) roi luu thanh mat na
alpha de dung lai cho ca nam anh.

Vi sao: ngoi sao la mot lop phu co dinh, cung hinh dang, cung vi tri tren
moi anh. Dat mat na elip uoc luong thi luon hoac thieu (con lai canh sao)
hoac thua (xoa lan sang net ve). Lay dung hinh dang that thi vua khit.
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / 'src' / 'assets' / 'gen' / 'true-ending-03.png'
OUT = Path(__file__).parent / '_wm_star_mask.npy'
META = Path(__file__).parent / '_wm_star_box.txt'

WM_X = 0.930
WM_Y = 0.868


def main():
    im = Image.open(REF).convert('RGB')
    w, h = im.size
    cx, cy = int(w * WM_X), int(h * WM_Y)

    # Cua so 50x50 quanh tam; do lech tam that do duoc la (-0.5, +4.5).
    S = 52
    x0, y0 = cx - S // 2, cy - S // 2 + 4
    crop = im.crop((x0, y0, x0 + S, y0 + S))

    a = np.asarray(crop).astype(np.float32).mean(axis=2)
    # Le den tuyet doi co gia tri ~1; ngoi sao mau xam. Nguong 8 bat tron
    # ca phan quang mo cua canh sao ma khong bat nhieu nen.
    mask = (a > 8).astype(np.float32)

    # Gian ra 1px de phu ca vien chong rang cua, roi lam mem 1px cho mep
    # khong hien duong cat.
    m = Image.fromarray((mask * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MaxFilter(3))
    m = m.filter(ImageFilter.GaussianBlur(1.2))
    mask = np.asarray(m).astype(np.float32) / 255.0

    ys, xs = np.where(mask > 0.02)
    print(f'hinh sao: {len(xs)} diem, rong {xs.max()-xs.min()+1}, cao {ys.max()-ys.min()+1}')
    print(f'cua so dat tai ({x0},{y0}), kich thuoc {S}')
    print(f'nen trong cua so: trung vi {np.median(a):.1f}, p99 {np.percentile(a,99):.1f}')

    np.save(OUT, mask)
    META.write_text(f'{x0} {y0} {S}\n', encoding='utf-8')
    print('ghi', OUT)
    return 0


if __name__ == '__main__':
    sys.exit(main())
