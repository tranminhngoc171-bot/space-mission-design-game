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

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src' / 'assets' / 'gen'
BAK = ROOT / 'src' / 'assets' / 'gen-wm-orig'

NAMES = [f'bg-im-{i:02d}.png' for i in range(1, 8)]

# Tam ngoi sao va nua kich thuoc hop che. Do lai that ky tren anh goc:
# ngoi sao chi rong khoang 26px, khung bao x 1261..1287, y 664..690.
# Lan dau uoc luong 170px nen vung khuech tan qua lon, che mat mot mang
# tranh va hien ra nhu vet mo. Hop che phai sat voi ngoi sao.
WM_CX = 1274
WM_CY = 677
WM_HW = 22
WM_HH = 24


def star_mask(a):
    """Mat na om sat ngoi sao, khong phai hinh chu nhat.

    Ngoi sao ban trong suot mau trang xam nen do bao hoa thap va do sang
    cao hon han vung quanh. Quet trong hop 90x90 quanh tam, lay pixel
    thoa ca hai dieu kien, roi no ra 4px de phu vien mem.

    Mat na hinh chu nhat 44x48 phu ca vung khong co sao, nen buoc lap
    phai bia ra mot mang lon: o khung 02 no an vao mat nhan vat, o khung
    05 no an vao to giay. Om sat sao thi chi con vai tram pixel phai lap.
    """
    h, w = a.shape[:2]
    m = np.zeros((h, w), np.uint8)

    r = 45
    y0, y1 = max(0, WM_CY - r), min(h, WM_CY + r)
    x0, x1 = max(0, WM_CX - r), min(w, WM_CX + r)
    sub = a[y0:y1, x0:x1].astype(int)

    lum = sub.mean(axis=2)
    sat = sub.max(axis=2) - sub.min(axis=2)

    # Nguong tuong doi theo do sang nen quanh sao, de anh toi va anh
    # sang deu bat duoc sao.
    bg_lum = np.median(lum)
    cand = (lum > bg_lum + 22) & (sat < 45)
    m[y0:y1, x0:x1] = np.where(cand, 255, 0).astype(np.uint8)

    # Nguong tren bat ca chi tiet sang cua canh (den ban, giay trang...),
    # lam mat na phinh ra hang nghin pixel va buoc lap phai bia qua
    # nhieu. Giu lai thanh phan lien thong chua tam sao roi gioi han
    # trong o 60x60 quanh tam: ngoi sao khong the rong hon the.
    n_lab, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    if n_lab > 1:
        cy = WM_CY - y0
        cx = WM_CX - x0
        keep = lab[max(0, cy), max(0, cx)]
        if keep == 0:
            # diem tam roi vao khe giua cac canh sao: lay thanh phan
            # gan tam nhat
            best, best_d = 0, 1e9
            for i in range(1, n_lab):
                sx, sy = stats[i, 0] + stats[i, 2] / 2, stats[i, 1] + stats[i, 3] / 2
                d = (sx - cx) ** 2 + (sy - cy) ** 2
                if d < best_d:
                    best, best_d = i, d
            keep = best
        m = np.where(lab == keep, 255, 0).astype(np.uint8)

    # Gioi han cung: chi giu trong hop 60x60 quanh tam.
    lim = np.zeros_like(m)
    ly0, ly1 = max(0, WM_CY - y0 - 30), min(m.shape[0], WM_CY - y0 + 30)
    lx0, lx1 = max(0, WM_CX - x0 - 30), min(m.shape[1], WM_CX - x0 + 30)
    lim[ly0:ly1, lx0:lx1] = 255
    m = cv2.bitwise_and(m, lim)

    # No ra de phu vien mem cua sao.
    m = cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2)
    return m


def inpaint_diffuse(im, iters=900):
    """Lap vung sao bang cv2.inpaint (thuat Telea).

    Vi sao khong nhan ban ket cua (clone patch): da thu hai lan. Lan mot
    de lai dau tren cua sao; lan hai che duoc sao nhung hop che hien ra
    nhu mot hinh chu nhat lech tong so voi nen.

    Vi sao khong dung khuech tan thuần numpy: vung lap tro thanh mot vet
    mo dai, mat het net ve va ket cau cua canh quanh (o khung 02 no an
    vao mat mot nhan vat). Telea gan ket qua tu canh theo huong gradient,
    giu duoc net va bien do tot hon nhieu.

    Mat na chi phu dung ngoi sao 44x48, khong lon hon: lan dau uoc luong
    170px thi vet sua hien ra nhu mot vung mo to.
    """
    a = np.array(im)
    h, w = a.shape[:2]
    x0, x1 = max(0, WM_CX - WM_HW), min(w, WM_CX + WM_HW)
    y0, y1 = max(0, WM_CY - WM_HH), min(h, WM_CY + WM_HH)

    mask = np.zeros((h, w), np.uint8)
    mask[y0:y1, x0:x1] = 255

    n_pix = int((mask > 0).sum())
    # INPAINT_NS (Navier-Stokes) voi ban kinh 11 cho ket qua sach nhat.
    # Da thu bon bien the (telea 3, telea 7, ns 5, ns 11) tren khung 02
    # va 05: telea de lai vet mo ro o vung mat nguoi va to giay, ns 11
    # lap kin khong con vet. Ban kinh lon la diem mau: ns lay trung binh
    # theo huong dong chay cua gradient tren vong tron rong, nen rong
    # hon thi vung lap muon hon va khong lo hinh chu nhat.
    out = cv2.inpaint(a, mask, 11, cv2.INPAINT_NS)

    # Them hat phim nhe de vung lap khong nhuan hon canh quanh.
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 2.2, out.shape)
    out = out.astype(np.float64)
    out[mask > 0] += noise[mask > 0]
    out = np.clip(out, 0, 255).astype(np.uint8)
    print(f'    mat na {n_pix} pixel')
    return Image.fromarray(out)


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
        out = inpaint_diffuse(im)
        out.save(p)
        w, h = im.size
        print(f'  {name:16} {w}x{h} khuech tan hop '
              f'{WM_HW * 2}x{WM_HH * 2} tai ({WM_CX},{WM_CY})')
        if dbg:
            cx, cy = WM_CX, WM_CY
            r = 110
            crop = out.crop((max(0, cx - r), max(0, cy - r),
                             min(w, cx + r), min(h, cy + r)))
            crop.resize((crop.size[0] * 4, crop.size[1] * 4),
                        Image.LANCZOS).save(BAK / f'_chk_{name}')


if __name__ == '__main__':
    main()
