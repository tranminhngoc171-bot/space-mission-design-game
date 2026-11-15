#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wm-clean-true.py

Che ngoi sao watermark cua API tren nam tranh true-ending.

Khac wm-clean.py o cho: bo true-ending khong co mot nen duy nhat duoi
ngoi sao. Do lai tung anh thi thay hai truong hop:

  - true-ending-01/02/03: ngoi sao nam tren LE DEN TRON cua trang truyen,
    cho le trang de trong khong co net ve.
  - true-ending-04/05: ngoi sao de len chinh phan tranh (nen giay kem,
    mang ao cam, mang gioi o ria tranh).

Nhan ban ket cau nhu wm-clean.py chi dung cho truong hop sau, vi o le den
no se keo net ve vao cho trong va hien ra mot mang lech mau. Lan truyen
mau chi dung cho truong hop truoc, vi o cho co net ve no lam nhoe mat
duong but.

Vi vay script do do lech chuan cua vung quanh ngoi sao de tu chon:
  - std thap  -> nen phang (le den)  -> lan truyen mau
  - std cao   -> co net ve          -> nhan ban ket cau

Ca hai deu dung mat na elip mem nen mep khong hien duong cat.

Chay: python scripts/wm-clean-true.py [--force-diffuse|--force-clone]
"""

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src' / 'assets' / 'gen'
DST = ROOT / 'src' / 'assets' / 'gen-clean'

# Tam watermark theo ti le khung, do tren ca bo anh.
WM_X = 0.930
WM_Y = 0.868
# Ban kinh vung can che theo ti le (rong, cao). Canh ngang ngoi sao dai
# nhat khoang 55px tren 1376px, cong quang mo lay 3.4% va 5.2%.
WM_RX = 0.040
WM_RY = 0.052

# Duoi nguong nay coi la nen phang (le den). Le den that co std gan 0;
# vung co net ve luon vuot xa nguong nay.

def region(im):
    w, h = im.size
    cx, cy = int(w * WM_X), int(h * WM_Y)
    rx, ry = int(w * WM_RX), int(h * WM_RY)
    return cx, cy, rx, ry


def ring_stats(im):
    """Thong ke cua vanh elip quanh watermark, bo chinh vung ngoi sao.

    Dung vanh elip (1.05 < e < 1.9) chu khong dung hinh chu nhat: hinh chu
    nhat quanh goc se an ca mep tranh va bao dong gia. p90 la chi so quyet
    dinh: le den tron co p90 gan 0, con nen co sao hay co net ve thi p90
    vot len rat xa.
    """
    w, h = im.size
    cx, cy, rx, ry = region(im)
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    e = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    band = (e > 1.05) & (e < 1.9)
    v = a[band]
    return float(np.median(v)), float(np.percentile(v, 90))


def diffuse(im, iterations=1400):
    """Lan truyen mau trong mat na: chi lay mau tu vung quanh, khong keo net.

    Chi chay tren cua so nho quanh watermark. Lap 1400 lan tren toan khung
    1376x768 ton vai phut moi anh, trong khi vung can sua chi rong 150px.
    """
    w, h = im.size
    cx, cy, rx, ry = region(im)
    pad = 60
    x0, y0 = max(0, cx - rx - pad), max(0, cy - ry - pad)
    x1, y1 = min(w, cx + rx + pad), min(h, cy + ry + pad)

    win = np.asarray(im.crop((x0, y0, x1, y1)).convert('RGB')).astype(np.float32)
    cw, ch = x1 - x0, y1 - y0
    mask = Image.new('L', (cw, ch), 0)
    ImageDraw.Draw(mask).ellipse((cx - rx - x0, cy - ry - y0,
                                 cx + rx - x0, cy + ry - y0), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(6))
    alpha = np.asarray(mask).astype(np.float32)[..., None] / 255.0

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


def clone(im, feather=9, tries=60):
    """Nhan ban ket cau tu vung lan can, chon do doi co histogram gan nhat.

    Duyet cac do doi theo vong cung quanh vung can che, cham diem bang chenh
    lech trung binh va do lech chuan so voi vanh, roi lay cai khop nhat.
    """
    w, h = im.size
    cx, cy, rx, ry = region(im)
    x0, y0 = max(0, cx - rx), max(0, cy - ry)
    x1, y1 = min(w, cx + rx), min(h, cy + ry)
    bw, bh = x1 - x0, y1 - y0

    a = np.asarray(im.convert('RGB')).astype(np.float32)
    pad = 55
    ry0, ry1 = max(0, cy - ry - pad), min(h, cy + ry + pad)
    rx0, rx1 = max(0, cx - rx - pad), min(w, cx + rx + pad)
    ring = a[ry0:ry1, rx0:rx1]
    ring_mean, ring_std = ring.mean(), ring.std()

    best, best_score = None, 1e18
    for i in range(tries):
        ang = 2 * math.pi * i / tries
        dist = 2.2
        dx = int(-math.cos(ang) * dist * rx)
        dy = int(-math.sin(ang) * dist * ry)
        sx0 = min(max(0, x0 + dx), w - bw)
        sy0 = min(max(0, y0 + dy), h - bh)
        patch = a[sy0:sy0 + bh, sx0:sx0 + bw]
        score = abs(patch.mean() - ring_mean) + 0.9 * abs(patch.std() - ring_std)
        if score < best_score:
            best_score = score
            best = (sx0, sy0)

    sx0, sy0 = best
    src = im.crop((sx0, sy0, sx0 + bw, sy0 + bh))

    mask = Image.new('L', (bw, bh), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((feather, feather, bw - feather, bh - feather), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather))

    out = im.copy()
    out.paste(src, (x0, y0), mask)
    return out, best_score


def main():
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
        med, p90 = ring_stats(im)
        # Vanh la le den tron khi ca trung vi lan p90 deu rat thap. Anh
        # 02 co vanh den (p90 = 1) nen di duong nhan ban cung khong sao,
        # nhung lan truyen moi la dung y do: le den phai la le den.
        flat = p90 < 12.0
        method = force or ('diffuse' if flat else 'clone')
        if method == 'diffuse':
            out = diffuse(im)
            note = f'le den tron (med {med:5.1f} p90 {p90:5.1f}) -> lan truyen mau'
        else:
            out, score = clone(im)
            note = f'co net ve (med {med:5.1f} p90 {p90:5.1f}) -> nhan ban, lech {score:4.1f}'

        out.save(DST / p.name)
        w, h = im.size
        print(f'{p.stem:16} {w}x{h}  {note}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
