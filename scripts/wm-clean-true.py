#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wm-clean-true.py

Che ngoi sao watermark cua API tren nam tranh true-ending bang lan truyen
mau (diffusion inpaint), khong dung nhan ban ket cau nhu wm-clean.py.

Vi sao phai khac wm-clean.py: tren bo true-ending, ngoi sao nam tren LE
DEN TRON cua trang truyen, cho le trang de trong khong co net ve. Nhan
ban mot mang o canh do se keo ca net ve vao le den, hien ra mot mang lech
mau ro rang (da thay dung nhu vay tren true-ending-02, 03 va 04). Lan
truyen mau chi an mau tu vung den quanh no, nen le van la le tron.

Cach lam: mat na elip mem quanh tam ngoi sao, roi lap phep thay moi diem
trong mat na bang trung binh bon diem ke. Lap du lau thi vung trong tro
thanh nghiem ham dieu hoa noi lien bien, tuc chuyen mau muot tu mep vao
giua, khong lo hinh chu nhat. Mat na mem giu mep khong hien duong cat.

Chay: python scripts/wm-clean-true.py
"""

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


def inpaint(im, iterations=900):
    """Lan truyen mau trong mat na elip mem quanh tam watermark."""
    w, h = im.size
    a = np.asarray(im.convert('RGB')).astype(np.float32)

    cx, cy = int(w * WM_X), int(h * WM_Y)
    rx, ry = int(w * WM_RX), int(h * WM_RY)

    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(6))
    alpha = (np.asarray(mask).astype(np.float32) / 255.0)[..., None]

    work = a.copy()
    for _ in range(iterations):
        up = np.roll(work, 1, axis=0)
        dn = np.roll(work, -1, axis=0)
        lf = np.roll(work, 1, axis=1)
        rt = np.roll(work, -1, axis=1)
        avg = (up + dn + lf + rt) * 0.25
        work = work * (1 - alpha) + avg * alpha

    return Image.fromarray(np.clip(work, 0, 255).astype(np.uint8))


def main():
    DST.mkdir(parents=True, exist_ok=True)
    targets = sorted(SRC.glob('true-ending-*.png'))
    if not targets:
        print('khong thay true-ending-*.png trong', SRC)
        return 1
    for p in targets:
        im = Image.open(p).convert('RGB')
        inpaint(im).save(DST / p.name)
        w, h = im.size
        print(f'{p.stem:16} {w}x{h}  inpaint tai '
              f'({int(w * WM_X)},{int(h * WM_Y)}) '
              f'r=({int(w * WM_RX)},{int(h * WM_RY)})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
