#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh loạt asset mới cho nhịp mở đầu 8 khung + hồi tưởng.
Chạy: python scripts/gen-new.py
Ghi log ra $TMPDIR/gen-new.log để theo dõi tiến độ.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

NAMES = [
    'bg-storm-wide',
    'bg-crew-running',
    'bg-running-pov',
    'bg-face-closeup',
    'bg-fall-buried',
    'bg-mars-orbit',
    'bg-waking-eyes',
    'bg-entering-hab',
    'icon-family-photo',
    'bg-houston-kitchen',
    'bg-moving-boxes',
    'bg-farewell-door',
]

ok, fail = [], []
for n in NAMES:
    print(f'=== {n} ===', flush=True)
    r = subprocess.run(
        [sys.executable, str(ROOT / 'scripts' / 'gen-assets.py'), n],
        cwd=str(ROOT),
    )
    if r.returncode == 0:
        p = ROOT / 'src' / 'assets' / 'gen' / f'{n}.png'
        if p.exists():
            ok.append(n)
        else:
            fail.append(n + ' (không có file)')
    else:
        fail.append(f'{n} (exit {r.returncode})')

print('')
print('XONG:', len(ok), 'ảnh')
for n in ok:
    p = ROOT / 'src' / 'assets' / 'gen' / f'{n}.png'
    print(f'  {n:22} {p.stat().st_size // 1024} KB')
if fail:
    print('HỎNG:')
    for n in fail:
        print('  ' + n)
