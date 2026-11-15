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

# ------------------------------------------- bộ art màn căn cứ thiết kế lại
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
STYLE_CHAR = (
    STYLE_HARD + ', '
    'full body character sprite of one single astronaut, '
    'head to boots completely inside the frame, standing vertically, '
    'both boots and their soles fully visible with clear empty grey space '
    'below the feet, generous empty margin above the head, '
    'nothing floating in the empty space beside the body, '
    'no stray marks, no props floating in the air, '
    'background is a single flat uniform mid grey #7A7A7A, '
    'no gradient, no vignette, no floor plane, no horizon, no scenery, '
    'no props behind the figure, no cast shadow on the background, '
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


def out_dir_for(spec):
    """Thư mục ghi ảnh gốc: bộ art màn căn cứ (char, icon-sprite, popup) ghi
    ra gen-sprites/ để không bị vòng quét gen/*.png của process-assets.py
    nhặt nhầm vào pipeline cũ."""
    kind = spec.get('kind')
    return SPRITE_DIR if kind in ('char', 'icon-sprite', 'popup') else OUT_DIR


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
