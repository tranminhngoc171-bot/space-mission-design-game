
from PIL import Image
from pathlib import Path
src = Path(r"C:\Users\nguye\workspace\nasa-space-apps-2026\team-repo\src\assets\gen\menu-mars-hero.png")
out = Path(r"C:\Users\nguye\workspace\nasa-space-apps-2026\team-repo\src\assets\art")
im = Image.open(src).convert("RGB")
print("goc:", im.size)
# Xuat 1920 rong (du cho 1440p va 1080p), giu ty le
for wpx, q, name in [(1920, 84, "menu-mars-hero.webp"), (1280, 82, "menu-mars-hero-1280.webp")]:
    h = round(im.size[1] * wpx / im.size[0])
    r = im.resize((wpx, h), Image.LANCZOS)
    p = out / name
    r.save(p, "WEBP", quality=q, method=6)
    print(f"{name}: {r.size} {p.stat().st_size//1024} KB")
# Anh trich cho man hep: cat giua lay vung co tau va phi hanh gia
wpx = 900
h = round(im.size[1] * wpx / im.size[0])
r = im.resize((wpx, h), Image.LANCZOS)
p = out / "menu-mars-hero-900.webp"
r.save(p, "WEBP", quality=82, method=6)
print(f"menu-mars-hero-900.webp: {r.size} {p.stat().st_size//1024} KB")
