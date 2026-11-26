# Ảnh sinh cho Phase 2

Sinh bởi `scripts/gen-p2-art.py`. SVG vector, dùng đúng bảng màu trong `src/css/tokens.css`, không chữ, không logo NASA, tỉ lệ 16:9 (1600×900). Mỗi file dưới 4KB.

| File | Dùng cho | Nội dung |
|---|---|---|
| `p2-radar-grid.svg` | Bước 1, khung radar | 4 vòng đồng tâm, 12 tia, 3 điểm trạm cách 120°, quạt quét |
| `p2-dsn-map.svg` | Thẻ ba trạm DSN | Hình cầu kinh vĩ với 3 trạm nối về tâm |
| `p2-assembly-bay.svg` | Bước 2, xưởng lắp ráp | Gian tháp hai bên, thân tàu giữa, hai đường nối đối xứng |
| `p2-launch-pad.svg` | Bước 4, bệ phóng | Bệ, tên lửa, khối lửa, tháp dịch vụ |
| `p2-mars-approach.svg` | Bước 4, tiếp cận Sao Hỏa | Hành tinh, vùng bề mặt, tàu bay tới |
| `p2-summary-bg.svg` | Báo cáo tổng kết | Hai quỹ đạo, đường chuyển Hohmann, khung bảng |

Ảnh được đặt ở hai nơi:
- `src/assets/art/` theo đúng khe của `docs/15-ART-SLOTS.md`, game tự nhận.
- `phase2/assets/` để CSS trong `phase2/` dùng đường dẫn tương đối `./assets/`.

Muốn đổi nội dung ảnh thì sửa hàm tương ứng trong `scripts/gen-p2-art.py`, chạy lại script, rồi copy sang cả hai thư mục.
