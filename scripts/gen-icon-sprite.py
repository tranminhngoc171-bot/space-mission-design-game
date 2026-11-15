#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen-icon-sprite.py
Sinh 4 icon sprite NỀN TRONG SUỐT cho màn viễn thông Giai đoạn 1.

Vì sao là script riêng: scripts/gen-assets.py đang được một sub-agent
khác sửa song song (thêm ảnh cảnh mở đầu). Sửa file đó sẽ conflict, nên
script này tự chứa phần gọi API (find_key + call_api lấy y nguyên hành vi
của gen-assets.py) và chỉ ghi ra src/assets/art/.

Khác biệt so với icon cũ: icon cũ nền tối đục + viền quanh khung. Icon
mới phải là sprite RGBA trong suốt để đặt đè lên bảng điều khiển, nên
bước hậu kỳ phải tách nền thật (matte theo màu nền) chứ không đệm nền tối.

Cách dùng:
    python scripts/gen-icon-sprite.py --list
    python scripts/gen-icon-sprite.py icon-mro-satellite
    python scripts/gen-icon-sprite.py --all
    python scripts/gen-icon-sprite.py --all --force
"""

import argparse
import base64
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / 'src' / 'assets' / 'art'
# Ảnh gốc để ở thư mục riêng, KHÔNG để trong src/assets/gen: process-assets.py
# quét gen/icon-*.png rồi ghi đè src/assets/art/icon-*.webp bằng bản nền tối,
# chạy nó sau khi sinh icon sprite là mất sạch icon trong suốt.
RAW_DIR = ROOT / 'src' / 'assets' / 'gen-icons'
MANIFEST = OUT_DIR / 'asset-manifest.json'

API_BASE = 'https://api.vilao.ai/v1'
MODEL = 'gemini-3.1-flash-lite-image'
TIMEOUT_FIRST = 180
TIMEOUT_NEXT = 120
RETRY_STATUSES = {429, 500, 502, 503, 504, 408}
MAX_ATTEMPTS = 4
BACKOFF = [8, 20, 45]

# ---- đặc tả đầu ra đã chốt (khớp process-assets.py) ----
ICON_SIZE = 128
ICON_PAD = 8
ICON_FILL = 0.82          # vật thể chiếm 82 phần trăm khung trong
ICON_QUALITY = 88
OUTLINE_W = 2
OUTLINE_RGB = (10, 14, 20)

# ---------------------------------------------------------------- phong cách

# Khối style cố định, ghép vào MỌI prompt. Bảng màu game: cam đất Sao Hỏa
# #C84B31, xám thép tàu #1E242B, trắng thiết bị NASA #E2E8F0, vàng hổ phách
# cảnh báo #F59E0B, xanh lơ màn hình dữ liệu #38BDF8.
STYLE = (
    'Grounded Hard Sci-Fi 2D Illustration, clean lineart, '
    'painterly atmospheric lighting, 60 Seconds cutaway-base clarity '
    'with The Martian NASA engineering aesthetic, '
    'palette restricted to martian rust orange #C84B31, spaceship steel '
    'grey #1E242B, NASA equipment white #E2E8F0, warning amber #F59E0B, '
    'data-screen cyan #38BDF8, '
    'isolated object on transparent background, centered, '
    'single object only, fully inside frame with empty margin on all sides, '
    'no text, no watermark, no border, no frame, no ground shadow, '
    'no background scenery, no people'
)

# Biến thể cho icon có chữ kỹ thuật hợp lệ (icon-hex-packet): bỏ "no text"
# và thay bằng luật cho phép đúng loại ký tự được duyệt.
STYLE_TEXT_OK = STYLE.replace(
    'no text, no watermark,',
    'the only text allowed is the hexadecimal glyph layer described above, '
    'rendered large, faint and inside the object surface, '
    'no other text, no caption, no label, no watermark,'
)

# Nền để key: model ảnh không xuất alpha thật, nên xin một nền phẳng
# trung tính rồi tách bằng thuật toán. Xám trung tính an toàn hơn trắng
# (vật trắng NASA) và hơn xanh lá (viền xanh bị lem vào cạnh kim loại).
KEY_BG = (
    'background is a single flat uniform mid grey #7A7A7A, '
    'no gradient, no vignette, no floor, no shadow cast on the background'
)

ASSETS = {
    'icon-mro-satellite': {
        'note': 'icon: vệ tinh Mars Reconnaissance Orbiter',
        'prompt': (
            'a NASA Mars Reconnaissance Orbiter spacecraft shown as a single '
            'isolated object in three quarter view, tilted slightly so the '
            'viewer sees both the top deck and one flank, '
            'a boxy rectangular aluminium equipment bus with visible panel '
            'seams, rivets and small bolted hatch plates, '
            'two very large flat rectangular solar array wings extending '
            'left and right from the bus, each wing made of dark blue '
            'photovoltaic cell grids in a pale metal lattice frame, '
            'a small white parabolic high gain dish antenna mounted on the '
            'front of the bus angled clearly downward toward the viewer, '
            'a slim gold foil thermal blanket band around the middle of the '
            'bus, one small amber status lamp, thin cyan instrument slit, '
            'clean crisp outlines, cool white key light from upper left with '
            'warm rust rim light along the right edge, '
            'wide readable silhouette, both solar wings fully inside the frame'
        ),
    },
    'icon-dsn-dish': {
        'note': 'icon: chảo thu Deep Space Network',
        'prompt': (
            'a large Deep Space Network parabolic dish antenna as a single '
            'isolated object, seen from a low three quarter angle so the '
            'concave bowl faces up and toward the upper right of frame, '
            'the dish surface is a fine regular mesh grid of pale ribs and '
            'open triangles with a small central feed horn on a tripod strut '
            'pointing out of the bowl, '
            'the back of the dish is braced by radial steel struts, '
            'the bowl sits on a heavy steel truss pedestal of riveted box '
            'beams and diagonal lattice bracing with two visible azimuth '
            'wheel trucks at the base, '
            'white painted dish rim and pale NASA equipment white panels on '
            'the pedestal, rust orange and grey steel structure, '
            'one small amber beacon lamp on the truss, '
            'clean crisp lineart on every truss member, '
            'cool white key light from upper left, warm amber fill from below, '
            'entire pedestal base and dish rim fully inside the frame'
        ),
    },
    'icon-uhf-transmitter': {
        'note': 'icon: bộ phát UHF gắn trên trạm',
        'prompt': (
            'a compact UHF radio transmitter unit as a single isolated object, '
            'seen in three quarter view, '
            'a rugged metal box chassis in NASA equipment white with steel '
            'grey corner brackets, bolted flanges and four mounting feet, '
            'a front panel with a small cyan data screen and three round '
            'knurled dials, cooling fins cut into one side, '
            'two short stiff stub whip antennas rising from the top rear '
            'connector block, one straight and one angled, '
            'a short coiled signal cable looped at the left side, '
            'a small amber signal lamp lit on the top front corner, '
            'scuffed paint and light dust film, clean crisp outlines, '
            'cool white key light from upper left with warm rust bounce '
            'from the right, whole chassis and antenna tips inside the frame'
        ),
    },
    'icon-hex-packet': {
        'note': 'icon: gói tin dữ liệu hex',
        # allow_text: khối STYLE toàn cục có "no text", mà đặc tả icon này
        # lại đòi chữ hex mờ bên trong khối. Lần sinh đầu model bỏ sạch
        # glyph vì bị chính STYLE cấm, nên spec này tắt "no text" và thay
        # bằng luật riêng cho phép ký tự kỹ thuật cỡ lớn.
        'allow_text': True,
        'prompt': (
            'a single floating data packet cube as an icon, '
            'a solid isometric cube with three visible faces, sharp clean '
            'edges, dark steel blue glass panels, '
            'every face is covered edge to edge by a bright glowing cyan '
            'triangular wireframe lattice grid, the lattice lines are thick '
            'and clearly visible on all three faces with bright cyan nodes at '
            'every intersection, the lattice is the dominant surface feature, '
            'behind the lattice on each face sit very large faint hexadecimal '
            'characters spelling digit and letter pairs such as 4F 2A 9C E1 '
            '7B 0D, big chunky glyphs readable at small icon size, drawn in '
            'pale cyan and amber at low opacity, three glyph rows per face, '
            'a continuous glowing amber edge highlight runs along every one '
            'of the nine visible silhouette edges of the cube, '
            'one corner of the cube emits a soft data-screen cyan glow, '
            'clean crisp lineart on all edges, painterly atmospheric glow, '
            'cool cyan key light with warm amber rim light, '
            'whole cube fully inside the frame with margin on all sides'
        ),
    },
}


# ---------------------------------------------------------------- gọi API

def find_key():
    """Tìm API key có quyền tạo ảnh (chép nguyên thứ tự ưu tiên của
    gen-assets.py: file secrets trong workspace đứng trước biến môi trường,
    vì .env trên máy này là key cũ chỉ dùng cho model chữ, gọi tạo ảnh 403)."""
    candidates = []
    for p in sorted(Path.home().glob('workspace/user-*/secrets/vilao-api-key.txt')):
        if p.exists():
            text = p.read_text(encoding='utf-8-sig', errors='ignore')
            m = re.search(r'sk-[A-Za-z0-9\-_]+', text)
            if m:
                candidates.append(('workspace-secrets', m.group(0)))

    env_key = os.environ.get('HERMES_MODEL_PROVIDER_API_KEY')
    if env_key:
        candidates.append(('env', env_key))

    for p in [
        Path.home() / 'AppData' / 'Local' / 'hermes' / '.env',
        Path.home() / '.hermes' / '.env',
    ]:
        if p.exists():
            text = p.read_text(encoding='utf-8-sig', errors='ignore')
            m = re.search(r'HERMES_MODEL_PROVIDER_API_KEY\s*=\s*["\']?(sk-[A-Za-z0-9\-_]+)', text)
            if m:
                candidates.append(('hermes-env', m.group(1)))

    for src, c in candidates:
        c = c.strip().strip('"').strip("'")
        if c.startswith('sk-') and len(c) > 20:
            print(f'  dùng key từ: {src}')
            return c
    return None


def call_api(key, prompt, timeout):
    payload = json.dumps({'model': MODEL, 'prompt': prompt, 'n': 1}).encode('utf-8')
    req = urllib.request.Request(
        f'{API_BASE}/images/generations',
        data=payload,
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        detail = ''
        try:
            detail = e.read().decode('utf-8')[:300]
        except Exception:
            pass
        return None, {'status': e.code, 'detail': detail}
    except urllib.error.URLError as e:
        return None, {'status': 0, 'detail': f'lỗi mạng: {e.reason}'}
    except TimeoutError:
        return None, {'status': 0, 'detail': 'hết thời gian chờ'}

    data = body.get('data') or []
    if not data:
        return None, {'status': 0, 'detail': 'phản hồi không có ảnh'}
    item = data[0]
    if item.get('b64_json'):
        return base64.b64decode(item['b64_json']), None
    if item.get('url'):
        try:
            with urllib.request.urlopen(item['url'], timeout=120) as r:
                return r.read(), None
        except Exception as e:
            return None, {'status': 0, 'detail': f'tải url lỗi: {e}'}
    return None, {'status': 0, 'detail': 'không có b64_json lẫn url'}


def generate(key, name, spec, force=False):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / f'{name}.png'

    if out_path.exists() and out_path.stat().st_size > 5000 and not force:
        print(f'  [{name}] đã có ảnh gốc, bỏ qua (--force để làm lại).')
        return True

    print(f'  [{name}] {spec["note"]}')
    style = STYLE_TEXT_OK if spec.get('allow_text') else STYLE
    full_prompt = spec['prompt'] + ', ' + KEY_BG + ', ' + style
    (RAW_DIR / f'{name}.prompt.txt').write_text(full_prompt, encoding='utf-8')

    for attempt in range(1, MAX_ATTEMPTS + 1):
        t0 = time.time()
        timeout = TIMEOUT_FIRST if attempt == 1 else TIMEOUT_NEXT
        img, err = call_api(key, full_prompt, timeout)
        elapsed = time.time() - t0
        if img:
            out_path.write_bytes(img)
            print(f'    xong sau {elapsed:.0f} giây, {len(img) / 1024:.0f} KB')
            return True

        status = (err or {}).get('status', 0)
        detail = (err or {}).get('detail', 'không rõ')
        if status in (401, 403):
            print(f'    DỪNG: {status} {detail[:200]}')
            return False
        if status in RETRY_STATUSES or status == 0:
            if attempt < MAX_ATTEMPTS:
                wait = BACKOFF[min(attempt - 1, len(BACKOFF) - 1)] + random.randint(0, 4)
                print(f'    lần {attempt} lỗi {status}, chờ {wait} giây rồi thử lại')
                time.sleep(wait)
                continue
        print(f'    HỎNG sau {attempt} lần: {status} {detail[:200]}')
        return False
    return False


# ---------------------------------------------------------------- hậu kỳ

def _sample_bg(rgb):
    """Màu nền: trung vị của dải viền ngoài cùng. Trung vị chịu được vài
    pixel vật thể lọt ra mép, còn trung bình thì bị kéo lệch."""
    h, w, _ = rgb.shape
    band = max(3, min(w, h) // 40)
    edges = np.concatenate([
        rgb[:band].reshape(-1, 3), rgb[-band:].reshape(-1, 3),
        rgb[:, :band].reshape(-1, 3), rgb[:, -band:].reshape(-1, 3),
    ])
    return np.median(edges, axis=0)


def _largest_component(mask, min_ratio=0.08):
    """Mặt nạ boolean chỉ giữ các thành phần liên thông đủ lớn.

    Giữ mọi thành phần có diện tích >= min_ratio lần thành phần lớn nhất,
    chứ không chỉ đúng một thành phần: ăng-ten que mảnh hay tấm pin nối
    bằng cột mảnh có thể đứt trong mặt nạ ngưỡng, bỏ chúng thì icon mất
    chi tiết. Mảnh rác lơ lửng của model thì nhỏ hơn ngưỡng nên bị loại.
    """
    from collections import deque

    h, w = mask.shape
    seen = np.zeros((h, w), bool)
    comps = []
    for sy in range(h):
        row = mask[sy]
        if not row.any():
            continue
        for sx in np.nonzero(row & ~seen[sy])[0]:
            if seen[sy, sx]:
                continue
            q = deque([(sy, int(sx))])
            seen[sy, sx] = True
            pix = []
            while q:
                y, x = q.popleft()
                pix.append((y, x))
                for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        q.append((ny, nx))
            comps.append(pix)

    if not comps:
        return mask
    biggest = max(len(c) for c in comps)
    out = np.zeros((h, w), bool)
    for c in comps:
        if len(c) >= biggest * min_ratio:
            ys = [p[0] for p in c]
            xs = [p[1] for p in c]
            out[ys, xs] = True
    return out


def matte_background(im):
    """Tách nền thành alpha. Trả ảnh RGBA.

    Model không xuất alpha thật, nên: đo màu nền từ viền ảnh, tính khoảng
    cách màu từng pixel tới màu nền, rồi lấy ngưỡng mềm. Sau đó chỉ giữ
    thành phần liên thông lớn nhất chạm tâm (bỏ các mảng nền rác lọt vào
    do gradient), và lấp lỗ bên trong vật thể (lỗ có alpha 0 nằm trong
    silhouette sẽ thành đốm trong suốt khi đặt lên panel tối).
    """
    rgb = np.array(im.convert('RGB')).astype(np.float32)
    h, w, _ = rgb.shape
    bg = _sample_bg(rgb)

    dist = np.sqrt(((rgb - bg) ** 2).sum(axis=2))
    # ngưỡng dưới: dưới mức này coi là nền tuyệt đối; trên ngưỡng trên coi
    # là vật thể tuyệt đối; ở giữa là cạnh, cho alpha chuyển dần để cạnh
    # không bị răng cưa khi thu nhỏ về 128.
    lo, hi = 14.0, 40.0
    alpha = np.clip((dist - lo) / (hi - lo), 0.0, 1.0)

    solid = (alpha > 0.5).astype(np.uint8) * 255
    # --- chỉ giữ thành phần liên thông LỚN NHẤT ---
    # Không dùng "mọi vùng không chạm viền": model hay vẽ thêm mảnh rác rời
    # rạc (một hình thoi nhỏ lơ lửng cạnh vật thể). Nếu giữ, bbox bị kéo
    # lệch và vật thể chính lệch tâm trong khung 128.
    keep = _largest_component(solid > 0)

    alpha = alpha * keep.astype(np.float32)

    # --- lấp lỗ: pixel alpha 0 nằm trong silhouette thì nâng lên theo
    # hàng xóm gần nhất (dùng phép giãn lặp, ảnh nhỏ nên nhanh) ---
    filled = (alpha > 0.05)
    for _ in range(int(min(h, w) * 0.06)):
        grown = filled.copy()
        grown[1:, :] |= filled[:-1, :]
        grown[:-1, :] |= filled[1:, :]
        grown[:, 1:] |= filled[:, :-1]
        grown[:, :-1] |= filled[:, 1:]
        if grown.sum() == filled.sum():
            break
        filled = grown
    holes = filled & (alpha < 0.05)
    if holes.any():
        # điền alpha cho lỗ bằng giá trị trung vị của vật thể
        alpha[holes] = 1.0

    out = np.dstack([rgb, alpha * 255.0]).astype(np.uint8)
    res = Image.fromarray(out, 'RGBA')
    # làm mượt cạnh alpha một chút, chỉ trên kênh alpha
    a = res.getchannel('A').filter(ImageFilter.GaussianBlur(0.6))
    res.putalpha(a)
    return res


def alpha_bbox(im, thresh=24):
    a = np.array(im.getchannel('A'))
    ys, xs = np.nonzero(a > thresh)
    if len(ys) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def process_icon(name):
    """Tách nền, dò bbox vật thể, canh giữa, resize 128x128, vẽ viền 2px.

    Viền vẽ SAU khi resize, và vẽ bằng cách giãn chính silhouette của vật
    thể 2px rồi tô màu tối phía dưới, không vẽ khung chữ nhật quanh canvas,
    vì như vậy bốn góc sẽ hết trong suốt (đặc tả đòi alpha = 0 ở bốn góc).
    """
    src = RAW_DIR / f'{name}.png'
    im = Image.open(src)
    rgba = matte_background(im)

    box = alpha_bbox(rgba)
    if not box:
        raise RuntimeError(f'{name}: tách nền ra rỗng, ảnh gốc có thể quá giống nền')
    x0, y0, x1, y1 = box
    rgba = rgba.crop(box)

    # đưa về vuông, giữ tỉ lệ vật thể, đệm trong suốt
    w, h = rgba.size
    side = max(w, h)
    sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    sq.paste(rgba, ((side - w) // 2, (side - h) // 2))

    inner = int((ICON_SIZE - ICON_PAD * 2) * ICON_FILL)   # 91 px
    sq = sq.resize((inner, inner), Image.LANCZOS)

    canvas = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    off = (ICON_SIZE - inner) // 2
    canvas.paste(sq, (off, off))

    # --- viền tối 2px bám silhouette, vẽ sau resize ---
    a = np.array(canvas.getchannel('A'))
    mask = (a > 40)
    grown = mask.copy()
    for _ in range(OUTLINE_W):
        g = grown.copy()
        g[1:, :] |= grown[:-1, :]
        g[:-1, :] |= grown[1:, :]
        g[:, 1:] |= grown[:, :-1]
        g[:, :-1] |= grown[:, 1:]
        grown = g
    ring = grown & ~mask                     # vành ngoài đúng 2px
    arr = np.array(canvas)
    arr[ring, 0] = OUTLINE_RGB[0]
    arr[ring, 1] = OUTLINE_RGB[1]
    arr[ring, 2] = OUTLINE_RGB[2]
    arr[ring, 3] = 255
    canvas = Image.fromarray(arr, 'RGBA')

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f'{name}.webp'
    canvas.save(out, 'WEBP', quality=ICON_QUALITY, method=6)
    return out, canvas


def update_manifest():
    """Gộp 4 icon mới vào asset-manifest.json, giữ nguyên phần scenes và
    các icon cũ. Đọc lại file thay vì ghi đè cứng, để không xoá công của
    process-assets.py chạy trước đó."""
    if MANIFEST.exists():
        try:
            manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            manifest = {'scenes': [], 'icons': []}
    else:
        manifest = {'scenes': [], 'icons': []}

    manifest.setdefault('scenes', [])
    icons = {i['id']: i for i in manifest.get('icons', [])}

    for name in ASSETS:
        p = OUT_DIR / f'{name}.webp'
        if not p.exists():
            continue
        with Image.open(p) as im:
            w, h = im.size
        icons[name] = {
            'id': name,
            'path': f'assets/art/{p.name}',
            'width': w,
            'height': h,
            'bytes': p.stat().st_size,
            'transparent': True,
            'note': ASSETS[name]['note'],
        }

    manifest['icons'] = [icons[k] for k in sorted(icons)]
    manifest['generated'] = datetime.now().isoformat(timespec='seconds')
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return MANIFEST


def main():
    ap = argparse.ArgumentParser(description='Sinh icon sprite nền trong suốt')
    ap.add_argument('name', nargs='?')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--force', action='store_true', help='sinh lại ảnh gốc')
    ap.add_argument('--post', action='store_true', help='chỉ chạy hậu kỳ, không gọi API')
    args = ap.parse_args()

    if args.list:
        for k, v in ASSETS.items():
            print(f'  {k:24} {v["note"]}')
        return

    targets = list(ASSETS.items()) if args.all else (
        [(args.name, ASSETS[args.name])] if args.name in ASSETS else []
    )
    if not targets:
        ap.print_help()
        return

    if not args.post:
        key = find_key()
        if not key:
            print('Không tìm thấy API key.')
            sys.exit(1)
        print(f'Model: {MODEL}\nRa: {OUT_DIR}\n')
        ok, fail = 0, []
        for i, (name, spec) in enumerate(targets, 1):
            print(f'({i}/{len(targets)})', end=' ')
            if generate(key, name, spec, force=args.force):
                ok += 1
            else:
                fail.append(name)
            if i < len(targets):
                time.sleep(3)
        print(f'\nSinh xong: {ok}/{len(targets)}')
        if fail:
            print(f'Hỏng: {", ".join(fail)}')
            sys.exit(1)

    print('Hậu kỳ:')
    for name, _ in targets:
        if not (RAW_DIR / f'{name}.png').exists():
            print(f'  {name}: thiếu ảnh gốc')
            continue
        out, img = process_icon(name)
        print(f'  {out.name:26} {img.size[0]}x{img.size[1]}  {out.stat().st_size} bytes')

    print(f'\nManifest: {update_manifest()}')


if __name__ == '__main__':
    main()
