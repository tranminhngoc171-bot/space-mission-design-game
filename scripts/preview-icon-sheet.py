#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bang xem truoc icon tren nen caro chat luong cao de soi bang mat/vision.

- Moi icon phong 6x bang LANCZOS (khong dung NEAREST: mep lỏm chom lam
  nguoi xem tuong icon bi rang cua / bi vien sticker).
- Nen caro o lon 32px, hai muc xam sang, de neu con lop nen ban trong suot
  thi o caro se bi mo di ro ret.
- Xuat them 1 ban ghep tren nen tim magenta: neu con quang xam quanh vat
  the thi hien ngay.

Chay: python scripts/preview-icon-sheet.py
"""
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / 'src' / 'assets' / 'art'
OUT = Path(os.environ.get('LOCALAPPDATA', '.')) / 'Temp' / 'iconcheck'

NAMES = [
    'icon-mro-satellite',
    'icon-dsn-dish',
    'icon-uhf-transmitter',
    'icon-hex-packet',
]

SCALE = 6
CELL = 128 * SCALE
PAD = 24
TILE = 32


def checker(w, h, light=(255, 255, 255), dark=(196, 196, 196)):
    im = Image.new('RGB', (w, h), light)
    d = ImageDraw.Draw(im)
    for y in range(0, h, TILE):
        for x in range(0, w, TILE):
            if ((x // TILE) + (y // TILE)) % 2:
                d.rectangle([x, y, x + TILE - 1, y + TILE - 1], fill=dark)
    return im


def sheet(bg_color=None):
    cols, rows = 2, 2
    W = cols * CELL + (cols + 1) * PAD
    H = rows * CELL + (rows + 1) * PAD
    if bg_color is None:
        sheet_im = checker(W, H)
    else:
        sheet_im = Image.new('RGB', (W, H), bg_color)
    for i, n in enumerate(NAMES):
        im = Image.open(ART / f'{n}.webp').convert('RGBA')
        im = im.resize((CELL, CELL), Image.LANCZOS)
        cx = PAD + (i % cols) * (CELL + PAD)
        cy = PAD + (i // cols) * (CELL + PAD)
        sheet_im.paste(im, (cx, cy), im)
    return sheet_im


def single(name, bg_color=None):
    im = Image.open(ART / f'{name}.webp').convert('RGBA')
    im = im.resize((CELL, CELL), Image.LANCZOS)
    if bg_color is None:
        base = checker(CELL, CELL)
    else:
        base = Image.new('RGB', (CELL, CELL), bg_color)
    base.paste(im, (0, 0), im)
    return base


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / 'sheet-v2-caro.png'
    sheet().save(p)
    print(p)
    p = OUT / 'sheet-v2-magenta.png'
    sheet((230, 40, 230)).save(p)
    print(p)
    for n in NAMES:
        p = OUT / f'big-{n}.png'
        single(n).save(p)
        print(p)


if __name__ == '__main__':
    main()
