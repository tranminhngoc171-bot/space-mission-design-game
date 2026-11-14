#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply-script-txt.py
Đọc file kịch bản TXT (bản Thiện Nhân biên tập tay) rồi ghi ngược
vào src/story-data.js, giữ nguyên cấu trúc và thứ tự cảnh.

Chạy:  python scripts/apply-script-txt.py
Đọc:   <Desktop>/NASA-Game-Kich-Ban.txt
Ghi:   src/story-data.js

Quy ước đọc file TXT:
  - Khối bắt đầu bằng dòng '----' và có dòng 'LƯỢT nn'
  - Dòng 'VI: ...' là bản tiếng Việt
  - Dòng 'EN: ...' là bản tiếng Anh
  - Dòng '> Tên Nhân Vật  (Chức danh)' là người nói
  - Dòng '[LOG]' đánh dấu lượt nhật ký
  - Dòng '[NHẬP TÊN NGƯỜI CHƠI]' đánh dấu lượt nhập tên
  - Dòng '#  CẢNH: ...' và '#  Tệp tranh: <key>' đánh dấu cảnh mới

Nếu file TXT thiếu một lượt nào, lượt đó giữ nguyên như cũ.
Nếu file TXT có lượt mới, nó được thêm vào đúng vị trí.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'src' / 'story-data.js'
DUMP = Path(os.environ.get('TMPDIR', '/tmp')) / 'story-dump-apply.json'


def find_desktop():
    home = Path.home()
    for cand in [home / 'Desktop', home / 'OneDrive' / 'Desktop',
                 home / 'OneDrive' / 'Máy tính' / 'Desktop']:
        if cand.is_dir():
            return cand
    return home


def load_current():
    """Đọc dữ liệu hiện tại của game để lấy phần không có trong TXT."""
    js = (
        "import('./story-data.js').then(m => {"
        "  const out = { crew: m.CREW, role: m.PLAYER_ROLE, story: m.STORY };"
        f"  require('fs').writeFileSync({json.dumps(str(DUMP))}, JSON.stringify(out), 'utf8');"
        "}).catch(e => { console.error(e.message); process.exit(1); });"
    )
    r = subprocess.run(['node', '-e', js], cwd=str(ROOT / 'src'),
                       capture_output=True, text=True)
    if r.returncode != 0:
        print('Lỗi đọc story-data.js:', r.stderr)
        sys.exit(1)
    return json.loads(DUMP.read_text(encoding='utf-8'))


def parse_txt(path):
    """Tách file TXT thành danh sách lượt, mỗi lượt có cảnh và nội dung."""
    text = path.read_text(encoding='utf-8-sig')
    lines = text.splitlines()

    beats = []
    scene = None
    cur = None

    for raw in lines:
        line = raw.rstrip()

        # đổi cảnh
        m = re.match(r'^#\s+Tệp tranh:\s*(\S+)', line)
        if m:
            scene = m.group(1).strip()
            continue

        # mở lượt mới
        if re.match(r'^LƯỢT\s+\d+', line):
            if cur:
                beats.append(cur)
            cur = {'scene': scene, 'who': None, 'kind': 'narration',
                   'vi': '', 'en': '', 'extra': {}}
            continue

        if cur is None:
            continue

        if line == '[LOG]':
            cur['kind'] = 'log'
        elif line == '[NHẬP TÊN NGƯỜI CHƠI]':
            cur['kind'] = 'name'
        elif line.startswith('> '):
            cur['kind'] = 'dialogue'
            cur['who'] = line[2:].split('(')[0].strip()
        elif line.startswith('VI: '):
            cur['vi'] = line[4:].strip()
        elif line.startswith('EN: '):
            cur['en'] = line[4:].strip()
        elif line.startswith('Gợi ý VI: '):
            cur['extra']['hint_vi'] = line[len('Gợi ý VI: '):].strip()
        elif line.startswith('Gợi ý EN: '):
            cur['extra']['hint_en'] = line[len('Gợi ý EN: '):].strip()
        elif line.startswith('Ô trống VI: '):
            cur['extra']['ph_vi'] = line[len('Ô trống VI: '):].strip()
        elif line.startswith('Ô trống EN: '):
            cur['extra']['ph_en'] = line[len('Ô trống EN: '):].strip()

    if cur:
        beats.append(cur)

    return beats


def match_crew(name, crew):
    """Tìm id nhân vật từ tên đầy đủ hoặc tên ngắn."""
    if not name:
        return None
    n = name.strip().lower()
    for c in crew:
        if c.get('full', '').lower() == n or c.get('name', '').lower() == n:
            return c['id']
    return None


def esc(s):
    """Thoát chuỗi cho JS, giữ nguyên nội dung."""
    return s.replace('\\', '\\\\').replace("'", "\\'")


def build_js(data, beats):
    crew = data['crew']
    role = data['role']

    out = []
    A = out.append

    A('/* ============================================================')
    A('   story-data.js')
    A('   Toàn bộ lời kể của màn mở đầu, viết song ngữ.')
    A('')
    A('   >>> KHI THÊM LƯỢT MỚI, BẮT BUỘC ĐIỀN CẢ vi VÀ en <<<')
    A('   Thiếu một bên là lỗi. Không để dịch sau.')
    A('')
    A('   Bốn loại lượt:')
    A("     type: 'log'        dòng nhật ký kỹ thuật, số liệu, mốc thời gian")
    A("     type: 'narration'  lời kể")
    A("     type: 'name'       bảng hỏi tên người chơi")
    A("     type: 'dialogue'   một nhân vật nói")
    A('')
    A('   Trong text: {name} là tên người chơi, *chữ* là in nghiêng.')
    A('   art là KHE ẢNH, trỏ tới key trong art.js.')
    A('')
    A('   File này được sinh tự động từ file kịch bản TXT trên Desktop.')
    A('   Muốn sửa lời thoại thì sửa file TXT, đừng sửa file này.')
    A('   ============================================================ */')
    A('')
    A('export const CREW = [')

    for c in crew:
        A('  {')
        A(f"    id: '{c['id']}',")
        A(f"    name: '{esc(c['name'])}',")
        A(f"    full: '{esc(c['full'])}',")
        A(f"    role: {{ vi: '{esc(c['role']['vi'])}', en: '{esc(c['role']['en'])}' }},")
        A(f"    color: '{c['color']}',")
        A(f"    short: '{c['short']}',")
        A('  },')
    A('];')
    A('')
    A('export const PLAYER_ROLE = {')
    A(f"  vi: '{esc(role['vi'])}',")
    A(f"  en: '{esc(role['en'])}',")
    A('};')
    A('')
    A('export const STORY = [')

    current_scene = None
    for b in beats:
        if b['scene'] and b['scene'] != current_scene:
            current_scene = b['scene']
            A('')
            A(f"  /* ═══ cảnh: {current_scene} ═══ */")
            A('')

        vi = esc(b['vi'])
        en = esc(b['en'])
        art_line = f"    art: '{current_scene}'," if current_scene else ''

        if b['kind'] == 'log':
            A('  {')
            A("    type: 'log',")
            A('    text: {')
            A(f"      vi: '{vi}',")
            A(f"      en: '{en}',")
            A('    },')
            A('  },')

        elif b['kind'] == 'dialogue':
            who = match_crew(b['who'], crew) or 'lewis'
            A('  {')
            A("    type: 'dialogue',")
            A(f"    who: '{who}',")
            A('    text: {')
            A(f"      vi: '{vi}',")
            A(f"      en: '{en}',")
            A('    },')
            A('  },')

        elif b['kind'] == 'name':
            x = b['extra']
            A('  {')
            A("    type: 'name',")
            A(f"    prompt: {{ vi: '{vi}', en: '{en}' }},")
            A(f"    hint: {{ vi: '{esc(x.get('hint_vi',''))}', en: '{esc(x.get('hint_en',''))}' }},")
            A(f"    placeholder: {{ vi: '{esc(x.get('ph_vi',''))}', en: '{esc(x.get('ph_en',''))}' }},")
            A('  },')

        else:
            A('  {')
            A("    type: 'narration',")
            if art_line:
                A(art_line)
            A('    text: {')
            A(f"      vi: '{vi}',")
            A(f"      en: '{en}',")
            A('    },')
            A('  },')

    A('];')
    A('')

    return '\n'.join(out)


def main():
    txt = find_desktop() / 'NASA-Game-Kich-Ban.txt'
    if not txt.exists():
        print(f'Không tìm thấy file kịch bản: {txt}')
        print('Chạy scripts/build-script-txt.py trước để sinh ra file này.')
        sys.exit(1)

    data = load_current()
    beats = parse_txt(txt)

    if not beats:
        print('File kịch bản không có lượt nào. Dừng để tránh xoá sạch dữ liệu.')
        sys.exit(1)

    # kiểm tra thiếu bản dịch
    missing = [(i + 1, b) for i, b in enumerate(beats) if not b['vi'] or not b['en']]
    if missing:
        print('CẢNH BÁO: những lượt sau thiếu bản Việt hoặc Anh:')
        for n, b in missing:
            which = 'Việt' if not b['vi'] else 'Anh'
            print(f'  lượt {n}: thiếu bản {which}')
        print('Vẫn ghi tiếp, nhưng nên bổ sung cho đủ.')

    new_js = build_js(data, beats)
    DATA.write_text(new_js, encoding='utf-8')

    # kiểm tra cú pháp ngay
    r = subprocess.run(['node', '--check', str(DATA)], capture_output=True, text=True)
    if r.returncode != 0:
        print('LỖI CÚ PHÁP sau khi ghi:', r.stderr)
        sys.exit(1)

    print(f'Đã ghi {DATA}')
    print(f'  {len(beats)} lượt')
    print('  cú pháp hợp lệ')
    print('')
    print('Bước tiếp: mở game kiểm tra, rồi báo Hân đẩy lên GitHub.')


if __name__ == '__main__':
    main()
