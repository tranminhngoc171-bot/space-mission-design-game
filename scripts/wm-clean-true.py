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
from PIL import Image, ImageFilter

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


def clone(im, mask, mx, my, tries=60, feather=4.0):
    """Nhan ban ket cau tu vung lan can, dan vao theo mat na hinh sao.

    feather la do mo cua mat na khi dan: mo nhieu thi mep khong hien
    duong cat (dung cho nen co net but), mo it thi giu net sac (nen den).
    """
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
    # Mat na khi dan: gian ra truoc roi moi lam mo. Chi lam mo mot mat na
    # vua khi thi phan canh sao sat mep chi duoc phu mot nua va con nhin
    # thay; gian 3px roi moi mo 4px thi loi van dac va mep van mem.
    binm = (mask > 0.30).astype(np.uint8) * 255
    soft = Image.fromarray(binm)
    if feather > 0:
        soft = soft.filter(ImageFilter.MaxFilter(7))
        soft = soft.filter(ImageFilter.GaussianBlur(feather))
    alpha = np.asarray(soft).astype(np.float32)[..., None] / 255.0

    a = a.copy()
    a[my:my + S, mx:mx + S] = (
        a[my:my + S, mx:mx + S] * (1 - alpha) + src * alpha
    )
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return out, best_score



def residual_score(im, mask, mx, my):
    """Do xem con sao hay khong: chenh sang cua hinh sao so voi nen cuc bo.

    Ngoi sao la lop phu co hinh dang co dinh (mat na tu _wm_mask.py). Neu
    con sao thi cac diem trong hinh sao sang hon han vung trong quanh no.
    Dung trung vi cuc bo lam nen nen phep do khong phu thuoc do sang chung
    cua buc tranh.
    """
    w, h = im.size
    S = mask.shape[0]
    pad = 20
    x0, y0 = max(0, mx - pad), max(0, my - pad)
    x1, y1 = min(w, mx + S + pad), min(h, my + S + pad)

    crop = im.crop((x0, y0, x1, y1)).convert('L')
    lum = np.asarray(crop).astype(np.float32)
    bg = np.asarray(crop.filter(ImageFilter.MedianFilter(31))).astype(np.float32)
    d = lum - bg

    cw, ch = x1 - x0, y1 - y0
    m = np.zeros((ch, cw), np.float32)
    m[my - y0:my - y0 + S, mx - x0:mx - x0 + S] = mask

    on, off = m > 0.55, m < 0.02
    if on.sum() < 20 or off.sum() < 20:
        return float('nan')
    return abs(float(d[on].mean() - d[off].mean()))


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
        before = residual_score(im, mask, mx, my)

        # Thu hai phep che roi chon cai de lai it dau vet sao nhat. Khong
        # doan theo loai nen: true-ending-01 nam tren troi sao (nen khong
        # phang nhung cung khong co net but) va chi lan truyen moi sach,
        # trong khi 04 nam tren mang giap co net va chi nhan ban moi giu
        # duoc net. Chon bang so lieu thi khong phai doan.
        cands = []
        if force in (None, 'diffuse'):
            cands.append(('lan truyen', diffuse(im, mask, mx, my)))
        if force in (None, 'clone'):
            cands.append(('nhan ban', clone(im, mask, mx, my)[0]))

        scored = [(residual_score(o, mask, mx, my), name, o) for name, o in cands]
        scored.sort(key=lambda t: t[0])
        after, name, out = scored[0]

        out.save(DST / p.name)
        detail = ', '.join(f'{n} {s:.1f}' for s, n, _ in scored)
        print(f'{p.stem:16} {im.size[0]}x{im.size[1]}  '
              f'truoc {before:5.1f} -> sau {after:4.1f}  dung: {name}  [{detail}]')

    return 0


if __name__ == '__main__':
    sys.exit(main())
