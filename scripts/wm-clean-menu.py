"""Che watermark ngôi sao 4 cánh ở góc dưới phải ảnh menu mới.

Dùng cv2.inpaint (Navier-Stokes) vì watermark nằm trên vùng cát đỏ có
kết cấu hạt mịn: clone patch sẽ để lại vệt lặp, còn inpaint thì nội
suy từ viền nên hoà vào kết cấu.

Cách dùng: C:\\Python314\\python.exe scripts/wm-clean-menu.py
"""

import sys
from pathlib import Path

import cv2
import numpy as np

SRC = Path.home() / "Desktop" / "ZALO HKT" / "Gemini_Generated_Image_an5t5tan5t5tan5t.png"
OUT_DIR = Path(__file__).resolve().parent.parent / "src" / "assets" / "gen"
OUT = OUT_DIR / "menu-mars-hero.png"

# Hộp watermark đo được trên ảnh gốc 2752x1536: ngôi sao nằm trong
# khoảng x 2592..2687, y 1376..1471. Nới mỗi phía 14px để lấy trọn
# quầng mờ quanh ngôi sao, vì inpaint cần che cả phần nhoè viền.
BOX = (2578, 1362, 2701, 1485)   # x1, y1, x2, y2


def main() -> int:
    if not SRC.exists():
        print("Không thấy ảnh gốc:", SRC)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    img = cv2.imread(str(SRC), cv2.IMREAD_COLOR)
    if img is None:
        print("Không đọc được ảnh:", SRC)
        return 1
    h, w = img.shape[:2]
    print("ảnh gốc:", w, "x", h)

    x1, y1, x2, y2 = BOX
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    # Mặt nạ che: elip mềm bên trong hộp, phủ kín ngôi sao và quầng.
    mask = np.zeros((h, w), dtype=np.uint8)
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    cv2.ellipse(
        mask,
        (cx, cy),
        ((x2 - x1) // 2, (y2 - y1) // 2),
        0, 0, 360, 255, -1,
    )

    # Navier-Stokes, bán kính 11: đủ để tái tạo hạt cát mà không nhoè
    # lan sang vùng tối của bóng đổ.
    cleaned = cv2.inpaint(img, mask, 11, cv2.INPAINT_NS)

    cv2.imwrite(str(OUT), cleaned)
    print("đã ghi:", OUT, f"({OUT.stat().st_size // 1024} KB)")

    # Kiểm nhanh: vùng vừa che không còn điểm sáng bất thường.
    sub = cleaned[y1:y2, x1:x2].astype(np.float32).mean(axis=2)
    ring = cleaned[max(0, y1 - 40):y1, x1:x2].astype(np.float32).mean(axis=2)
    print(f"độ sáng TB trong hộp: {sub.mean():.1f} | viền ngoài: {ring.mean():.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
