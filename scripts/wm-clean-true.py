#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wm-clean-true.py

Che ngoi sao watermark cua API tren nam tranh true-ending, dung dung
HINH DANG that cua ngoi sao thay vi mat na elip uoc luong.

Vi sao khong dung wm-clean.py: bo true-ending khong co mot nen duy nhat
duoi ngoi sao. true-ending-01/02/03 ngoi sao nam tren le den tron cua
trang truyen, true-ending-04/05 de len chinh phan tranh. Nhan ban ket cau
tren le den keo net ve vao cho trong va lo mang lech mau; lan truyen mau
tren cho co net ve lam nhoe mat duong but.

Vi vay script lam hai viec:

  1. Doc mat na hinh sao that tu scripts/_wm_star_mask.npy (trich tu
     true-ending-03 vi le den tuyet doi, nen hinh sao la toan bo phan
     sang). Ngoi sao la lop phu co dinh cung vi tri tren moi anh nen mot
     mat na dung cho ca nam.
  2. Chon phuong phap theo nen duoi ngoi sao cua tung anh:
       - vanh quanh sao la le den tron (p90 < 12)  -> lan truyen mau,
         chi lay mau tu vung den quanh no, le van la le den.
       - vanh co net ve (p90 >= 12)                -> nhan ban ket cau,
         tim do doi co histogram gan nhat roi dan vao theo mat na.

Ca hai deu dan theo mat na hinh sao nen mep khong hien duong cat.

Chay lan dau can tao mat na: python scripts/_wm_mask.py
Chay: python scripts/wm-clean-true.py [--force-diffuse|--force-clone]
"""

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src' / 'assets' / 'gen'
DST = ROOT / 'src' / 'assets' / 'gen-clean'
MASK_NPY = Path(__file__).parent / '_wm_star_mask.npy'
MASK_BOX = Path(__file__).parent / '_wm_star_box.txt'

# Tam tham chieu cua cua so mat na trong anh goc, doc tu _wm_star_box.txt.
WM_X = 0.930
WM_Y = 0.868


def load_mask():
    """Tra (mat na 0..1, toa do goc trai cua cua so trong anh 1376x768)."""
    mask = np.load(MASK_NPY)
    x0, y0, _ = MASK_BOX.read_text().split()
    return mask, int(x0), int(y0)


def star_stats(im, mask, mx, my):
    """Thong ke vanh quanh ngoi sao, bo chinh vung sao.

    Vanh elip 1.05 < e < 1.9 quanh tam (0.930, 0.868). p90 la chi so quyet
    dinh: le den tron co p90 gan 0, nen co net ve thi p90 vot len xa.
    """
    w, h = im.size
    cx, cy = int(w * WM_X), int(h * WM_Y)
    rx, ry = int(w * 0.040), int(h * 0.052)
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    e = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    band = (e > 1.05) & (e < 1.9)
    v = a[band]
    return float(np.median(v)), float(np.percentile(v, 90))


def diffuse(im, mask, mx, my, iterations=1400):
    """Lan truyen mau trong mat na hinh sao, tren cua so nho quanh no."""
    w, h = im.size
    S = mask.shape[0]
    pad = 60
    x0, y0 = max(0, mx - pad), max(0, my - pad)
    x1, y1 = min(w, mx + S + pad), min(h, my + S + pad)

    win = np.asarray(im.crop((x0, y0, x1, y1)).convert('RGB')).astype(np.float32)
    cw, ch = x1 - x0, y1 - y0

    full = np.zeros((ch, cw), np.float32)
    full[my - y0:my - y0 + S, mx - x0:mx - x0 + S] = mask
    alpha = full[..., None]

    work = win.copy()
    for _ in range(iterations):
        up = np.roll(work, 1, axis=0)
        dn = np.roll(work, -1, axis=0)
        lf = np.roll(work, 1, axis=1)
        rt = np.roll(work, -1, axis=1)
        avg = (up + dn + lf + rt) * 0.25
        work = work * (1 - alpha) + avg * alpha

    out = im.copy()
    out.paste(Image.fromarray(np.clip(work, 0, 255).astype(np.uint8)), (x0, y0))
    return out


def clone(im, mask, mx, my, tries=60):
    """Nhan ban ket cau tu vung lan can, dan vao theo mat na hinh sao."""
    w, h = im.size
    S = mask.shape[0]
    a = np.asarray(im.convert('RGB')).astype(np.float32)

    # Vanh tham chieu: vung quanh cua so sao, bo chinh cua so.
    pad = 55
    ry0, ry1 = max(0, my - pad), min(h, my + S + pad)
    rx0, rx1 = max(0, mx - pad), min(w, mx + S + pad)
    ring = a[ry0:ry1, rx0:rx1]
    hole = np.zeros(ring.shape[:2], bool)
    hole[my - ry0:my - ry0 + S, mx - rx0:mx - rx0 + S] = True
    ring_v = ring[~hole]
    rmean, rstd = ring_v.mean(), ring_v.std()

    best, best_score = None, 1e18
    for i in range(tries):
        ang = 2 * math.pi * i / tries
        dist = 2.2
        dx = int(-math.cos(ang) * dist * S)
        dy = int(-math.sin(ang) * dist * S)
        sx0 = min(max(0, mx + dx), w - S)
        sy0 = min(max(0, my + dy), h - S)
        patch = a[sy0:sy0 + S, sx0:sx0 + S]
        score = abs(patch.mean() - rmean) + 0.9 * abs(patch.std() - rstd)
        if score < best_score:
            best_score = score
            best = (sx0, sy0)

    sx0, sy0 = best
    src = np.asarray(im.crop((sx0, sy0, sx0 + S, sy0 + S)).convert('RGB')).astype(np.float32)
    alpha = mask[..., None]

    a = a.copy()
    a[my:my + S, mx:mx + S] = (
        a[my:my + S, mx:mx + S] * (1 - alpha) + src * alpha
    )
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return out, best_score


def main():
    if not MASK_NPY.exists():
        print('Chua co mat na. Chay scripts/_wm_mask.py truoc.')
        return 1
    mask, mx, my = load_mask()

    DST.mkdir(parents=True, exist_ok=True)
    force = None
    if '--force-diffuse' in sys.argv:
        force = 'diffuse'
    elif '--force-clone' in sys.argv:
        force = 'clone'

    targets = sorted(SRC.glob('true-ending-*.png'))
    if not targets:
        print('khong thay true-ending-*.png trong', SRC)
        return 1

    for p in targets:
        im = Image.open(p).convert('RGB')
        med, p90 = star_stats(im, mask, mx, my)
        flat = p90 < 12.0
        method = force or ('diffuse' if flat else 'clone')
        if method == 'diffuse':
            out = diffuse(im, mask, mx, my)
            note = f'le den tron (med {med:5.1f} p90 {p90:5.1f}) -> lan truyen mau'
        else:
            out, score = clone(im, mask, mx, my)
            note = f'co net ve (med {med:5.1f} p90 {p90:5.1f}) -> nhan ban, lech {score:4.1f}'

        out.save(DST / p.name)
        print(f'{p.stem:16} {im.size[0]}x{im.size[1]}  {note}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
