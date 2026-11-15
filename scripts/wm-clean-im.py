#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wm-clean-im.py

Che watermark ngoi sao o goc duoi phai cho bay khung chuyen tiep
bg-im-01 .. bg-im-07.

Vi sao khong dung trim_watermark cua process-assets.py: ham do cat han mot
dai 12 phan tram mep phai va 14 phan tram mep duoi. Voi tranh chia hai o
ngang thi dai do an mat phan lon o ben phai, hong bo cuc. Ngoi sao chi rong
khoang 60px nen nhan ban ket cua vung lan can la du.

Vi sao khong dung wm-clean.py: file do chi quet ending_*.png.

Meo quan trong: ngoi sao co bon canh, canh tren vuon cao hon tam nhieu.
Lan dau dat hop qua nho va dung mat na elip nen dau tren cua sao song sot.
Do lai khung bao that: x 1250..1310, y 612..695 tren anh 1376x768. Hop che
vi vay phai phu ca y 577..733, va mat na phai la hinh chu nhat lam mo mep
chu khong phai elip, neu khong bon dau sao lo ra ngoai duong elip.

Chay: python scripts/wm-clean-im.py [--debug]
Ghi de len src/assets/gen/bg-im-0N.png, ban goc luu o gen-wm-orig/.
"""

import shutil
import sys
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src' / 'assets' / 'gen'
BAK = ROOT / 'src' / 'assets' / 'gen-wm-orig'

NAMES = [f'bg-im-{i:02d}.png' for i in range(1, 8)]

# Tam ngoi sao va nua kich thuoc hop che. Do tren anh goc: khung bao sao
# la x 1250..1310, y 612..695; cong them le de phu quang mo.
WM_CX = 1280
WM_CY = 655
WM_HW = 85
WM_HH = 78


def clone_patch(im, dx=-180, dy=-150, feather=16):
    w, h = im.size
    x0, x1 = max(0, WM_CX - WM_HW), min(w, WM_CX + WM_HW)
    y0, y1 = max(0, WM_CY - WM_HH), min(h, WM_CY + WM_HH)
    box_w, box_h = x1 - x0, y1 - y0

    sx0 = min(max(0, x0 + dx), w - box_w)
    sy0 = min(max(0, y0 + dy), h - box_h)
    src = im.crop((sx0, sy0, sx0 + box_w, sy0 + box_h))

    # Mat na hinh chu nhat lam mo deu bon mep. Dung elip thi bon dau sao
    # nam ngoai duong elip va van hien ra.
    mask = Image.new('L', (box_w, box_h), 255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather))

    out = im.copy()
    out.paste(src, (x0, y0), mask)
    return out


def main():
    dbg = '--debug' in sys.argv
    BAK.mkdir(parents=True, exist_ok=True)

    for name in NAMES:
        p = SRC / name
        if not p.exists():
            print(f'  {name:16} thieu, bo qua')
            continue
        bak = BAK / name
        if not bak.exists():
            shutil.copy2(p, bak)
        im = Image.open(bak).convert('RGB')
        out = clone_patch(im)
        out.save(p)
        w, h = im.size
        print(f'  {name:16} {w}x{h} che hop {WM_HW * 2}x{WM_HH * 2} tai '
              f'({WM_CX},{WM_CY})')
        if dbg:
            cx, cy = WM_CX, WM_CY
            r = 110
            crop = out.crop((max(0, cx - r), max(0, cy - r),
                             min(w, cx + r), min(h, cy + r)))
            crop.resize((crop.size[0] * 4, crop.size[1] * 4),
                        Image.LANCZOS).save(BAK / f'_chk_{name}')


if __name__ == '__main__':
    main()
