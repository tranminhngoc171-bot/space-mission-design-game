#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh sprite phi hành gia mặc bộ đồ du hành, đeo ba lô dưỡng khí.

Bản char-healthy.webp hiện có là một thành viên phi hành đoàn mặc
jumpsuit cầm bảng kẹp, không phải bộ đồ du hành có ba lô. Bản phác
thảo màn menu gọi đúng hình đó, nên sinh riêng một sprite.

Dùng lại đúng bộ hàm của scripts/gen-assets.py để khối style và cách
tìm khoá API không lệch.
"""
import base64
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib.util

_spec = importlib.util.spec_from_file_location(
    'gen_assets', Path(__file__).resolve().parent / 'gen-assets.py')
ga = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ga)

OUT = Path(__file__).resolve().parent.parent / 'src' / 'assets' / 'gen-sprites' / 'menu-astro.png'

PROMPT = (
    'a lone astronaut in a full white and grey pressurised EVA space suit, '
    'seen from behind at a three-quarter angle over the shoulder, standing still, '
    'large rectangular life support backpack with hoses and a small amber status light, '
    'helmet with a dark gold mirrored visor, dusty red-orange Mars regolith caked on the boots and knees, '
    'arms relaxed at the sides, body turned slightly away from the viewer, '
    'full body from helmet to boots, centred, occupies about 82 percent of the frame height, '
    'clean flat mid-grey background with no scenery and no cast shadow'
)

STYLE = (
    'digital painting, semi-realistic concept art, cinematic lighting, '
    'warm amber rim light along the silhouette, cool shadow side, '
    'high detail, sharp focus, no text, no watermark, no logo'
)

KEY_BG = (
    'isolated on a plain flat neutral mid-grey backdrop, subject fully inside the frame, '
    'nothing touching the edges, no ground plane, no horizon, no props'
)


def main():
    key = ga.find_key()
    if not key:
        print('không tìm được khoá API')
        return 1

    prompt = PROMPT + ', ' + STYLE + ', ' + KEY_BG
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists() and OUT.stat().st_size > 5000:
        print('đã có', OUT)
        return 0

    for attempt in range(1, 4):
        print(f'lần {attempt}...')
        t0 = time.time()
        img, err = ga.call_api(key, prompt, ga.TIMEOUT_FIRST if attempt == 1 else ga.TIMEOUT_NEXT,
                               size='896x1152')
        print(f'  {time.time() - t0:.0f}s', 'lỗi: ' + str(err) if err else 'ok')
        if img:
            OUT.write_bytes(img)
            print('ghi', OUT, len(img), 'byte')
            return 0
        time.sleep(5)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
