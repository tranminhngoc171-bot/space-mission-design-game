#!/usr/bin/env python3
"""Sinh 6 anh nen SVG cho Phase 2, dung bang mau token cua du an.

Chay:  python scripts/gen-p2-art.py
Ra:    src/assets/art/p2-*.svg  (game tu nhan, khong can sua code)

Anh la schematic/technical illustration, khong chu, khong logo NASA,
phu hop lam nen co overlay toi phia tren.
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "src", "assets", "art")
OUT = os.path.abspath(OUT)

BG_VOID = "#07090d"
BG_PANEL = "#111721"
LINE = "#26313f"
LINE_STRONG = "#35455a"
AMBER = "#e8a33d"
CYAN = "#4fb8c9"
TX_DIM = "#72879d"

W, H = 1600, 900


def wrap(body, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img">\n'
        f"<defs>{defs}</defs>\n"
        f'<rect width="{W}" height="{H}" fill="{BG_VOID}"/>\n'
        f"{body}\n</svg>\n"
    )


def grid(step=80, color=LINE, opacity=".35"):
    lines = []
    for x in range(0, W + 1, step):
        lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>')
    for y in range(0, H + 1, step):
        lines.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>')
    return f'<g stroke="{color}" stroke-width="1" opacity="{opacity}">{"".join(lines)}</g>'


# 1. Radar grid: vong quet + 3 tram
def radar():
    cx, cy = W // 2, H // 2
    rings = []
    for r in (120, 220, 320, 420):
        rings.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LINE}" stroke-width="1.5"/>')
    spokes = []
    import math
    for deg in range(0, 360, 30):
        a = math.radians(deg)
        spokes.append(
            f'<line x1="{cx}" y1="{cy}" x2="{cx + 420 * math.cos(a):.1f}" '
            f'y2="{cy + 420 * math.sin(a):.1f}" stroke="{LINE}" stroke-width="1" opacity=".6"/>'
        )
    # 3 tram cach nhau 120 do
    stations = []
    for i, deg in enumerate((0, 120, 240)):
        a = math.radians(deg - 90)
        x = cx + 300 * math.cos(a)
        y = cy + 300 * math.sin(a)
        stations.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{CYAN}" opacity=".9"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="20" fill="none" stroke="{CYAN}" '
            f'stroke-width="1.5" opacity=".45"/>'
        )
    body = (
        grid(80, LINE, ".25")
        + "".join(rings)
        + "".join(spokes)
        + f'<path d="M {cx} {cy} L {cx + 420} {cy} A 420 420 0 0 0 {cx} {cy - 420} Z" '
        f'fill="{CYAN}" opacity=".07"/>'
        + "".join(stations)
        + f'<circle cx="{cx}" cy="{cy}" r="5" fill="{AMBER}"/>'
    )
    return wrap(body)


# 2. DSN map: ba tram tren dia cau
def dsn():
    cx, cy, r = W // 2, H // 2, 300
    body = [grid(80, LINE, ".22")]
    body.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LINE_STRONG}" stroke-width="2"/>')
    for lat in (-150, -75, 0, 75, 150):
        body.append(f'<ellipse cx="{cx}" cy="{cy + lat}" rx="{r}" ry="{abs(lat) * 0.35 + 12:.0f}" '
                    f'fill="none" stroke="{LINE}" stroke-width="1" opacity=".7"/>')
    for lon in (-200, -100, 0, 100, 200):
        body.append(f'<ellipse cx="{cx + lon}" cy="{cy}" rx="{abs(lon) * 0.3 + 14:.0f}" ry="{r}" '
                    f'fill="none" stroke="{LINE}" stroke-width="1" opacity=".7"/>')
    # 3 tram: Goldstone, Madrid, Canberra cach 120 do
    import math
    for i, deg in enumerate((0, 120, 240)):
        a = math.radians(deg - 90)
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{AMBER}"/>')
        body.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" '
                    f'stroke="{AMBER}" stroke-width="1" stroke-dasharray="6 8" opacity=".5"/>')
    body.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 40}" fill="none" stroke="{CYAN}" '
                f'stroke-width="1" stroke-dasharray="4 10" opacity=".4"/>')
    return wrap("".join(body))


# 3. Assembly bay: khung gian thap + tau dang lap
def assembly():
    body = [grid(100, LINE, ".2")]
    # gian thap
    for x in (260, 1340):
        body.append(f'<rect x="{x - 14}" y="120" width="28" height="660" fill="none" '
                    f'stroke="{LINE_STRONG}" stroke-width="2"/>')
        for y in range(160, 760, 90):
            body.append(f'<line x1="{x - 14}" y1="{y}" x2="{x + 14}" y2="{y + 45}" '
                        f'stroke="{LINE}" stroke-width="1.5"/>')
    body.append(f'<line x1="260" y1="150" x2="1340" y2="150" stroke="{LINE_STRONG}" stroke-width="2"/>')
    # than tau (hinh vòm + than)
    body.append(f'<path d="M 800 250 C 900 250 950 330 950 430 L 950 640 L 650 640 L 650 430 '
                f'C 650 330 700 250 800 250 Z" fill="{BG_PANEL}" stroke="{LINE_STRONG}" stroke-width="2"/>')
    body.append(f'<rect x="700" y="470" width="200" height="90" fill="none" stroke="{CYAN}" '
                f'stroke-width="1.5" opacity=".8"/>')
    # chan đáp
    body.append(f'<path d="M 700 640 L 660 720 M 900 640 L 940 720" stroke="{LINE_STRONG}" stroke-width="3"/>')
    body.append(f'<line x1="640" y1="720" x2="700" y2="720" stroke="{LINE_STRONG}" stroke-width="3"/>')
    body.append(f'<line x1="900" y1="720" x2="960" y2="720" stroke="{LINE_STRONG}" stroke-width="3"/>')
    # day noi
    body.append(f'<path d="M 260 300 L 650 400 M 950 400 L 1340 300" stroke="{CYAN}" '
                f'stroke-width="1.5" stroke-dasharray="5 7" opacity=".6"/>')
    return wrap("".join(body))


# 4. Launch pad: be phong + khoi loi
def launch():
    body = [grid(100, LINE, ".18")]
    body.append(f'<rect x="0" y="700" width="{W}" height="200" fill="{BG_PANEL}" opacity=".7"/>')
    # be phong
    body.append(f'<path d="M 520 700 L 1080 700 L 1180 860 L 420 860 Z" fill="none" '
                f'stroke="{LINE_STRONG}" stroke-width="2"/>')
    # ten lua
    body.append(f'<path d="M 800 180 C 850 240 860 320 860 420 L 860 640 L 740 640 L 740 420 '
                f'C 740 320 750 240 800 180 Z" fill="{BG_PANEL}" stroke="{LINE_STRONG}" stroke-width="2"/>')
    body.append(f'<path d="M 740 640 L 720 700 L 880 700 L 860 640 Z" fill="none" '
                f'stroke="{LINE_STRONG}" stroke-width="2"/>')
    # khoi loi
    body.append(f'<path d="M 770 700 C 770 780 785 830 800 870 C 815 830 830 780 830 700 Z" '
                f'fill="{AMBER}" opacity=".55"/>')
    body.append(f'<path d="M 785 700 C 785 760 792 800 800 830 C 808 800 815 760 815 700 Z" '
                f'fill="{AMBER}" opacity=".85"/>')
    # thap dich vu
    body.append(f'<rect x="1020" y="260" width="18" height="440" fill="none" stroke="{LINE}" stroke-width="2"/>')
    for y in range(300, 680, 60):
        body.append(f'<line x1="1020" y1="{y}" x2="1060" y2="{y}" stroke="{LINE}" stroke-width="1.5"/>')
    return wrap("".join(body))


# 5. Mars approach: sao Hoả + tau tiep can
def approach():
    cx, cy, r = 1050, 470, 260
    body = [grid(100, LINE, ".15")]
    body.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#2a1512" stroke="{LINE_STRONG}" stroke-width="2"/>')
    # vung va cham
    for dx, dy, rr in ((-70, -60, 46), (40, 30, 64), (-20, 90, 34), (90, -90, 28)):
        body.append(f'<circle cx="{cx + dx}" cy="{cy + dy}" r="{rr}" fill="#3d1f19" opacity=".8"/>')
    # tau nho dang bay toi
    body.append(f'<path d="M 300 300 L 360 330 L 340 390 L 280 360 Z" fill="{BG_PANEL}" '
                f'stroke="{CYAN}" stroke-width="2"/>')
    body.append(f'<line x1="360" y1="330" x2="470" y2="360" stroke="{CYAN}" stroke-width="1.5" '
                f'stroke-dasharray="5 7" opacity=".7"/>')
    body.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 60}" fill="none" stroke="{CYAN}" '
                f'stroke-width="1" stroke-dasharray="3 12" opacity=".35"/>')
    return wrap("".join(body))


# 6. Summary bg: lưới báo cáo + đường quỹ đạo
def summary():
    body = [grid(80, LINE, ".2")]
    # quy dao Hohmann
    body.append(f'<ellipse cx="420" cy="450" rx="300" ry="120" fill="none" stroke="{LINE_STRONG}" '
                f'stroke-width="1.5" transform="rotate(-18 420 450)"/>')
    body.append(f'<ellipse cx="1180" cy="450" rx="220" ry="90" fill="none" stroke="{LINE_STRONG}" '
                f'stroke-width="1.5" transform="rotate(-18 1180 450)"/>')
    body.append(f'<circle cx="420" cy="450" r="10" fill="{AMBER}"/>')
    body.append(f'<circle cx="1180" cy="450" r="7" fill="{CYAN}"/>')
    body.append(f'<path d="M 430 450 Q 800 250 1173 450" fill="none" stroke="{CYAN}" '
                f'stroke-width="1.5" stroke-dasharray="7 9" opacity=".7"/>')
    # khung bao cao
    for i, y in enumerate((180, 300, 420, 540, 660)):
        body.append(f'<rect x="180" y="{y}" width="1240" height="70" fill="none" '
                    f'stroke="{LINE}" stroke-width="1" opacity=".55"/>')
    return wrap("".join(body))


FILES = {
    "p2-radar-grid.svg": radar,
    "p2-dsn-map.svg": dsn,
    "p2-assembly-bay.svg": assembly,
    "p2-launch-pad.svg": launch,
    "p2-mars-approach.svg": approach,
    "p2-summary-bg.svg": summary,
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in FILES.items():
        path = os.path.join(OUT, name)
        svg = fn()
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print(f"{name:26} {len(svg):7} bytes")
    print("ghi vao:", OUT)