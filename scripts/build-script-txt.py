#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build-script-txt.py
Sinh file kịch bản TXT từ src/story-data.js để Thiện Nhân biên tập tay.

Chạy:  python scripts/build-script-txt.py
Ghi ra: <Desktop>/NASA-Game-Kich-Ban.txt

File TXT này là bản dễ đọc và dễ sửa. Muốn đổi lời thoại thì sửa
file TXT, rồi chạy scripts/apply-script-txt.py để đổ ngược vào game.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DUMP = Path(os.environ.get('TMPDIR', '/tmp')) / 'story-dump.json'

# Nhãn cảnh: mô tả bối cảnh và không khí của từng tranh, để người
# biên tập biết mình đang viết cho khung hình nào.
SCENE_LABEL = {
    'earth-home':   ('Trái Đất, đêm trước ngày đi', 'Nhà Watney ở Houston. Bếp tối, đèn vàng ấm hắt từ cửa sổ. Đồ đạc đóng thùng gần hết, chỉ còn bàn ghế và tờ lịch trên tường.'),
    'farewell':     ('Tạm biệt gia đình', 'Hành lang trước cửa nhà. Watney mặc bộ đồ bay, vợ đứng đối diện. Ánh sáng vàng từ một phía. Vali dưới chân.'),
    'launchpad':    ('Bệ phóng, sáu giờ trước giờ G', 'Tên lửa đứng trên bệ phóng, giàn giáo hai bên. Trời chạng vạng chuyển từ tím sang xanh đậm, vài ngôi sao mờ.'),
    'mars-surface': ('Đồng bằng Acidalia Planitia, Sol 6', 'Bề mặt sao Hỏa. Đất đỏ, đá rải rác, bầu trời vàng nhợt. Xa xa là tàu đổ bộ MAV và khoang trú ẩn.'),
    'storm-coming': ('Cơn bão cát ập tới', 'Bức tường bụi đỏ cao kịch trần, cuồn cuộn về phía trước. Mọi thứ mờ dần trong cát.'),
    'storm-impact': ('Tai nạn, mảnh ăng-ten', 'Bụi dày đặc, tầm nhìn gần như bằng không. Một mảnh ăng-ten kim loại đang xoay trong gió.'),
    'departure':    ('MAV cất cánh, năm người rời đi', 'Tàu đổ bộ rời bệ phóng, để lại vệt khói và cát đỏ. Bên dưới là bề mặt hoang vắng.'),
    'awake':        ('Watney tỉnh dậy một mình, Sol 19', 'Trong khoang trú ẩn. Ánh sáng nhân tạo, các giá treo đồ trống. Ngoài cửa sổ chỉ có đất đỏ và bầu trời vàng.'),
}


def load_story():
    """Đọc story-data.js bằng node, ghi JSON tạm, rồi nạp vào Python."""
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


def find_desktop():
    """Tìm thư mục Desktop thật, kể cả khi OneDrive đã chiếm."""
    home = Path.home()
    for cand in [home / 'Desktop', home / 'OneDrive' / 'Desktop',
                 home / 'OneDrive' / 'Máy tính' / 'Desktop']:
        if cand.is_dir():
            return cand
    return home


def main():
    data = load_story()
    story = data['story']
    crew = {c['id']: c for c in data['crew']}

    lines = []
    A = lines.append

    A('=' * 74)
    A('  SPACE MISSION DESIGN GAME  ·  KỊCH BẢN MÀN MỞ ĐẦU')
    A('  NASA Space Apps Challenge 2026')
    A('=' * 74)
    A('')
    A('CÁCH SỬA FILE NÀY')
    A('')
    A('  Đây là bản dễ đọc của toàn bộ chữ hiện trên màn hình game.')
    A('  Cậu cứ sửa trực tiếp: xóa câu, thêm câu, đổi lời thoại.')
    A('  Sửa xong thì báo Hân, Hân sẽ đổ ngược vào game và đẩy lên GitHub.')
    A('')
    A('  Vài quy ước nhỏ:')
    A('    - Mỗi lượt có khối [VI] và [EN]. Giữ đủ cả hai.')
    A('    - {ten} trong câu sẽ tự đổi thành tên người chơi.')
    A('    - Dòng bắt đầu bằng "> " là lời nhân vật đang nói.')
    A('    - Dòng không có dấu > là lời kể.')
    A('    - Dòng có [LOG] là nhật ký kỹ thuật, hiện bằng chữ đơn cách.')
    A('    - Muốn bỏ một lượt thì xóa cả khối của lượt đó, kể cả dòng ---- .')
    A('    - Muốn thêm lượt thì copy một khối rồi sửa nội dung.')
    A('')
    A('  Đừng sửa các dòng ==== và ---- vì Hân dùng chúng để tách lượt.')
    A('')
    A('=' * 74)
    A('')
    A('NHÂN VẬT')
    A('')
    for c in data['crew']:
        A(f"  {c['name']:<12} {c['full']:<20} {c['role']['vi']}")
    A('')
    A(f"  Vai của người chơi: {data['role']['vi']}")
    A('')
    A('=' * 74)
    A('')
    A('')

    current_scene = None
    beat_no = 0

    for beat in story:
        btype = beat.get('type')
        art = beat.get('art')

        # Chèn khối bối cảnh mỗi khi đổi cảnh
        if art and art != current_scene:
            current_scene = art
            title, desc = SCENE_LABEL.get(art, (art, ''))
            A('#' * 74)
            A(f'#  CẢNH: {title}')
            A(f'#  Tệp tranh: {art}')
            A('#' * 74)
            if desc:
                A('')
                A('  Bối cảnh: ' + desc)
                A('')

        beat_no += 1
        A('-' * 74)
        A(f'LƯỢT {beat_no:02d}' + (f'   [cảnh: {art}]' if art else ''))
        A('-' * 74)

        if btype == 'log':
            A('[LOG]')
            A('VI: ' + beat['text']['vi'])
            A('EN: ' + beat['text']['en'])
            A('')

        elif btype == 'dialogue':
            who = crew.get(beat.get('who'), {})
            name = who.get('full') or who.get('name') or beat.get('who', '')
            role = (who.get('role') or {}).get('vi', '')
            A(f'> {name}' + (f'  ({role})' if role else ''))
            A('VI: ' + beat['text']['vi'])
            A('EN: ' + beat['text']['en'])
            A('')

        elif btype == 'name':
            A('[NHẬP TÊN NGƯỜI CHƠI]')
            A('VI: ' + beat['prompt']['vi'])
            A('EN: ' + beat['prompt']['en'])
            A('Gợi ý VI: ' + beat.get('hint', {}).get('vi', ''))
            A('Gợi ý EN: ' + beat.get('hint', {}).get('en', ''))
            A('Ô trống VI: ' + beat.get('placeholder', {}).get('vi', ''))
            A('Ô trống EN: ' + beat.get('placeholder', {}).get('en', ''))
            A('')

        else:  # narration
            A('VI: ' + beat['text']['vi'])
            A('EN: ' + beat['text']['en'])
            A('')

    A('=' * 74)
    A('  HẾT KỊCH BẢN')
    A('=' * 74)
    A('')

    out_path = find_desktop() / 'NASA-Game-Kich-Ban.txt'
    out_path.write_text('\n'.join(lines), encoding='utf-8-sig')

    print(f'Đã ghi: {out_path}')
    print(f'  {beat_no} lượt, {len(SCENE_LABEL)} cảnh')
    print(f'  {out_path.stat().st_size:,} byte')


if __name__ == '__main__':
    main()
