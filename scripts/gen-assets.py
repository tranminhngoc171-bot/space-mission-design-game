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
# Sprite có nền trong suốt (char-*, icon-sprite) ghi ra thư mục riêng: nếu để
# chung gen/ thì process-assets.py quét gen/icon-*.png và ghi đè icon trong
# suốt bằng bản nền tối đục của pipeline icon cũ.
SPRITE_DIR = ROOT / 'src' / 'assets' / 'gen-sprites'

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

# ---------- tám cảnh kết thúc thua ----------
# Yêu cầu riêng: truyện tranh khoa học viễn tưởng toàn màu, ánh sáng điện
# ảnh, đổ bóng sâu, nét vẽ sắc. Khác COMIC_BASE ở chỗ khoá bảng màu Sao Hỏa
# (đỏ cam đất, đen xám bụi, trắng lạnh, hổ phách #e8a33d, xanh lơ #4fb8c9)
# để tám tranh đứng cạnh nhau trong màn kết thúc vẫn là một bộ.
# Nhấn mạnh "no text" nhiều lần: model hay vẽ chữ lên màn hình thiết bị, mà
# luật của game là tranh tuyệt đối không có chữ.
ENDING_STYLE = (
    'full-color science fiction comic book illustration, sharp clean ink '
    'linework, cinematic dramatic lighting with a strong single key light, '
    'deep black shadows, rich saturated colour, detailed rendering, '
    'widescreen 16:9 composition, '
    'palette of rust orange Mars dust, charcoal grey grit, cold white light, '
    'amber highlight #E8A33D and pale cyan #4FB8C9 accents, '
    'absolutely no text, no letters, no numbers, no labels, no signage, '
    'no writing on any screen or wall, no logo, no watermark, no border, '
    'no frame, no caption box'
)


# Bộ này theo Art Direction mới, không theo NASA concept art book cũ: tranh
# phẳng, nét sạch, đọc được ở cỡ nhỏ, bảng màu khoá cứng 5 màu. Dùng chung
# cho sprite nhân vật, icon vật phẩm và tranh popup để ba nhóm không lệch
# giọng với nhau.
STYLE_HARD = (
    'Grounded Hard Sci-Fi 2D Illustration, clean crisp lineart, '
    'painterly atmospheric lighting kept subtle and controlled, '
    '60 Seconds cutaway-base clarity with The Martian NASA engineering '
    'aesthetic, readable silhouette at thumbnail size, '
    'palette restricted to martian rust orange #C84B31, spaceship steel grey '
    '#1E242B, NASA equipment white #E2E8F0, warning amber #F59E0B, '
    'data-screen cyan #38BDF8'
)

# Icon vật phẩm: khối style chép từ gen-icon-sprite.py, giữ nguyên cách xin
# nền xám phẳng để bước hậu kỳ tách alpha. Hậu kỳ của bộ này nằm trong
# process-assets.py (process_icon_sprite), không dùng process_icon vì hàm
# đó đệm nền tối đục và vẽ khung chữ nhật quanh canvas.
ICON_KEY_BG = (
    'background is a single flat uniform mid grey #7A7A7A, '
    'no gradient, no vignette, no floor, no shadow cast on the background'
)

STYLE_ICON_SPRITE = (
    STYLE_HARD + ', '
    'flat cel shaded colour fills with at most two shading tones per face, '
    'bold uniform dark ink outline running cleanly around the whole '
    'silhouette and along every major form break, crisp readable shapes, '
    'isolated object on transparent background, centered, '
    'single object only, fully inside frame with empty margin on all sides, '
    'no text, no watermark, no border, no frame, no ground shadow, '
    'no background scenery, no people'
)

# Sprite nhân vật: KHÔNG được mang câu "no people, no faces, no hands" của
# STYLE_CLEAN, nếu không model trả về khung cảnh trống. Nền vẫn phải phẳng
# một màu để hậu kỳ tách alpha, và phải là ảnh toàn thân đứng trong khung
# dọc, cùng tỉ lệ cho cả ba tư thế.
#
# MÀU NỀN: xanh lơ nhạt đặc #B8D8D0, không dùng xám #7A7A7A nữa. Hai lý do:
# (1) bộ đồ có mảng trắng xám NASA #E2E8F0 rất gần xám nền, hiệu màu chỉ
# khoảng 40 đơn vị nên mặt nạ alpha bị ăn mòn vào vai và ống chân; (2) nền
# xám trung tính trùng với màu giày xám nhạt và với ánh sáng phụ, nên
# silhouette khó dò. Xanh lơ nhạt đứng xa cả da nâu, cam gỉ và trắng xám
# về mặt hiệu màu, tách sạch mà không cần chỉnh ngưỡng.
#
# ĐÓNG KHUNG: phải nói rõ tỉ lệ khung dọc và tỉ lệ người chiếm khung. Bản
# trước chỉ nói "head to boots inside the frame" mà không nói người chiếm
# bao nhiêu phần khung, model hiểu là phải lấp đầy khung nên phóng người
# lên và tràn chân ra ngoài mép dưới.
CHAR_BG_HEX = '#B8D8D0'

STYLE_CHAR = (
    STYLE_HARD + ', '
    'full body character sprite of one single astronaut, '
    'vertical portrait frame, the figure standing upright and centered, '
    'full body shot, entire figure visible from the top of the head to the '
    'soles of the boots, generous empty margin above the head and below the '
    'boots, the character occupies only about 80 percent of the frame height, '
    'feet fully visible wearing work boots, '
    'both boots and their soles fully visible with clear empty background '
    'space below the feet, '
    'not cropped at the legs, not cut off at the ankles, no missing feet, '
    'nothing floating in the empty space beside the body, '
    'no stray marks, no props floating in the air, '
    f'background is a single flat uniform light cyan-green {CHAR_BG_HEX}, '
    'uniform flat background, perfectly smooth and even, '
    'no gradient, no vignette, no floor plane, no horizon, no scenery, '
    'no props behind the figure, no shadows cast on the background, '
    'clean crisp silhouette, no text, no watermark, no border, no frame, '
    'no extra limbs, no second person'
)

# Tranh popup: cảnh nội thất 16:9, có người vận hành nhưng mặt khuất hoặc
# chỉ thấy bóng lưng, nên không dùng STYLE_CLEAN khoá con người.
STYLE_POPUP = (
    STYLE_HARD + ', '
    'cinematic 16:9 interior scene, wide readable composition that stays '
    'clear behind a popup panel, deep charcoal shadows with warm rust bounce '
    'light, no text, no letters, no numbers, no logo, no watermark, no border, '
    'no frame'
)

# Mô tả nhân vật dùng CHUNG nguyên văn cho cả ba tư thế. Đây là điều quan
# trọng nhất của bộ sprite: model không nhận ảnh tham chiếu, nên chỉ có một
# khối mô tả cố định, dài và cụ thể mới giữ ba tư thế là cùng một người,
# cùng bộ đồ, cùng tỉ lệ. Sửa khối này là phải sinh lại cả ba.
CHAR_LOOK = (
    'the same recurring character in all poses: a stocky astronaut in his '
    'mid thirties, 1.8 metres tall, broad shoulders, short cropped dark brown '
    'buzz cut hair, square jaw with light stubble, warm medium brown skin, '
    'thick straight eyebrows, a small pale scar above the left eyebrow, '
    'identical face and identical head shape in every pose, '
    'wearing the same light duty Mars habitat coverall, not a heavy EVA '
    'pressure suit: a soft slate grey-blue one piece utility coverall, the '
    'trousers exactly the same slate grey-blue as the jacket sleeves, '
    'with a pale NASA equipment white chest panel, a diagonal front zip, a '
    'rust orange shoulder yoke and rust orange knee patches, sleeves rolled to '
    'the elbow showing bare forearms, a small amber rectangle patch badge on '
    'the right chest, a thin cyan status strip on the left wrist cuff, a fabric '
    'tool belt with two pouches, scuffed grey utility boots with pale soles, '
    'same costume, same colours, same body proportions in every pose, '
    'do not change the costume design between poses'
)

# ------------------------------------------------- màn mở đầu dạng truyện tranh
# Mười hai khung của đoạn phim mở đầu kể bằng tranh, không lời thoại.
# Khối này KHÁC hẳn STYLE_LOOK ở trên: tranh truyện in màu, nét mực đen
# sắc, đổ bóng sâu, không phải tranh concept mờ ảo. Vì vậy không dùng
# STYLE_CLEAN cho các khung này: STYLE_CLEAN có 'no people, no faces,
# no hands' và model sẽ vẽ ra phong cảnh trống, mất hẳn phần kể chuyện.
# Chỉ hai khung 01 và 12 là cảnh trống nên mới được phép khoá con người.
COMIC_BASE = (
    'full-color graphic novel illustration, sharp clean ink linework, '
    'deep shadows, cinematic dramatic lighting, science fiction comic book '
    'style, rich saturated colors, detailed rendering, no text, no letters, '
    'no watermark, no logo, no border, no frame'
)

COMIC_PALETTE = (
    'palette of rust red and burnt orange Mars dust, charcoal grey storm '
    'shade, cold white light from helmet lamps, hot red engine glow, '
    'widescreen 16:9 comic panel composition'
)

# Cảnh trống: chỉ dùng cho khung 01 và 12.
COMIC_EMPTY = COMIC_BASE + ', ' + COMIC_PALETTE + ', no people, no figures'

# Cảnh có phi hành gia, mặt khuất sau kính mũ.
COMIC_CREW = (
    COMIC_BASE + ', ' + COMIC_PALETTE + ', '
    'astronauts in bulky white EVA pressure suits with dusty mirrored visors'
)

# Cảnh có một khuôn mặt nhìn rõ sau kính mũ.
COMIC_FACE = (
    COMIC_BASE + ', ' + COMIC_PALETTE + ', '
    'one astronaut in a white EVA suit, face clearly visible behind a clear '
    'scratched helmet visor'
)

# Góc nhìn thứ nhất: có bàn tay trong khung nên không được khoá tay.
COMIC_POV = (
    COMIC_BASE + ', ' + COMIC_PALETTE + ', '
    'first person point of view, one gloved hand and forearm of a white EVA '
    'suit reaching into the lower edge of the frame'
)

# Tỉ lệ khung: dùng 16:9 cho ảnh nền, 1:1 cho icon.
# Model có thể bỏ qua tham số size, nên vẫn phải crop ở hậu kỳ.

# ---------- năm ảnh nền cho Giai đoạn 2 ----------
# Cùng giọng với ENDING_STYLE (truyện tranh khoa học viễn tưởng toàn màu,
# ánh sáng điện ảnh, đổ bóng sâu, nét vẽ sắc) để Phase 2 đứng cạnh Phase 1
# không bị lệch chất. Khác một điểm: các ảnh này là LỚP NỀN nằm sau nội
# dung SVG, nên phải tối và ít chi tiết ở vùng giữa khung, nếu không chữ
# và thanh đo phía trên sẽ chìm. Vì vậy thêm câu "uncluttered midtones in
# the centre of frame" và cấm mọi chữ.
# Cũng cấm tuyệt đối mọi chữ trên màn hình thiết bị: model rất hay vẽ chữ
# giả lên màn hình điều khiển, mà luật của game là tranh không có chữ.
P2_SCENE_STYLE = (
    'full-color science fiction comic book illustration, sharp clean ink '
    'linework, cinematic dramatic lighting with a strong single key light, '
    'deep black shadows, rich saturated colour, detailed rendering, '
    'widescreen 16:9 composition, uncluttered midtones in the centre of '
    'frame so interface text can sit on top, '
    'palette of rust orange Mars dust, charcoal grey grit, cold white light, '
    'amber highlight #E8A33D and pale cyan #4FB8C9 accents, '
    'absolutely no text, no letters, no numbers, no labels, no signage, '
    'no writing on any screen or wall, no logo, no watermark, no border, '
    'no frame, no caption box'
)

# Phòng điều khiển có người trực: chỉ thấy bóng người ngồi quay lưng hoặc
# nghiêng, không cần mặt rõ. Nếu khoá "no people" thì khung hình thành
# căn phòng trống, mất hẳn không khí căng thẳng đang chờ.
P2_SCENE_STYLE_CREW = P2_SCENE_STYLE.replace(
    'no logo, no watermark, no border, no frame, no caption box',
    'flight controllers seen from behind as dark silhouettes, faces not '
    'visible, no logo, no watermark, no border, no frame, no caption box'
)

# ------------------------------------------- chuyển tiếp Giai đoạn 1 sang 2
# Bảy khung bg-im-* của bộ mười ba khung chuyển tiếp. Hai sub sinh hai nửa
# bộ ảnh chạy song song, nên khối mô tả nhân vật và khối phong cách phải
# chép nguyên văn giống nhau ở cả hai nơi; lệch một chữ là hai nửa bộ ảnh
# hiện ra hai phòng điều khiển khác nhau.
#
# IM_CHARS là khối mô tả nhân vật DÙNG CHUNG, không được sửa, không được
# rút gọn: model không nhận ảnh tham chiếu nên chỉ có một khối chữ dài và
# cố định mới giữ viên kiểm soát và giám đốc nhiệm vụ là cùng một người
# qua nhiều khung.
IM_CHARS = (
    'consistent character design: NASA flight controller is a young man in '
    'his late twenties with short dark hair, rectangular black-framed '
    'glasses, white dress shirt with a dark navy tie, NASA badge clipped to '
    'his chest pocket; the NASA mission director is a man in his late '
    'fifties with salt and pepper grey hair, wearing a light grey flight '
    'director vest over a white shirt with rolled up sleeves, stern '
    'determined jaw; the control room has two huge projection screens '
    'mounted on a dark wall with the NASA logo centered between them, '
    'tiered rows of computer desks below, blue cyan glow from monitors, '
    'dark navy and amber lighting'
)

# Phong cách chung của cả mười ba khung, đúng như bản mô tả của tác giả:
# truyện tranh toàn màu, nét mực sắc, đổ bóng sâu, điện ảnh.
# Khác COMIC_BASE ở chỗ bảng màu là phòng điều khiển (xanh lơ cyan, hổ
# phách amber, navy tối, đỏ cam cảnh báo) chứ không phải bụi Sao Hỏa.
# Câu "leave a calm empty area in an upper or lower corner" là chỗ để hộp
# thoại HTML đè lên: tranh không được kín chi tiết ở mọi góc.
IM_STYLE = (
    'full-color graphic novel illustration, sharp clean ink linework, '
    'deep shadows, cinematic dramatic lighting, science fiction comic book '
    'style, rich saturated colors, 16:9 widescreen composition, '
    'palette of cyan glow from screens, amber #e8a33d from warm lamps, '
    'dark navy room shadow, red orange emergency light, '
    'leave a calm uncluttered area in one upper or lower corner so a dialogue '
    'box can sit on top of the art later, '
    'do not draw any caption box, do not draw any blank empty rectangle in '
    'a corner, no speech bubble, '
    'absolutely no text, no letters, no numbers, no labels, no signage, '
    'no writing on any screen, wall or paper, no watermark, no logo, '
    'no caption box, no speech bubble'
)

# Cảnh trong phòng điều khiển dùng chung khối IM_STYLE. Khối nhân vật
# IM_CHARS KHÔNG gắn vào style mà chép thẳng vào từng prompt: spec của bộ
# ảnh yêu cầu khối đó nằm trong prompt, và nhét thêm lần nữa qua style sẽ
# gửi cùng một đoạn 190 từ hai lần trong một câu lệnh.
IM_STYLE_ROOM = IM_STYLE

# Khung ngoài không gian không có phòng điều khiển nên không mang khối
# nhân vật; chỉ giữ phần phong cách và bảng màu cyan của tín hiệu.
IM_STYLE_SPACE = IM_STYLE

# Phi hành gia mắc kẹt của khung 9: mô tả cố định, dùng nguyên văn trong
# prompt. Bộ đồ Horizon IV: vỏ cứng trắng NASA, lớp vải cam gỉ ở vai hông
# đầu gối, phủ bụi đỏ và vết xước, đúng như bộ nhân vật cố định của game.
IM_ASTRO = (
    'in a dusty white and orange Horizon IV Mars surface suit, hard white '
    'shell torso and limbs with rust orange fabric joint panels at the '
    'shoulders, hips and knees, a small mission patch on the chest, the '
    'suit covered in fine red dust and scuff marks, gloves off and hooked '
    'at his waist'
)

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

    # Tam anh gia dinh. Day la vat pham nguoi choi mo ra xem trong tui
    # do o man can cu, nen phai doc ra ngay la anh chup vo va con, khong
    # phai anh chung chung. Chup doc, kho in thuong, co nep gap va bang
    # keo dan o mep tren dung nhu truyen ke.
    'mem-family-photo': {
        'prompt': (
            'a creased colour photograph lying on a dark table, portrait '
            'orientation, showing a man in a plain shirt kneeling beside a '
            'woman with long dark hair, and between them a small girl about '
            'five years old held in the woman arms, the three of them in a '
            'warm apartment kitchen with a window behind, the photo itself '
            'visibly worn with a white crease running across one corner and '
            'a strip of black electrical tape stuck to the top edge, soft '
            'natural indoor light, warm amber tones, shot from directly '
            'above so the photo fills the frame, no text, no watermark'
        ),
        'note': 'tam anh gia dinh: vo va con gai, vat pham mo trong tui do',
        'kind': 'scene',
    },
    # Hai canh bo sung cho doan hoi tuong: con gai co mat trong truyen
    # thi phai co hinh, neu khong loi ke nhac toi con ma tranh chi co
    # hai nguoi la lech.
    'bg-kid-doorway': {
        'prompt': (
            'a small girl about five years old standing in a lit apartment '
            'doorway at dawn, holding a folded piece of paper in both hands, '
            'hair sleep tousled, wearing pyjamas, the corridor behind her '
            'dark and cool blue, the flat behind her warm amber, seen from '
            'adult eye level looking down, no text'
        ),
        'note': 'hoi tuong: con gai dung o nguong cua buoi sang',
        'kind': 'scene',
    },
    'bg-family-kitchen-night': {
        'prompt': (
            'a family of three sitting on the kitchen floor with their backs '
            'against the lower cupboards at three in the morning, a man in a '
            'plain shirt, a woman with long dark hair, and a small girl '
            'asleep leaning against the woman shoulder, the flat half packed '
            'with cardboard boxes stacked nearby, only the fridge light and '
            'one warm lamp on, quiet and tired, no text'
        ),
        'note': 'hoi tuong: ba nguoi ngoi bep luc ba gio sang',
        'kind': 'scene',
    },

    # ---------- mười hai khung truyện tranh của màn mở đầu ----------
    # Kể tuần tự không lời thoại, bám sát hai bản phác thảo tay của tác
    # giả. Bố cục từng khung ghi trong prompt là bố cục phác thảo, không
    # phải bố cục CSS: phần chia ô, thu nhỏ khung trước, mở mí mắt đều do
    # CSS làm khi ghép, nên ảnh phải là khung sạch không viền không ô nhỏ.

    'screen-01': {
        'prompt': (
            'extreme wide establishing shot of an empty Martian plain, '
            'a colossal dust storm vortex spiralling up from the ground and '
            'swallowing the whole horizon, towering wall of ochre dust, '
            'flat red desert floor with scattered rocks in the foreground, '
            'no figures anywhere, desolate and silent'
        ),
        'note': 'khung 1: bão cát nuốt chân trời, đồng bằng trống',
        'kind': 'comic',
        'style': COMIC_EMPTY,
    },
    'screen-02': {
        'prompt': (
            'medium shot of five or six astronauts in bulky white EVA suits '
            'sprinting hunched low through a thick red dust storm, bodies '
            'leaning into a hard gust, arms pumping, faces hidden behind '
            'dusty visors, dust streaking horizontally across frame, '
            'storm swallowing the background'
        ),
        'note': 'khung 2: đội chạy cúi người trong bão',
        'kind': 'comic',
        'style': COMIC_CREW,
    },
    'screen-03': {
        'prompt': (
            'first person view looking forward through blowing dust at a tall '
            'Mars ascent vehicle standing on its launch legs, cargo hatch open '
            'and ramp lowered, three white suited crew members ahead scrambling '
            'up the ladder toward the hatch, the viewer gloved arm and forearm '
            'reaching into the bottom edge of frame, dust halos around the '
            'floodlights'
        ),
        'note': 'khung 3: POV nhìn thấy tàu MAV, ba người leo lên',
        'kind': 'comic',
        'style': COMIC_POV,
    },
    'screen-04': {
        'prompt': (
            'tight close up of one astronaut face inside a helmet, seen '
            'through the curved visor glass, eyes wide open in shock and '
            'sudden realization, mouth half open, comic book shock emphasis '
            'lines radiating around the helmet, faint blurred reflection of a '
            'huge shape rushing toward them inside the glass, red dust on the '
            'visor edges'
        ),
        'note': 'khung 4: cận mặt giật mình sau kính mũ',
        'kind': 'comic',
        'style': COMIC_FACE,
    },
    'screen-05': {
        'prompt': (
            'low close up at ground level, a heavy astronaut boot mid stride '
            'catching hard on a rock jutting out of the red sand, boot toe '
            'jammed against the stone, clods of dirt and gravel flying up, '
            'sharp comic speed lines around the impact, dust puff at the heel'
        ),
        'note': 'khung 5: ủng vấp tảng đá, đất văng',
        'kind': 'comic',
        'style': COMIC_CREW,
    },
    'screen-06': {
        'prompt': (
            'wide shot of a single astronaut in a white EVA suit face down on '
            'the rocky ground, both gloved hands braced against the stones, '
            'body flat and sprawled, sand storm howling around them, dust '
            'curling over the back of the suit, hard wind blowing grit past '
            'the camera'
        ),
        'note': 'khung 6: ngã sấp giữa bão',
        'kind': 'comic',
        'style': COMIC_CREW,
    },
    'screen-07': {
        'prompt': (
            'wide shot of an astronaut lying motionless face down on the red '
            'ground while wind-driven sand pours over the body, the white suit '
            'half buried and fading into the dust drift, silhouette going '
            'dim and almost lost under the sand, chapter closing panel with '
            'heavy dark vignette closing in from all four edges, sand drifts '
            'piling at the frame edges'
        ),
        'note': 'khung 7: cát vùi dần, khung kết chương viền kép',
        'kind': 'comic',
        'style': COMIC_CREW,
    },
    'screen-08': {
        'prompt': (
            'straight top down aerial view looking vertically down the eye of '
            'a dust storm, a launch pad below with an upright Mars rocket, a '
            'transparent pressurised cabin near the top of the rocket with six '
            'white suited crew floating weightless inside, seen through the '
            'clear glass canopy, the rocket nose and body visible from above, '
            'storm wall spiralling around the pad'
        ),
        'note': 'khung 8: từ trên xuống, 6 người lơ lửng trong tàu',
        'kind': 'comic',
        'style': COMIC_CREW,
    },
    # Khung 9 kể khoảnh khắc tàn nhẫn nhất: tàu bỏ đi, còn đúng MỘT người
    # nằm sấp dưới đất. Prompt cũ hỏng hai chỗ: model vẽ bốn phi hành gia
    # đứng hai bên khung (không ai bị bỏ lại), và vẽ tên lửa đang HẠ cánh
    # (chân đáp bung ba phía, lửa đập tung đất ngay dưới chân tàu). Phải
    # khoá cứng ba ý: đúng một người, người đó nằm, tàu đã lên cao với
    # chân đáp thu vào thân.
    # Lần 3: hai lần trước model vẫn vẽ giàn chân đáp xòe quanh đế. Nguyên
    # nhân: tả tàu đang "climbing away" thì model tưởng còn ở trạng thái hạ
    # cánh. Đổi cách tả sang cấu hình bay: thân là ống trơn, đế là đĩa động
    # cơ phẳng, và nói rõ nét viền thân phải liền một đường từ mũi xuống đế.
    'screen-09': {
        'prompt': (
            'low angle looking straight up at a Mars ascent vehicle already '
            'far above the surface, high in flight and climbing fast, a wide '
            'band of empty dark air between the ship and the ground below, '
            'the ship is a smooth slender white cylinder with a tapered nose '
            'in clean launch configuration, its silhouette is one unbroken '
            'straight outline from nose to base that is never wider than the '
            'hull, flat circular engine plate at the base holding four '
            'engine bells, no landing gear, no legs, no struts, no fins, no '
            'outriggers, nothing protruding from the hull at all, four '
            'bright engine plumes blasting straight down from the engine '
            'plate into a huge billowing column of dust and smoke far below '
            'the ship, the rocket small in the upper third of the frame '
            'against a dark storm ceiling, torn clouds and debris whipping '
            'sideways, in the FOREGROUND at the very bottom corner of the '
            'frame ONE single astronaut lying face down on the red dirt, '
            'alone, small and helpless, arms sprawled, suit dust covered, '
            'no other people anywhere in the image, absolutely only one '
            'human figure in the entire scene'
        ),
        'note': 'khung 9: tàu đã bay cao, một mình nhân vật nằm sấp dưới đất',
        'kind': 'comic',
        'style': COMIC_CREW,
    },
    # Khung 10: bản cũ vẽ mũi tàu quay VỀ phía Sao Hỏa, tức là đang lao vào
    # hành tinh, ngược hẳn câu chuyện. Prompt mới khoá hướng: mũi tàu chỉ
    # ra ngoài vũ trụ, đuôi lửa nằm giữa tàu và Sao Hỏa.
    'screen-10': {
        'prompt': (
            'wide comic panel of deep black star filled space, planet Mars '
            'large and glowing red orange in the lower right of the frame '
            'with visible cratered surface, Valles Marineris canyon scar and '
            'a thin blue glowing atmosphere rim, a small spacecraft in the '
            'UPPER LEFT flying AWAY from the planet toward the top left '
            'corner, its nose pointed AWAY from Mars into empty space, a long '
            'bright red orange engine plume trailing BEHIND it back toward '
            'the planet, the ship clearly departing and growing distant, '
            'heavy black ink outlines on the planet limb and the ship, '
            'halftone dot shading in the shadow side of the planet, drawn on '
            'paper like a printed comic page'
        ),
        'note': 'khung 10: tàu nhỏ bay khỏi Sao Hỏa',
        'kind': 'comic',
        'style': COMIC_EMPTY,
    },
    'screen-11': {
        'prompt': (
            'first person view from the ground through barely opened eyes, '
            'thick solid black eyelid shapes filling the top quarter and the '
            'bottom quarter of the frame, a narrow horizontal slit between '
            'them showing an out of focus pale Mars sky and red ground, soft '
            'blur only inside the slit, a white suited arm lying limp in the '
            'sand visible in the lower slit edge, comic panel framing'
        ),
        'note': 'khung 11: mở mí mắt, nhìn ra bầu trời Sao Hỏa',
        'kind': 'comic',
        'style': COMIC_POV,
    },
    'screen-12': {
        'prompt': (
            'quiet wide shot of the Martian surface after the storm, clear '
            'orange sky, an empty red plain, a lonely dome shaped habitat '
            'module standing on the left side of frame with a round airlock '
            'door and small antenna, a few rock outcrops and a piece of '
            'equipment on the right side, long shadows, no figures anywhere'
        ),
        'note': 'khung 12: trạm Hab mái vòm sau bão, cảnh trống',
        'kind': 'comic',
        'style': COMIC_EMPTY,
    },

    # ---------- bộ art màn căn cứ thiết kế lại ----------
    # Ba sprite nhân vật dùng chung CHAR_LOOK nguyên văn. Chỉ phần tư thế
    # đổi, phần con người và bộ đồ giữ y nguyên từng chữ, để model không
    # vẽ ra ba người khác nhau.

    'char-healthy': {
        'prompt': (
            CHAR_LOOK + ', '
            'pose: standing upright and confident, weight even on both boots, '
            'shoulders square, chin level, calm focused expression looking '
            'slightly to his left toward a piece of equipment, '
            'turned three quarters to the viewer so the body faces the right '
            'side of frame, '
            'his left hand holds a pale metal clipboard with a paper checklist '
            'up at chest height, held close against his body, '
            'his right arm bent with the hand resting on his hip, elbow out, '
            'nothing floating in the air beside him, '
            'healthy and alert, upright posture, alert eyes, clean unworn '
            'coverall, lit from the left by cool white equipment light with a '
            'warm amber rim on the right shoulder'
        ),
        'note': 'nhân vật: khoẻ mạnh, đứng cầm bảng kiểm tra',
        'kind': 'char',
        'style': STYLE_CHAR,
    },
    'char-tired': {
        'prompt': (
            CHAR_LOOK + ', '
            'pose: SITTING DOWN on the metal floor, definitely not standing. '
            'His hips and seat are on the ground, both knees are drawn up in '
            'front of his chest with the boots flat on the floor close to his '
            'body, both forearms hanging forward to rest on top of his knees, '
            'the whole body folded into a compact huddled seated shape that is '
            'clearly shorter than a standing figure, '
            'head hanging low between his shoulders, chin dropped onto his '
            'chest, eyes looking down at the floor, shoulders slumped and '
            'rolled forward, spine curved over, '
            'exhausted hungry expression, sunken tired eyes, hollow cheeks, '
            'dull grey shadowed skin, lips pressed thin, '
            'the coverall creased and dusty, one boot lace loose, '
            'no crate, no chair, no stool, no box to sit on, nothing behind '
            'him, he sits directly on the empty floor, '
            'seen three quarters from the front, '
            'dim cold blue fill light from the left, empty hands'
        ),
        'note': 'nhân vật: mệt mỏi, ngồi bó gối',
        'kind': 'char',
        'style': STYLE_CHAR,
    },
    'char-cold': {
        'prompt': (
            CHAR_LOOK + ', '
            'pose: standing but hunched against the cold, knees slightly bent, '
            'both arms folded tight across his chest with each hand tucked '
            'under the opposite arm, shoulders drawn up near the ears, '
            'head pulled down into his collar, shivering, '
            'wearing the same grey-blue coverall with an extra quilted amber '
            'thermal over-jacket open over it, padded rust orange lining at '
            'the collar and cuffs, hood down behind the neck, '
            'a thin plume of visible breath vapour leaving his mouth, '
            'pale bluish skin, tight pained expression, jaw clenched, '
            'full body standing sprite with the same head to boot scale as '
            'the other poses, seen three quarters from the front, '
            'cold cyan light from the left, faint warm amber from the right'
        ),
        'note': 'nhân vật: co ro vì lạnh, mặc áo giữ nhiệt',
        'kind': 'char',
        'style': STYLE_CHAR,
    },

    # ---------- sáu icon vật phẩm mới, sprite trong suốt ----------

    'icon-ration-nasa': {
        'prompt': (
            'a single NASA crew ration pouch standing upright, '
            'a sealed vacuum foil bag of dull brushed silver metallised film '
            'with fine crinkle creases catching light, '
            'a wide printed label band across the lower half of the pouch in '
            'NASA equipment white with a rust orange stripe, '
            'a short clear drinking tube with a bite valve clipped to the top '
            'right corner of the pouch, one small amber sealed port, '
            'a folded tear notch at the upper left corner, '
            'slightly squashed in the middle like a partly used bag, '
            'clean crisp outlines on every fold, '
            'cool white key light from upper left, warm rust rim light on the '
            'right edge, whole pouch and tube inside the frame'
        ),
        'note': 'icon: gói khẩu phần NASA',
        'kind': 'icon-sprite',
        'style': STYLE_ICON_SPRITE,
        'key_bg': True,
    },
    'icon-water-recycled': {
        'prompt': (
            'a single reusable water bottle made of brushed stainless steel, '
            'tall cylinder with a slightly tapered neck and a screw cap, '
            'a clear vertical sight window strip down the front of the body, '
            'thin engraved volumetric graduation marks along that window in '
            'even steps, a pale NASA equipment white silicone grip band around '
            'the middle, a small rust orange cap tether loop, '
            'a few condensation droplets on the steel, '
            'slight dent on the lower body, clean crisp outlines, '
            'cool white key light from upper left with a cyan bounce along the '
            'left edge and warm rust rim on the right, '
            'whole bottle fully inside the frame'
        ),
        'note': 'icon: bình nước tái chế có vạch chia',
        'kind': 'icon-sprite',
        'style': STYLE_ICON_SPRITE,
        'key_bg': True,
    },
    'icon-moxie-core': {
        'prompt': (
            'a single cylindrical MOXIE style oxygen generator cartridge, '
            'seen in three quarter view standing tilted at about thirty '
            'degrees, clearly a fat short drum with round ends, '
            'the drum body is bright NASA equipment white painted metal, '
            'lit strongly so the pale body stands out against any background, '
            'the middle third of the drum is a stack of many separate thin '
            'flat circular cooling discs, each disc a distinct ring with a '
            'dark shadow gap between it and the next, the finned section reads '
            'as a ribbed heat sink, '
            'steel grey end caps bolted on with visible hex bolts, '
            'a heavy machined brass and steel connector head on the left end '
            'with a knurled locking collar and two short rigid pipe stubs '
            'pointing left, '
            'a small glowing cyan indicator window and one amber status lamp '
            'on the upper surface, '
            'a rust orange caution band around the right end, '
            'light dust film on the white paint, clean crisp outlines on every '
            'fin, '
            'strong bright cool white key light from upper left, warm amber '
            'glow from the connector end, bright rim light along the top edge, '
            'whole drum fully inside the frame'
        ),
        'note': 'icon: lõi lọc MOXIE',
        'kind': 'icon-sprite',
        'style': STYLE_ICON_SPRITE,
        'key_bg': True,
    },
    'icon-battery-spare': {
        'prompt': (
            'a single spare battery pack as a chunky rectangular block, '
            'seen in three quarter view standing on one narrow end, '
            'a rugged steel grey case with rounded corner bumpers and a '
            'recessed carry handle slot on top, '
            'two thick brass coloured terminals on the top face, one positive '
            'and one negative, clearly separated, '
            'a vertical column of four small charge indicator lamps on the '
            'front face, three lit amber and one dark, '
            'a pale NASA equipment white label plate with a rust orange band '
            'and a cyan status strip low on the front, '
            'faint vent slots cut into the side, scuffed edges, '
            'clean crisp outlines, cool white key light from upper left with '
            'an amber glow from the lit lamps, whole block inside the frame'
        ),
        'note': 'icon: pin dự phòng',
        'kind': 'icon-sprite',
        'style': STYLE_ICON_SPRITE,
        'key_bg': True,
    },
    'icon-antenna-board': {
        'prompt': (
            'a single antenna circuit board seen flat on at a slight tilt, '
            'a rectangular dark green printed circuit board with a pale metal '
            'mounting frame, '
            'a large square copper antenna coil taking up the whole upper half '
            'of the board, a flat spiral of thick copper trace wound four full '
            'turns with clear gaps between the turns, the single dominant '
            'feature of the board, '
            'a row of silver surface mount components and small capacitors '
            'along the lower edge, thin pale cyan silkscreen tracks running '
            'between them, '
            'a bright brass coaxial connector block sticking up from the right '
            'edge with a threaded collar and a short centre pin, '
            'four mounting holes in the corners, one small amber lamp, '
            'clean crisp lineart on every trace, '
            'cool white key light from upper left, warm rust rim along the '
            'board edge, whole board and connector inside the frame'
        ),
        'note': 'icon: bo mạch ăng-ten',
        'kind': 'icon-sprite',
        'style': STYLE_ICON_SPRITE,
        'key_bg': True,
    },
    'icon-first-aid': {
        'prompt': (
            'a single first aid kit box seen in three quarter view, '
            'a compact moulded hard case in clean NASA equipment white with '
            'steel grey reinforced corners and a rounded lid, '
            'a bold red cross symbol embossed in the centre of the lid front, '
            'not a printed sticker, raised and painted, '
            'a metal latch clasp with a small amber push button on the front '
            'edge, '
            'a thin rust orange stripe running around the body just below the '
            'lid seam, two hinge blocks at the back, '
            'a faint dust film and one small scuff on the lid, '
            'clean crisp outlines, cool white key light from upper left with '
            'warm amber fill from below, whole case inside the frame'
        ),
        'note': 'icon: bộ sơ cứu',
        'kind': 'icon-sprite',
        'style': STYLE_ICON_SPRITE,
        'key_bg': True,
    },

    # ---------- hai tranh popup màn căn cứ ----------

    'popup-comms-radar': {
        'prompt': (
            'interior of a cramped Mars habitat communications station at '
            'night, seen in a wide 16:9 composition, '
            'a large circular radar screen dominating the upper middle of '
            'frame, mounted in a heavy steel grey console frame, '
            'the screen dark with a glowing cyan sweep line rotating from the '
            'centre and three faint cyan target blips with short motion '
            'trails arcing across the scope, '
            'a faint green-cyan grid of range rings on the glass, '
            'the console below the screen is crowded with rows of round '
            'knurled knobs, toggle switches and small amber lit button '
            'indicators, an angled keyboard slab and a coiled handset '
            'hanging on a hook, '
            'the cyan light from the screen washes over one operator seen from '
            'behind, only the back of the shoulders and the short cropped hair '
            'are visible in silhouette at the lower left, one hand resting on '
            'a knob, face turned away from camera and not visible, '
            'cable runs and a patch panel of connectors on the wall behind, '
            'dark steel grey walls, faint rust orange primer patches, red dust '
            'film on every surface, '
            'cool cyan key light only from the screen with a warm amber accent '
            'lamp high on the right wall'
        ),
        'note': 'popup: trạm liên lạc, màn radar và bóng người vận hành',
        'kind': 'popup',
        'style': STYLE_POPUP,
    },
    'popup-airlock-eva': {
        'prompt': (
            'interior of a Mars habitat airlock chamber seen from inside, '
            'wide 16:9 composition, '
            'a heavy circular vault style outer door at the centre of frame '
            'swung open on thick hinges, '
            'beyond the open doorway a blinding wall of red dust storm fills '
            'the whole opening, thick ochre and rust orange sand streaking '
            'sideways past the frame, the outside world completely obscured, '
            'a haze of fine dust blowing in across the threshold and swirling '
            'low over the floor grating, '
            'on the right hand wall a steel rack holds two bulky white EVA '
            'pressure suits hanging empty from the shoulders, one helmet '
            'seated on a shelf beside them with a scratched mirrored visor, '
            'a second helmet clipped to the wall brackets, coiled tether '
            'loops and a tool harness, '
            'a yellow and black hazard band painted around the door frame, '
            'an amber warning lamp lit above the door casting a hot pool of '
            'light on the floor, '
            'steel grey interior walls, condensation on the ceiling panels, '
            'red dust film on the suits and on the floor, '
            'warm amber interior light meeting the cold red storm light in the '
            'doorway, no people in frame'
        ),
        'note': 'popup: khoang khoá khí mở ra bão cát, giá đồ EVA',
        'kind': 'popup',
        'style': STYLE_POPUP,
    },

    # ---------- tám cảnh kết thúc thua ----------
    # Cùng một khối style cho cả tám, để màn kết thúc trông như một bộ.
    # Nhấn mạnh ba lần "no text" vì model hay vẽ chữ lên màn hình thiết bị.
    'ending_hypoxia': {
        'prompt': (
            'interior of a Mars habitat module with the red emergency lighting '
            'on, wide 16:9 composition, deep shadow in the corners, '
            'an astronaut in a slate grey coverall slumped forward over the '
            'life support control console, one arm hanging, helmet off and '
            'resting on the desk, face turned away and not readable, '
            'the console screens show a flat dead green line where the oxygen '
            'graph used to trace, a dark red warning lamp washing the wall, '
            'frost forming on the inner face of the window, dust film on every '
            'surface, scattered printouts on the floor, no text anywhere'
        ),
        'note': 'ending: thiếu oxy, gục bên bảng điều khiển',
        'kind': 'ending',
        'style': ENDING_STYLE,
        'size': '1600x900',
    },
    'ending_dehydration': {
        'prompt': (
            'close in on a dusty Mars habitat engineering bench, wide 16:9 '
            'composition, '
            'the ECLSS water recycling unit standing open and bone dry, the '
            'inner trays pulled out and empty, a single amber fault lamp '
            'glowing on its front panel, '
            'an astronaut in a slate grey coverall sitting on the floor with '
            'his back against the bulkhead, knees up, head tipped back, '
            'exhausted, face in shadow and not readable, '
            'a cracked empty water bottle lying on its side with no drop left '
            'in it, red dust drifted against the skirting, '
            'cold white lamp light from above against warm amber bounce, '
            'no text anywhere'
        ),
        'note': 'ending: hết nước, bình ECLSS rỗng',
        'kind': 'ending',
        'style': ENDING_STYLE,
        'size': '1600x900',
    },
    'ending_starvation': {
        'prompt': (
            'interior of a Mars habitat galley, wide 16:9 composition, '
            'a food locker hanging open and completely empty, bare shelves, '
            'torn silver foil ration pouches scattered across the floor and '
            'under the table, all of them flattened and empty, '
            'one dented metal tray with nothing on it, '
            'a weak single overhead lamp barely lighting the counter, deep '
            'shadow filling the rest of the room, '
            'an astronaut sitting at the table with his head in his hands, '
            'shoulders thin, seen from behind so the face is not visible, '
            'red dust on the floor tiles, no text anywhere'
        ),
        'note': 'ending: hết lương thực, tủ khẩu phần trống',
        'kind': 'ending',
        'style': ENDING_STYLE,
        'size': '1600x900',
    },
    'ending_blackout': {
        'prompt': (
            'interior of a Mars habitat at night with all power gone, wide 16:9 '
            'composition, nearly total darkness lit only by one handheld torch '
            'beam, '
            'ice crystals grown across the inside of the window glass, and '
            'beyond the glass a red dust storm pressing against the pane, '
            'an astronaut in a thermal jacket curled up in the corner hugging '
            'his knees, the torch on the floor beside him throwing a hard cone '
            'of pale light and a long shadow, '
            'every console dark, frost on the metal, breath fog in the beam, '
            'cold blue white torch light against the deep rust glow outside, '
            'no text anywhere'
        ),
        'note': 'ending: mất điện trong bão, băng trên kính',
        'kind': 'ending',
        'style': ENDING_STYLE,
        'size': '1600x900',
    },
    'ending_orbit_miss': {
        'prompt': (
            'deep space view of a small damaged rescue spacecraft tumbling out '
            'of control past Mars, wide 16:9 composition, '
            'Mars filling the lower right of frame as a huge rust red disc with '
            'a thin pale atmosphere rim and Valles Marineris cutting across it, '
            'the ship in the upper left, silhouette lit hard on one side by the '
            'sun, one solar panel bent and one engine bell cold, '
            'a thin trail of venting gas curling away from a cracked fitting, '
            'the ship already drifting out of the frame into black, '
            'hard white sunlight and absolute black shadow, dust of stars, '
            'the hull is completely bare metal, not a single marking, no decal, '
            'no serial number, no stencil, no hull code, no insignia, '
            'no text anywhere'
        ),
        'note': 'ending: trượt quỹ đạo, tàu trôi vào bóng tối',
        'kind': 'ending',
        'style': ENDING_STYLE + ', the spacecraft hull is plain unmarked '
                 'panelling with no lettering of any kind',
        'size': '1600x900',
    },
    'ending_mutiny': {
        'prompt': (
            'interior of a cramped spacecraft cockpit, wide 16:9 composition, '
            'three astronauts in slate grey flight suits standing with their '
            'backs turned to each other, one at the left window, one at the '
            'right console, one at the centre hatch, faces and heads turned '
            'away, bodies rigid with tension, '
            'a navigation screen glowing cyan at the centre showing a curved '
            'return trajectory arcing back toward a small blue Earth, '
            'loose checklists and a torn crew schedule drifting on the deck, '
            'cold cyan screen light under warm amber cabin lamps, deep shadow '
            'between the three figures, no text anywhere'
        ),
        'note': 'ending: binh biến, ba người quay lưng',
        'kind': 'ending',
        'style': ENDING_STYLE,
        'size': '1600x900',
    },
    'ending_comms_lost': {
        'prompt': (
            'interior of a Mars habitat communications station at night, wide '
            '16:9 composition, '
            'the whole console buried under white static and rolling noise '
            'bands, three screens all filled with snow, cables hanging loose, '
            'a red carrier loss lamp lit on the panel, '
            'through the window behind, a large dish antenna stands dead still '
            'against a black night sky with Mars\'s two small moons and a band '
            'of stars, its feed horn pointed at nothing, '
            'red dust piled on the sill, cold white screen glow against the '
            'rusted metal, no text anywhere'
        ),
        'note': 'ending: mất liên lạc, màn hình nhiễu, chảo DSN đứng im',
        'kind': 'ending',
        'style': ENDING_STYLE,
        'size': '1600x900',
    },
    'ending_edl_crash': {
        'prompt': (
            'wide landscape view of a rocky Martian plain at dusk, 16:9 '
            'composition, '
            'a black column of smoke and burning debris driving down out of an '
            'orange dust sky and slamming into the jagged boulder field in the '
            'middle distance, a bright flash of impact light under the smoke, '
            'scattered wreckage panels and a torn parachute canopy strewn across '
            'the rocks, '
            'far off to the left the squat habitat module stands with red '
            'emergency beacons blinking on its roof, '
            'a lone astronaut in a white EVA suit standing small in the '
            'foreground watching, back to camera, '
            'long shadows, dust haze, no text anywhere'
        ),
        'note': 'ending: hạ cánh thất bại, vệt khói đen',
        'kind': 'ending',
        'style': ENDING_STYLE,
        'size': '1600x900',
    },

    # ---------- năm lớp nền cho Giai đoạn 2 ----------
    # Mỗi ảnh là một lớp nằm SAU nội dung SVG của feature, nên bố cục phải
    # chừa khoảng lặng ở giữa và để chi tiết dồn về mép. Tên bắt đầu bằng
    # p2- để process-assets.py nhặt riêng, không lẫn với bộ bg- của
    # Giai đoạn 1.
    'p2-radar-room': {
        'prompt': (
            'interior of a NASA mission control room at night, wide 16:9 '
            'composition, seen from behind the tiered rows of consoles, '
            'two enormous projection screens hang side by side on the dark '
            'far wall, both screens filled with a soft cyan radar glow and '
            'orbit track lines but no readable writing of any kind, '
            'a plain circular blue and red agency emblem decal centred '
            'between the two screens, dim and unlit, '
            'rows of desk consoles stepping down toward the screens with '
            'small amber and cyan indicator lamps, empty swivel chairs, '
            'one or two flight controllers seated far away and seen only as '
            'dark silhouettes from behind, '
            'cold cyan screen light washing up onto faces and desk edges, '
            'deep shadow in the ceiling, tense waiting atmosphere'
        ),
        'note': 'Giai đoạn 2: phòng điều khiển DSN ban đêm, lớp nền màn bắt sóng',
        'kind': 'p2scene',
        'style': P2_SCENE_STYLE_CREW,
        'size': '1600x900',
    },
    'p2-assembly-bay': {
        'prompt': (
            'interior of an enormous spacecraft assembly building, wide 16:9 '
            'composition, cathedral scale, '
            'a high steel truss ceiling with two overhead gantry cranes and '
            'hanging work platforms, '
            'in the centre a heavy raised assembly stand holding a half '
            'built interplanetary spacecraft, bare hull ribs, open panels '
            'and exposed cabling, scaffolding wrapped around its lower half, '
            'hard cold white industrial floodlights raking down from the '
            'ceiling in visible beams with floating dust in them, '
            'polished concrete floor with yellow safety line markings and a '
            'red walkway stripe, scattered tool carts at the edges, '
            'no people, everything still and waiting'
        ),
        'note': 'Giai đoạn 2: xưởng lắp ráp tàu, lớp nền màn ghép tàu',
        'kind': 'p2scene',
        'style': P2_SCENE_STYLE,
        'size': '1600x900',
    },
    'p2-orbit-map': {
        'prompt': (
            'comic book panel illustration, drawn with a brush pen and '
            'coloured flat, 16:9 widescreen panel, '
            'deep space view, wide 16:9 composition, seen from far outside '
            'both planets, '
            'a small blue Earth low in the bottom left corner, its night '
            'side toward the viewer with a thin cyan atmospheric rim, '
            'a large rust red Mars high in the top right corner, half lit '
            'by hard white sunlight, its surface showing dark canyon scars, '
            'between the two planets a single thin glowing transfer arc '
            'curves across the black, a hairline of pale amber light with a '
            'faint cyan haze around it, '
            'dense star field behind, a soft dusty nebula smear in the lower '
            'right, '
            'both planets drawn with a hard black inked outline, flat cel '
            'shaded colour blocks in two or three tones, visible halftone '
            'dot texture in the shadow side, screen printed comic colour, '
            'empty centre of frame, no spacecraft anywhere, no labels'
        ),
        'note': 'Giai đoạn 2: bản đồ quỹ đạo Trái Đất tới Sao Hỏa',
        'kind': 'p2scene',
        'style': P2_SCENE_STYLE,
        'size': '1600x900',
    },
    'p2-edl-sky': {
        'prompt': (
            'high aerial view looking down onto the Martian surface at dusk, '
            'wide 16:9 composition, '
            'the sky occupies the top third and is thick amber dust haze lit '
            'from a low sun off frame right, the horizon softened into the '
            'haze, '
            'below it a jagged field of broken rock and boulders with long '
            'shadows, '
            'a flat open plain sits in the middle of the frame with a fine '
            'grid of faint wheel tracks and a few small craters, '
            'in the middle of that plain one tiny bright amber point of light '
            'marks a portable landing beacon, small in frame but clearly '
            'glowing, '
            'no spacecraft, no parachute, no people, no structures'
        ),
        'note': 'Giai đoạn 2: bầu trời Sao Hỏa lúc hạ cánh, lớp nền hoạt cảnh EDL',
        'kind': 'p2scene',
        'style': P2_SCENE_STYLE,
        'size': '1600x900',
    },
    'p2-stars-bg': {
        'prompt': (
            'deep star field background, wide 16:9 composition, '
            'almost black space with a dense field of small sharp stars of '
            'varying brightness, '
            'a faint pale Milky Way band running diagonally from the lower '
            'left to the upper right, soft and dusty rather than bright, '
            'two very faint cool nebulae, one cyan and one dull amber, '
            'no planets, no spacecraft, no objects in the foreground, '
            'even and calm across the whole frame, dark enough for text to '
            'sit on top'
        ),
        'note': 'Giai đoạn 2: nền trời sao dùng chung cho cả Phase 2',
        'kind': 'p2scene',
        'style': P2_SCENE_STYLE,
        'size': '1600x900',
    },

    # ---------- huy hiệu màn chờ tải ----------
    # Huy hiệu tròn kiểu NASA mission patch, nền trong suốt, không chữ.
    # Vẽ nét mảnh trên nền xám phẳng để hậu kỳ tách alpha, rồi thu về
    # 512x512. Màu khoá theo bảng màu game: hổ phách và xanh lơ trên
    # nền tối, đỏ cam cho Sao Hoả.
    'loading-emblem': {
        'prompt': (
            'flat vector mission patch emblem, perfectly circular badge seen '
            'straight on, centred in frame, '
            'outer ring is a thin brushed steel grey rim with fine tick marks '
            'around it like the bezel of a gauge or a stopwatch dial, short '
            'evenly spaced radial ticks, no numerals, '
            'inside the ring a flat small Mars globe in warm rust orange '
            '#C84B31 with a few darker ochre surface blotches, '
            'a single thin ellipse orbit line in pale data cyan #4FB8C9 '
            'crossing the planet diagonally, drawn as a hairline stroke, '
            'one tiny spacecraft dot in pale amber #E8A33D sitting on the '
            'orbit line at the upper right, '
            'thin uniform line weight everywhere, minimal flat design, '
            'two colour flat fills only, no shading gradient, no glow, '
            'no text, no letters, no numbers, no logo, no watermark, '
            'no border frame around the canvas, no drop shadow, '
            'nothing else in the frame'
        ),
        'note': 'huy hiệu: huy hiệu tròn màn chờ tải, nền trong suốt',
        'kind': 'emblem',
        'style': (
            'clean technical vector illustration, flat design, '
            'crisp hairline strokes, high contrast against the background, '
            'readable at 96 pixels wide'
        ),
        'key_bg': True,
        'size': '1024x1024',
    },

    # ---------- bảy khung chuyển tiếp Giai đoạn 1 sang Giai đoạn 2 ----------
    # Mười ba khung tất cả, chia cho hai sub chạy song song: bảy khung ở
    # đây (im-01 tới im-07) và sáu khung còn lại do sub kia lo. Hai bộ phải
    # đứng cạnh nhau trong cùng một đoạn phim nên dùng chung khối nhân vật
    # IM_CHARS bên dưới, chép nguyên văn, không sửa một chữ.
    #
    # Tên asset giữ tiền tố bg- để process-assets.py nhặt vào vòng quét
    # bg-*.png và xuất WebP 1600x900 vào src/assets/art/.

    'bg-im-01': {
        'prompt': (
            'view from deep space, planet Earth glowing blue in the centre of '
            'a star filled black sky, a bright cyan radio beam shooting down '
            'from space toward a huge parabolic dish antenna of the Deep Space '
            'Network on Earth surface, concentric radio wave rings spreading '
            'from the dish, continents visible through thin cloud, night side '
            'of Earth with city lights, no people'
        ),
        'note': 'chuyển tiếp 1: tia tín hiệu bay tới Trái Đất',
        'kind': 'scene',
        'style': IM_STYLE_SPACE,
        'size': '1600x900',
    },
    'bg-im-02': {
        'prompt': (
            'wide shot inside the NASA mission control room described above, '
            'shot from high angle over the whole room so the chaos reads at a '
            'glance, '
            + IM_CHARS + ', '
            'both giant projection screens show red warning graphs and red '
            'telemetry failure charts, and the red light of those screens is '
            'the only key light in the room, '
            'NOBODY is sitting: every single engineer in shirtsleeves is '
            'standing, dozens of them on their feet at once, most pushed back '
            'from their desks, some with both hands pressed to their head, '
            'some turning to shout at the person beside them, some hurrying '
            'between the rows of desks carrying fistfuls of printouts, '
            'loose printed sheets scattered across the floor and the desks, '
            'several overturned chairs, '
            'tense chaotic atmosphere, red emergency light washing over the '
            'whole room, mood of a disaster that just happened'
        ),
        'note': 'chuyển tiếp 2: phòng điều khiển NASA hỗn loạn',
        'kind': 'scene',
        'style': IM_STYLE_ROOM,
        'size': '1600x900',
    },
    'bg-im-03': {
        'prompt': (
            'close shot of a single computer monitor in a dark control room, '
            'the screen blazing bright with a large glowing envelope icon and '
            'a pulsing amber and cyan exclamation mark, the light from the '
            'screen spilling across the desk and keyboard, the rest of the '
            'room dark and out of focus behind, papers and a headset on the '
            'desk, nobody visible'
        ),
        'note': 'chuyển tiếp 3: màn hình bật sáng có thư tới',
        'kind': 'scene',
        'style': IM_STYLE_ROOM,
        'size': '1600x900',
    },
    'bg-im-04': {
        'prompt': (
            'SPLIT PANEL LAYOUT, two horizontal panels with a clean black '
            'gutter between them, the gutter running edge to edge and filled '
            'with flat black, no border around the outside of the image, '
            'LEFT PANEL: small inset of the glowing monitor with the envelope '
            'icon seen from a distance in the dark room. '
            'RIGHT PANEL: tight close up of the NASA flight controller '
            'described above, shot from the side, he has just jumped up from '
            'his chair so fast the chair is tipping backwards, eyes wide open '
            'in shock, mouth open, one arm pointing straight at the screen, '
            'glasses catching the screen glow, dramatic rim light, '
            + IM_CHARS
        ),
        'note': 'chuyển tiếp 4: nhân viên kinh ngạc, chia hai ô ngang',
        'kind': 'scene',
        'style': IM_STYLE_ROOM,
        'size': '1600x900',
    },
    'bg-im-05': {
        'prompt': (
            'wide shot inside the NASA mission control room described above, '
            + IM_CHARS + ', '
            'the entire room erupting in celebration, everyone on their feet, '
            'engineers throwing armfuls of paper printouts into the air so '
            'the sheets fill the upper third of the frame, people hugging '
            'each other, faces jubilant and tearful, arms raised, both giant '
            'screens now showing bright green and cyan data, warm amber and '
            'cyan light mixing, joyful chaotic energy'
        ),
        'note': 'chuyển tiếp 5: cả phòng tung giấy ăn mừng',
        'kind': 'scene',
        'style': IM_STYLE_ROOM,
        'size': '1600x900',
    },
    'bg-im-06': {
        'prompt': (
            'CAMERA IS BEHIND THE GROUP, HIGH OVER THEIR HEADS, LOOKING DOWN: '
            'we see the backs of their heads and shoulders, NOT their faces '
            'facing the camera, '
            'a dozen engineers crowded shoulder to shoulder around one '
            'central desk in the dim control room, all leaning in toward the '
            'screen, bodies tense and silent, '
            'the flight controller described above sits at the centre of the '
            'huddle with his hand resting on a computer mouse, seen from '
            'behind and above over the shoulders of the people standing '
            'around him, '
            'screen glow lighting the underside of their faces and the desk '
            'from below, nobody speaking, the moment before a click, '
            + IM_CHARS
        ),
        'note': 'chuyển tiếp 6: cả nhóm nín thở quanh bàn',
        'kind': 'scene',
        'style': IM_STYLE_ROOM,
        'size': '1600x900',
    },
    'bg-im-07': {
        'prompt': (
            'SPLIT PANEL LAYOUT, two horizontal panels with a clean black '
            'gutter, the gutter running edge to edge and filled with flat '
            'black, no border around the outside of the image, '
            'LEFT PANEL: the same tight group of engineers crowded around the '
            'desk, tense faces lit from below by the screen, exactly as in '
            'the previous panel so the scene reads as continuous. '
            'RIGHT PANEL: extreme macro close up of a male hand pressing down '
            'on a wired computer mouse, the index finger pressing the button, '
            'the mouse on a desk mat, cyan screen light on the knuckles, the '
            'moment of the click frozen, comic book impact, '
            + IM_CHARS
        ),
        'note': 'chuyển tiếp 7: cận cảnh cú click, chia hai ô ngang',
        'kind': 'scene',
        'style': IM_STYLE_ROOM,
        'size': '1600x900',
    },

    # ---------- sáu khung cuối của đoạn chuyển tiếp (8 tới 13) ----------
    # Sub thứ hai lo sáu khung này. Khối nhân vật IM_CHARS và phong cách
    # IM_STYLE chép nguyên văn từ nửa trên, không sửa một chữ, để mười ba
    # khung ghép lại thành một đoạn phim liền mạch.
    #
    # Người thứ ba của bộ tranh: phi hành gia mắc kẹt. Khối IM_ASTRO dưới
    # đây là mô tả cố định cho anh ta, dùng y nguyên ở mọi khung có anh ta.
    # Bộ đồ Horizon IV: vỏ cứng trắng, lớp vải lót cam gỉ ở vai hông đầu
    # gối, phủ bụi đỏ và vết xước. Không có khối này thì mỗi khung model vẽ
    # một bộ đồ khác nhau và người xem mất dấu nhân vật.

    'bg-im-08': {
        'prompt': (
            'SPLIT PANEL LAYOUT, three comic panels separated by clean black '
            'gutters, two small panels of equal size side by side across the '
            'top row and one large panel filling the whole bottom row, every '
            'gutter filled with flat solid black running edge to edge, no '
            'border around the outside of the image, '
            'TOP LEFT PANEL: a tight crowd of shirt sleeved NASA engineers '
            'packed shoulder to shoulder leaning in over one desk, tense '
            'faces lit hard from below by a screen, jaws tight, eyes fixed '
            'downward, the backs of two heads at the panel edge, '
            'TOP RIGHT PANEL: extreme close up of a male hand pressing down '
            'on a computer mouse, knuckles taut, one finger on the button, '
            'hand and mouse lit by a strong cyan glow from the screen, a dark '
            'desk mat below, the moment of the click frozen, '
            'BOTTOM LARGE PANEL: straight on view of a computer monitor '
            'screen filling the whole panel edge to edge, the screen showing '
            'a glowing digital envelope graphic bursting open, bright light '
            'rays shooting out of the opened flap, cyan and amber particles '
            'swirling out of the burst, the burst light spilling off the '
            'glass and reflecting across the glossy desk surface below, '
            + IM_CHARS
        ),
        'note': 'chuyển tiếp 8: ba ô, đám đông, tay bấm chuột, phong bì bung sáng',
        'kind': 'scene',
        'style': IM_STYLE_ROOM,
        'size': '1600x900',
    },
    # Khung 9 là khung DUY NHẤT có bảng trắng để chữ HTML đè lên. Prompt phải
    # khoá ba lần ý "bảng trống": nếu chỉ nói "blank clipboard" thì model vẽ
    # đầy dòng gạch và chữ giả, và lớp chữ thật chồng lên sẽ thành hai lớp
    # chữ đè nhau. Bảng phải thẳng, vuông góc với máy quay, phẳng mặt.
    'bg-im-09': {
        'prompt': (
            'photograph style framing seen from inside a Mars habitat module, '
            'the shot is framed by a fixed camera: the corner of a riveted '
            'metal bulkhead cuts into the upper left of the frame and a dark '
            'steel mount bar fills the bottom edge, one small glowing red '
            'recording dot sits high in the top corner, surveillance camera '
            'feed look, '
            'in the centre of the frame a stranded astronaut ' + IM_ASTRO +
            ', stands facing the camera dead on, his helmet popped off and '
            'clipped to his belt at the hip so his dusty tired face is fully '
            'visible, grime on his cheeks, dust in his hair, hopeful eyes, '
            'clearly alive, breathing, '
            'he holds up a large blank white clipboard with both hands at '
            'chest height, the clipboard is perfectly straight and square to '
            'the camera, its surface is completely blank, empty, plain white, '
            'with no lines, no writing, no header, no text of any kind, '
            'nothing printed on the paper clip or the board, '
            'warm amber habitat lighting behind him, dust and scuff marks on '
            'the suit, shallow depth of field so the clipboard stays sharp'
        ),
        'note': 'chuyển tiếp 9: phi hành gia giơ bảng trắng, góc camera giám sát',
        'kind': 'scene',
        'style': IM_STYLE_ROOM,
        'size': '1600x900',
    },
    # Khung 10 là bảng số liệu để HTML đổ số thật vào. Bốn hàng thanh ngang
    # và các ô số phải TRỐNG: model rất hay tự vẽ số liệu vào, lúc đó số
    # của game đè lên số của tranh, đọc không ra.
    'bg-im-10': {
        'prompt': (
            'straight on view of a large computer monitor filling most of the '
            'frame inside a dark control room, the monitor seen dead on with '
            'its bezel just inside the frame edges, '
            'the screen shows a spacecraft telemetry analysis dashboard: four '
            'wide horizontal bar chart rows stacked down the frame, each row a '
            'thin glowing cyan track box with an empty channel, every bar fill '
            'deliberately left completely empty, no bar inside any track, no '
            'fill, no value, '
            'four blank label boxes at the left of the rows left completely '
            'empty and unmarked, every number field and readout left empty, '
            'no digits, no characters anywhere on the screen, '
            'small telemetry waveform graphs traced in the corners of the '
            'screen, thin grid lines, cyan and amber interface elements on a '
            'deep dark blue background, '
            'a few engineers silhouetted at the left and right edges of the '
            'frame watching the screen, faces unreadable in shadow, the screen '
            'glow reflecting along the desk in the foreground'
        ),
        'note': 'chuyển tiếp 10: bảng phân tích telemetry, thanh và ô số để trống',
        'kind': 'scene',
        'style': IM_STYLE_ROOM,
        'size': '1600x900',
    },
    'bg-im-11': {
        'prompt': (
            'wide shot of the NASA mission control room from a low angle, the '
            'camera near the floor of the tiered rows looking up, '
            'the mission director stands at the centre of frame on the raised '
            'command platform behind the front console, his right palm slammed '
            'flat down on the console desk in front of him, arm rigid, weight '
            'leaning into the blow, '
            'the impact captured as a frozen instant: a few small scattered '
            'papers lifting and tilting off the desk surface around his hand, '
            'one sheet caught in the air, a coffee cup rocking on its base, '
            'every engineer in the room has turned toward him, mid turn, all '
            'motion frozen, dozens of faces angled up at the platform, '
            'dramatic backlight from the giant projection screens behind him '
            'silhouetting his shoulders and outlining his vest in bright cyan '
            'rim light, his face in shadow, tense focused atmosphere, '
            + IM_CHARS
        ),
        'note': 'chuyển tiếp 11: giám đốc đập tay xuống bàn, cả phòng quay lại',
        'kind': 'scene',
        'style': IM_STYLE_ROOM,
        'size': '1600x900',
    },
    'bg-im-12': {
        'prompt': (
            'medium close up of the NASA mission director standing behind a '
            'lectern, framed from the chest up, the lectern edge just visible '
            'at the bottom of frame, '
            'his jaw set hard, eyes burning with fierce determination, brow '
            'furrowed, mouth open mid sentence, one hand gripping the lectern '
            'edge, '
            'harsh key light from one side carving deep black shadows across '
            'the far side of his face, the giant NASA projection screens '
            'behind him thrown far out of focus as soft glowing cyan and amber '
            'shapes, the dark room falling away into shadow behind, '
            'the frozen instant of a speech that changes everything, '
            + IM_CHARS
        ),
        'note': 'chuyển tiếp 12: cận giám đốc sau bục, khoảnh khắc bài phát biểu',
        'kind': 'scene',
        'style': IM_STYLE_ROOM,
        'size': '1600x900',
    },
    'bg-im-13': {
        'prompt': (
            'DRAMATIC DIAGONAL COMIC LAYOUT, the frame is cut by a strong '
            'diagonal gutter running from the lower left corner up to the '
            'upper right corner, the gutter filled with flat solid black, '
            'INSET PANEL in the upper left corner above the diagonal: the '
            'mission director at a lectern caught mid shout, his right fist '
            'thrust straight up in the air, mouth wide open, the soaked '
            'emotional peak of the speech, '
            'THE REST OF THE FRAME below and right of the diagonal: an entire '
            'NASA team of engineers and astronauts seen from a dramatic low '
            'angle looking up, dozens of them on their feet, fists thrust high '
            'in the air, faces ablaze with determination, mouths open mid '
            'cheer, ranks of bodies filling the panel from edge to edge, '
            'heroic low angle hero shot, powerful cyan and amber light '
            'blasting from behind them through haze, triumphant energy, '
            + IM_CHARS
        ),
        'note': 'chuyển tiếp 13: ô chéo, giám đốc hô, cả đội giơ nắm đấm',
        'kind': 'scene',
        'style': IM_STYLE_ROOM,
        'size': '1600x900',
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


def call_api(key, prompt, timeout, size=None):
    """Gọi một lần. Trả (ảnh bytes, None) hoặc (None, lỗi)."""
    body_req = {
        'model': MODEL,
        'prompt': prompt,
        'n': 1,
    }
    # Khung dọc cho sprite nhân vật. Model có thể bỏ qua tham số này và trả
    # khung ngang 1376x768 mặc định; prompt đã dặn tỉ lệ người chiếm khung
    # nên vẫn dùng được, nhưng xin đúng khung dọc thì chân không bị tràn.
    if size:
        body_req['size'] = size
    payload = json.dumps(body_req).encode('utf-8')

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


def out_dir_for(spec):
    """Thư mục ghi ảnh gốc: bộ art màn căn cứ (char, icon-sprite, popup) ghi
    ra gen-sprites/ để không bị vòng quét gen/*.png của process-assets.py
    nhặt nhầm vào pipeline cũ."""
    kind = spec.get('kind')
    return SPRITE_DIR if kind in ('char', 'icon-sprite', 'popup') else OUT_DIR


# Khung sinh ảnh cho sprite nhân vật: dọc, cao 640px quy đổi (tỉ lệ 3:4 dọc
# hơn khung ngang 1376x768 mặc định của model). Bản trước để model tự chọn
# khung, nó trả 1376x768 rồi vẽ người lấp đầy chiều cao khung ngang, chân
# tràn ra ngoài mép dưới. Khung dọc cộng với câu "occupies about 80 percent
# of the frame height" trong STYLE_CHAR thì chân còn nguyên.
CHAR_FRAME = {'char': '896x1152'}


def frame_size_for(spec):
    """Kích thước khung xin từ API, theo kind. None là để model tự chọn."""
    return spec.get('size') or CHAR_FRAME.get(spec.get('kind'))


def generate(key, name, spec):
    """Sinh một asset, có thử lại khi gặp lỗi tạm thời."""
    d = out_dir_for(spec)
    d.mkdir(parents=True, exist_ok=True)
    out_path = d / f'{name}.png'

    if out_path.exists() and out_path.stat().st_size > 5000:
        print(f'  [{name}] đã có, bỏ qua. Dùng --force để làm lại.')
        return True

    print(f'  [{name}] {spec["note"]}')
    print(f'    đang gửi yêu cầu, chờ 30 tới 90 giây...')

    # Ghép khối style chung vào mọi prompt để cả bộ ảnh cùng một giọng.
    # Cảnh có người thì dùng biến thể riêng, xem spec['style'].
    full_prompt = spec['prompt'] + ', ' + spec.get('style', STYLE)
    # Icon/strip nào cần tách nền thì phải xin thêm nền xám phẳng, vì model
    # ảnh không xuất alpha thật. Không có câu này thì hậu kỳ matte ra rỗng.
    if spec.get('key_bg'):
        full_prompt += ', ' + ICON_KEY_BG

    for attempt in range(1, MAX_ATTEMPTS + 1):
        t0 = time.time()
        timeout = TIMEOUT_FIRST if attempt == 1 else TIMEOUT_NEXT
        img, err = call_api(key, full_prompt, timeout, size=frame_size_for(spec))
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
            done = 'đã có' if (out_dir_for(v) / f'{k}.png').exists() else 'chưa có'
            print(f'  {k:16} {done:8} {v["note"]}')
        return

    if args.force:
        for k in (ASSETS if args.all else [args.name] if args.name else []):
            p = out_dir_for(ASSETS[k]) / f'{k}.png'
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
