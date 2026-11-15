#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen-assets.py
Sinh ảnh cho game qua API Vilao, có cơ chế thử lại.

Vì sao cần thử lại: mỗi ảnh tốn 30 tới 90 giây, và dịch vụ hay trả
lỗi tạm thời (503 quá tải, 429 quá nhiều request, timeout). Bỏ cuộc
ngay lần đầu là mất công chờ vô ích.

Cách dùng:
    python scripts/gen-assets.py --list
    python scripts/gen-assets.py <tên-asset>
    python scripts/gen-assets.py --all

Ảnh ra nằm trong src/assets/gen/<tên>.png
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
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / 'src' / 'assets' / 'gen'

API_BASE = 'https://api.vilao.ai/v1'
MODEL = 'gemini-3.1-flash-lite-image'

# Model này chậm: 30 tới 90 giây một ảnh là bình thường, lần đầu của
# một phiên có thể lâu hơn. Đặt hạn chờ rộng, đừng cắt sớm.
TIMEOUT_FIRST = 180
TIMEOUT_NEXT = 120

# Lỗi tạm thời thì thử lại. Lỗi quyền (403) thì dừng ngay vì thử lại
# cũng không qua, chỉ tốn thời gian.
RETRY_STATUSES = {429, 500, 502, 503, 504, 408}
MAX_ATTEMPTS = 4
BACKOFF = [8, 20, 45]   # giây chờ giữa các lần thử


# ---------------------------------------------------------------- phong cách

# Mọi prompt đều phải mang đúng khối này, không được lệch một chữ.
# Lý do: model tạo ảnh đổi phong cách theo từng lần gọi. Nếu mỗi ảnh
# tả style khác nhau thì bộ asset trông như nhặt từ nhiều game khác
# nhau ghép lại. Một khối style cố định giữ cả bộ cùng một giọng.
STYLE_LOOK = (
    'digital painting, semi-realistic concept art, '
    'soft brushwork with visible texture, '
    'cinematic warm lighting from a single low sun, '
    'muted desaturated palette of ochre, rust red and dusty amber, '
    'shallow depth of field, film grain, '
    'NASA concept art book aesthetic'
)

STYLE_CLEAN = (
    STYLE_LOOK + ', '
    'no text, no letters, no numbers, no logo, no watermark, '
    'no people, no faces, no hands'
)

# Cảnh mở đầu mới bắt buộc phải có người: nhóm phi hành gia chạy trong
# bão, góc nhìn thứ nhất, cận mặt trong mũ. Dùng chung khối STYLE ở trên
# thì model sẽ không vẽ người nào, khung hình thành phong cảnh trống và
# mất hẳn ý đồ kể chuyện. Ba biến thể dưới đây giữ nguyên giọng màu và
# ánh sáng, chỉ mở khoá phần con người.
STYLE_CREW = (
    STYLE_LOOK + ', '
    'figures in bulky white EVA pressure suits with scuffed visors, '
    'faces not visible behind mirrored helmet glass, '
    'no text, no letters, no numbers, no logo, no watermark'
)

STYLE_POV = (
    STYLE_LOOK + ', '
    'first person point of view, a single gloved hand and forearm '
    'in frame at the lower edge, bulky white EVA suit sleeve, '
    'no text, no letters, no numbers, no logo, no watermark, no face'
)

STYLE_FACE = (
    STYLE_LOOK + ', '
    'one astronaut seen in close up through a clear helmet visor, '
    'face visible behind the glass, red dust on the visor, '
    'no text, no letters, no numbers, no logo, no watermark'
)

STYLE = STYLE_CLEAN

# Tỉ lệ khung: dùng 16:9 cho ảnh nền, 1:1 cho icon.
# Model có thể bỏ qua tham số size, nên vẫn phải crop ở hậu kỳ.

# ---------------------------------------------------------------- mô tả asset

ASSETS = {
    # ---------- ảnh nền màn chơi ----------
    'bg-hab': {
        'prompt': (
            'interior of a small Mars habitat living module seen from a low angle, '
            'cramped metal walls with equipment lockers and cable runs, '
            'a folding work table, warm amber task lamp casting long shadows, '
            'red dust film on every surface'
        ),
        'note': 'nền: bên trong khoang trú ẩn',
        'kind': 'scene',
    },
    'bg-farm': {
        'prompt': (
            'interior of a sealed greenhouse growing module on Mars, '
            'rows of metal growing trays with small green potato sprouts, '
            'UV grow lamps hanging overhead, condensation on the ceiling panels, '
            'ochre stone walls around the trays'
        ),
        'note': 'nền: khu trồng trọt trong nhà kính',
        'kind': 'scene',
    },
    'bg-airlock': {
        'prompt': (
            'interior view of a Mars habitat airlock chamber, '
            'heavy circular pressure door with a small window, '
            'dust settling on the floor grating, coiled tether on a hook, '
            'dim emergency light above the door'
        ),
        'note': 'nền: cửa khoang khí',
        'kind': 'scene',
    },
    'bg-workbench': {
        'prompt': (
            'interior of a Mars habitat repair workshop, '
            'steel workbench covered with hand tools and coiled wire, '
            'a hydrazine tank on the floor, welding mask hanging on the wall, '
            'single overhead lamp illuminating the bench'
        ),
        'note': 'nền: bàn kỹ thuật',
        'kind': 'scene',
    },
    'bg-radio': {
        'prompt': (
            'interior corner of a Mars habitat communications station, '
            'a disassembled antenna dish leaning against the wall, '
            'cables running to a radio transceiver on a small table, '
            'faint green glow from the equipment panel'
        ),
        'note': 'nền: trạm liên lạc',
        'kind': 'scene',
    },

    # ---------- 8 khung mở đầu điện ảnh ----------
    # Nhịp mở màn mới: bão cát tới trước, kể bằng tai nạn, không kể bằng
    # bữa tối ở Houston. Thứ tự khung quyết định nhịp, nên mô tả ở đây
    # bám sát từng khung, không dùng chung một câu cảnh bão.

    'bg-storm-wide': {
        'prompt': (
            'vast martian plain at dusk, an enormous wall of red dust '
            'hundreds of meters tall advancing across the horizon, '
            'buttes and boulders silhouetted in front of it, '
            'the sun smothered to a dull orange disc, empty foreground, '
            'extreme wide shot, everything small against the storm'
        ),
        'note': 'khung 1: toàn cảnh bão cát trên Sao Hỏa',
        'kind': 'scene',
    },
    'bg-crew-running': {
        'prompt': (
            'five astronauts in bulky white pressure suits sprinting '
            'through a martian dust storm toward the camera-left, '
            'bodies leaning into the wind, one of them stumbling, '
            'red dust swirling thick around their legs and backlit by '
            'a dim orange sun, the lander legs looming behind them'
        ),
        'note': 'khung 2: nhóm phi hành gia chạy trong bão',
        'kind': 'scene',
        'style': STYLE_CREW,
    },
    'bg-running-pov': {
        'prompt': (
            'first person view running across a martian plain in a dust storm, '
            'a suited astronaut ahead climbing the ladder of a lander, '
            'second figure right behind them reaching for the rung, '
            'whipped red dust streaming past, lander legs and engine bell '
            'looming close, tilted horizon from running'
        ),
        'note': 'khung 3: góc nhìn thứ nhất, đồng đội leo lên tàu',
        'kind': 'scene',
        'style': STYLE_POV,
    },
    'bg-face-closeup': {
        'prompt': (
            'tight close up of an astronaut face inside a space helmet, '
            'dust scratched visor, a thin horizontal band of pale light '
            'sweeping across the eyes and cheekbone, sweat on the temple, '
            'storm and orange haze reflected in the curved glass, '
            'eyes wide, shallow focus on the eyes'
        ),
        'note': 'khung 4: cận mặt trong mũ không gian',
        'kind': 'scene',
        'style': STYLE_FACE,
    },
    'bg-fall-buried': {
        'prompt': (
            'a suited astronaut face down on martian ground, one arm '
            'outstretched, red sand already drifted over the legs and back, '
            'only the shoulder and helmet still clear, dust pouring across '
            'the frame, low angle close to the ground'
        ),
        'note': 'khung 5: ngã xuống, cát phủ dần',
        'kind': 'scene',
        'style': STYLE_CREW,
    },
    'bg-mars-orbit': {
        'prompt': (
            'mars seen from high orbit, the whole rust red disc filling '
            'the lower half of frame, thin pale atmosphere at the limb, '
            'a small ascent vehicle streaking away from the surface as a '
            'bright point with a faint exhaust trail, black space above, '
            'cold blue-white sunlight from the side'
        ),
        'note': 'khung 5: toàn cảnh Sao Hỏa, tàu đã bay xa',
        'kind': 'scene',
    },
    'bg-waking-eyes': {
        'prompt': (
            'interior of a habitat module seen from the floor, view tilted '
            'and partially obstructed by a blurred foreground edge like '
            'half closed eyelids, ceiling panels and cable runs overhead, '
            'warm amber light bleeding in from the left, heavy soft focus '
            'in the corners'
        ),
        'note': 'khung 7: mở mắt sau hôn mê',
        'kind': 'scene',
    },
    'bg-entering-hab': {
        'prompt': (
            'first person view walking through the open inner hatch of a '
            'mars habitat, dark airlock frame around the edges of frame, '
            'warm amber interior light spilling out across a metal floor, '
            'equipment lockers and a work table beyond the threshold, '
            'red dust on the boot plate at the bottom of frame'
        ),
        'note': 'khung 8: bước vào căn cứ',
        'kind': 'scene',
        'style': STYLE_POV,
    },

    # ---------- icon vật phẩm, khung vuông ----------
    'icon-ration': {
        'prompt': (
            'a single foil ration pack standing upright, '
            'crinkled silver packaging with a small torn corner, '
            'isolated on a plain dark background, centered, product shot'
        ),
        'note': 'icon: gói khẩu phần',
        'kind': 'icon',
    },
    'icon-water': {
        'prompt': (
            'a single clear plastic water bottle with a screw cap, '
            'half full, condensation droplets on the surface, '
            'isolated on a plain dark background, centered, product shot'
        ),
        'note': 'icon: bình nước',
        'kind': 'icon',
    },
    'icon-potato': {
        'prompt': (
            'a single raw potato with a few small sprouts, '
            'reddish brown skin with patches of dirt, '
            'isolated on a plain dark background, centered, product shot'
        ),
        'note': 'icon: củ khoai tây',
        'kind': 'icon',
    },
    'icon-seed': {
        'prompt': (
            'a small clear sample vial containing dark potato seeds, '
            'stopper on top, label tag tied with string, '
            'isolated on a plain dark background, centered, product shot'
        ),
        'note': 'icon: mẫu hạt giống',
        'kind': 'icon',
    },
    'icon-tape': {
        'prompt': (
            'a rolled length of thick grey duct tape, '
            'slightly unrolled end, worn cardboard core, '
            'isolated on a plain dark background, centered, product shot'
        ),
        'note': 'icon: băng keo chịu lực',
        'kind': 'icon',
    },
    'icon-electronics': {
        'prompt': (
            'a small circuit board with capacitors and wires, '
            'green board with silver solder points, '
            'isolated on a plain dark background, centered, product shot'
        ),
        'note': 'icon: linh kiện điện tử',
        'kind': 'icon',
    },
    'icon-hydrazine': {
        'prompt': (
            'a small white cylindrical fuel tank with a valve on top, '
            'stencilled bands around the body, slightly dented, '
            'isolated on a plain dark background, centered, product shot'
        ),
        'note': 'icon: bình hydrazine',
        'kind': 'icon',
    },
    'icon-media': {
        'prompt': (
            'a single black vinyl record disc standing upright and fully visible as a complete circle, '
            'concentric grooves clearly catching warm light, a paper label in the centre with a spindle hole, '
            'the disc tilted slightly so the whole circle silhouette reads clearly, '
            'isolated on a plain dark background, centered, product shot'
        ),
        'note': 'icon: đĩa nhạc cũ',
        'kind': 'icon',
    },
    'icon-solar': {
        'prompt': (
            'a folded portable solar panel array, '
            'blue photovoltaic cells in a metal frame, dust on the surface, '
            'isolated on a plain dark background, centered, product shot'
        ),
        'note': 'icon: tấm pin mặt trời',
        'kind': 'icon',
    },
    'icon-cable': {
        'prompt': (
            'a coiled length of thick braided power cable, '
            'connectors at both ends, '
            'isolated on a plain dark background, centered, product shot'
        ),
        'note': 'icon: dây cáp',
        'kind': 'icon',
    },
    'icon-filter': {
        'prompt': (
            'a cylindrical air filter cartridge with a mesh screen, '
            'grey metal casing with visible dust trapped in the mesh, '
            'isolated on a plain dark background, centered, product shot'
        ),
        'note': 'icon: bình lọc khí',
        'kind': 'icon',
    },
    'icon-toolbox': {
        'prompt': (
            'a metal toolbox with its lid open, '
            'wrenches and a screwdriver visible inside, scuffed red paint, '
            'isolated on a plain dark background, centered, product shot'
        ),
        'note': 'icon: hộp dụng cụ',
        'kind': 'icon',
    },
    'icon-family-photo': {
        'prompt': (
            'a small creased paper photograph lying face up, '
            'two people standing close together in front of a kitchen window, '
            'the image itself worn and slightly faded, one corner bent, '
            'a strip of black tape still stuck to the top edge, '
            'isolated on a plain dark background, centered, product shot'
        ),
        'note': 'icon: tấm ảnh gia đình',
        'kind': 'icon',
    },

    # ---------- ảnh cho đoạn hồi tưởng gia đình ----------
    # Ba cảnh này chỉ hiện khi người chơi mở túi đồ và bấm tấm ảnh,
    # tức là nằm trong gameplay chứ không nằm ở màn mở đầu.

    'bg-houston-kitchen': {
        'prompt': (
            'small Houston apartment kitchen at night, a bare table with two '
            'chairs, half packed cardboard boxes stacked against the counter, '
            'a fridge covered in paper and one taped photograph, '
            'a single warm ceiling light, empty wall calendar'
        ),
        'note': 'hồi tưởng: bếp Houston đêm trước khi đi',
        'kind': 'scene',
    },
    'bg-moving-boxes': {
        'prompt': (
            'narrow apartment hallway filled with stacked cardboard moving '
            'boxes, one box in the middle with a strip of tape across the '
            'lid and a marking pen resting on top, '
            'warm lamp light from an open doorway, bare wooden floor'
        ),
        'note': 'hồi tưởng: đóng thùng đồ',
        'kind': 'scene',
    },
    'bg-farewell-door': {
        'prompt': (
            'apartment front door standing open at dawn, a duffel bag on the '
            'floor of the threshold, cold blue light from the corridor and '
            'warm light from inside the flat, coat hooks on the wall, '
            'no people in frame'
        ),
        'note': 'hồi tưởng: chia tay ở cửa',
        'kind': 'scene',
    },
}


# ---------------------------------------------------------------- gọi API

def find_key():
    """Tìm API key có quyền tạo ảnh.

    Thứ tự ưu tiên quan trọng: file secrets trong workspace đứng TRƯỚC
    biến môi trường. Lý do: máy này có hai key Vilao khác nhau. Key
    trong .env là key cũ chỉ dùng cho model chữ, gọi tạo ảnh trả 403.
    Key trong workspace/user-*/secrets/vilao-api-key.txt mới là key có
    đăng ký model ảnh. Đọc nhầm key là mất cả buổi debug.
    """
    candidates = []

    # 1. file secrets của workspace, nơi key đúng đang nằm
    workspace_keys = sorted(Path.home().glob('workspace/user-*/secrets/vilao-api-key.txt'))
    for p in workspace_keys:
        if p.exists():
            text = p.read_text(encoding='utf-8-sig', errors='ignore')
            m = re.search(r'sk-[A-Za-z0-9\-_]+', text)
            if m:
                candidates.append(('workspace-secrets', m.group(0)))

    # 2. biến môi trường
    env_key = os.environ.get('HERMES_MODEL_PROVIDER_API_KEY')
    if env_key:
        candidates.append(('env', env_key))

    # 3. .env của hermes
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
    """Gọi một lần. Trả (ảnh bytes, None) hoặc (None, lỗi)."""
    payload = json.dumps({
        'model': MODEL,
        'prompt': prompt,
        'n': 1,
    }).encode('utf-8')

    req = urllib.request.Request(
        f'{API_BASE}/images/generations',
        data=payload,
        headers={
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
        },
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


def generate(key, name, spec):
    """Sinh một asset, có thử lại khi gặp lỗi tạm thời."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f'{name}.png'

    if out_path.exists() and out_path.stat().st_size > 5000:
        print(f'  [{name}] đã có, bỏ qua. Dùng --force để làm lại.')
        return True

    print(f'  [{name}] {spec["note"]}')
    print(f'    đang gửi yêu cầu, chờ 30 tới 90 giây...')

    # Ghép khối style chung vào mọi prompt để cả bộ ảnh cùng một giọng.
    # Cảnh có người thì dùng biến thể riêng, xem spec['style'].
    full_prompt = spec['prompt'] + ', ' + spec.get('style', STYLE)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        t0 = time.time()
        timeout = TIMEOUT_FIRST if attempt == 1 else TIMEOUT_NEXT
        img, err = call_api(key, full_prompt, timeout)
        elapsed = time.time() - t0

        if img:
            out_path.write_bytes(img)
            size_kb = len(img) / 1024
            print(f'    xong sau {elapsed:.0f} giây, {size_kb:.0f} KB')
            return True

        status = err.get('status', 0) if err else 0
        detail = (err or {}).get('detail', 'không rõ')

        # Lỗi quyền hoặc model không tồn tại thì dừng ngay, thử lại vô nghĩa
        if status == 403:
            print(f'    DỪNG: chưa đăng ký model. {detail[:160]}')
            return False
        if status == 401:
            print(f'    DỪNG: key không hợp lệ. {detail[:160]}')
            return False

        if status in RETRY_STATUSES or status == 0:
            if attempt < MAX_ATTEMPTS:
                wait = BACKOFF[min(attempt - 1, len(BACKOFF) - 1)]
                wait += random.randint(0, 4)
                print(f'    lần {attempt} lỗi {status}, chờ {wait} giây rồi thử lại')
                time.sleep(wait)
                continue

        print(f'    HỎNG sau {attempt} lần: {status} {detail[:160]}')
        return False

    return False


def main():
    ap = argparse.ArgumentParser(description='Sinh ảnh cho game qua API Vilao')
    ap.add_argument('name', nargs='?', help='tên asset cần sinh')
    ap.add_argument('--list', action='store_true', help='liệt kê asset có sẵn')
    ap.add_argument('--all', action='store_true', help='sinh toàn bộ')
    ap.add_argument('--force', action='store_true', help='làm lại dù đã có')
    args = ap.parse_args()

    if args.list:
        print('Asset có sẵn:')
        for k, v in ASSETS.items():
            done = 'đã có' if (OUT_DIR / f'{k}.png').exists() else 'chưa có'
            print(f'  {k:16} {done:8} {v["note"]}')
        return

    if args.force:
        for k in (ASSETS if args.all else [args.name] if args.name else []):
            p = OUT_DIR / f'{k}.png'
            if p.exists():
                p.unlink()
                print(f'  đã xoá {k}.png cũ')

    key = find_key()
    if not key:
        print('Không tìm thấy API key. Đặt HERMES_MODEL_PROVIDER_API_KEY trong môi trường.')
        sys.exit(1)

    print(f'Model: {MODEL}')
    print(f'Ra: {OUT_DIR}')
    print('')

    if args.all:
        targets = list(ASSETS.items())
    elif args.name:
        if args.name not in ASSETS:
            print(f'Không có asset tên {args.name}. Dùng --list để xem danh sách.')
            sys.exit(1)
        targets = [(args.name, ASSETS[args.name])]
    else:
        ap.print_help()
        return

    ok = 0
    fail = []
    for i, (name, spec) in enumerate(targets, 1):
        print(f'({i}/{len(targets)})', end=' ')
        if generate(key, name, spec):
            ok += 1
        else:
            fail.append(name)
        if i < len(targets):
            time.sleep(3)   # nghỉ giữa các ảnh, tránh bị chặn vì gửi dồn

    print('')
    print(f'Xong: {ok}/{len(targets)} ảnh')
    if fail:
        print(f'Hỏng: {", ".join(fail)}')
        print('Chạy lại lệnh trên để thử tiếp, ảnh đã có sẽ được bỏ qua.')


if __name__ == '__main__':
    main()
