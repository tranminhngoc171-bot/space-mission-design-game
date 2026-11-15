# Ảnh minh hoạ màn mở đầu — nguồn & giấy phép

Năm ảnh trong thư mục này được dựng từ ảnh gốc của NASA bằng
`scripts/build_scene_plates.py`. Tất cả ảnh gốc đều là **public domain**
(tác phẩm của chính phủ Hoa Kỳ, không có bản quyền theo 17 U.S.C. §105) —
dùng được cho cả mục đích thương mại, không cần xin phép. Ghi credit là
phép lịch sự, không phải nghĩa vụ pháp lý.

Credit chuẩn của NASA: `NASA/JPL-Caltech` (ảnh do phòng thí nghiệm JPL thực hiện).

## Quy trình xử lý chung

Mỗi ảnh gốc được: cắt về 16:9 → resize 1600×900 (Lanczos) → giảm bão hoà còn
~35% → phủ màu `#6b3413` ở mức 0.30 → brightness 0.80, contrast 1.06 →
vignette radial 0.45 → grain ±6 → JPEG q=86, progressive.

Hai ảnh có điều chỉnh riêng (ghi trong `SCENES` của script) để giữ được chi
tiết mà lớp bụi/grading làm mất.

## Danh sách

### 1. `mars-surface.jpg` — cảnh 1: phi hành gia làm việc trên bề mặt

- **NASA ID:** PIA24031 — "NASA Astronauts on Mars (Illustration)"
- **Trang:** https://images.nasa.gov/details/PIA24031
- **File gốc:** https://images-assets.nasa.gov/image/PIA24031/PIA24031~orig.jpg
- **Kích thước gốc:** 1600×900
- **Loại:** minh hoạ kỹ thuật số (concept art) của NASA, **không phải ảnh chụp** —
  chưa có người trên Sao Hoả. Hai phi hành gia (một đứng thao tác, một quỳ lấy
  mẫu), một tháp giàn, rover ở hậu cảnh trái.
- **Kết quả:** 1600×900, **275,3 KB**
- **Giấy phép:** NASA public domain (NASA/JPL-Caltech)

### 2. `storm-coming.jpg` — cảnh 2: bão bụi đang tới

- **NASA ID:** PIA22520 — "Curiosity's View of the June 2018 Dust Storm"
  (nửa trái, khung ngày 7/6/2018, τ ≈ 1,5)
- **Trang:** https://images.nasa.gov/details/PIA22520
- **File gốc:** https://images-assets.nasa.gov/image/PIA22520/PIA22520~orig.jpg
- **Kích thước gốc:** 4054×1808 (ảnh ghép 2 khung so sánh)
- **Loại:** ảnh chụp thật từ rover Curiosity (Mastcam), ghép panorama
- **Kết quả:** 1600×900, **230,8 KB** (contrast 1.70 + unsharp 120 để giữ
  đường sống núi mà lớp bụi làm nhoè)
- **Giấy phép:** NASA public domain (NASA/JPL-Caltech/MSSS)

### 3. `storm-impact.jpg` — cảnh 3: bão đã ập xuống

- **NASA ID:** PIA22520 — cùng ảnh trên, **nửa phải, khung ngày 10/6/2018, τ ≈ 8**
  (chân trời bị bụi nuốt hoàn toàn)
- **Trang:** https://images.nasa.gov/details/PIA22520
- **File gốc:** https://images-assets.nasa.gov/image/PIA22520/PIA22520~orig.jpg
- **Loại:** ảnh chụp thật từ rover Curiosity, ghép panorama
- **Kết quả:** 1600×900, **199,4 KB**
- **Giấy phép:** NASA public domain (NASA/JPL-Caltech/MSSS)

### 4. `departure.jpg` — cảnh 4: tàu rời bề mặt

- **NASA ID:** PIA23496 — "Mars Ascent Vehicle Launching with Samples
  (Artist's Concept)"
- **Trang:** https://images.nasa.gov/details/PIA23496
- **File gốc:** https://images-assets.nasa.gov/image/PIA23496/PIA23496~large.jpg
- **Kích thước gốc:** 1920×1435
- **Loại:** concept art của NASA/JPL-Caltech (CG render) — Mars Sample Return,
  tầng bay lên (MAV) phóng khỏi bệ đáp. Cắt từ mép trên để giữ nguyên thân tên lửa.
- **Kết quả:** 1600×900, **236,5 KB**
- **Giấy phép:** NASA public domain (NASA/JPL-Caltech)

### 5. `awake.jpg` — cảnh 5: tỉnh dậy trong khoang

- **NASA ID:** as11-36-5390 — "View of Astronaut Edwin Aldrin Jr. in Lunar Module"
- **Trang:** https://images.nasa.gov/details/as11-36-5390
- **File gốc:** https://images-assets.nasa.gov/image/as11-36-5390/as11-36-5390~orig.jpg
- **Kích thước gốc:** 1896×1892
- **Loại:** ảnh chụp thật — Buzz Aldrin trong module mặt trăng Eagle, Apollo 11,
  7/1969. Một nguồn sáng gắt từ cửa sổ tam giác, thân khoang chìm trong tối.
- **Xử lý riêng:** tint lạnh `#222a33` ở 0.22 (thay vì nâu cam) để giữ quầng
  xanh ở cửa sổ — tông cyan này khớp điểm nhấn `#4fb8c9` của game.
- **Kết quả:** 1600×900, **236,8 KB**
- **Giấy phép:** NASA public domain (NASA/JPL-Caltech)

## Tổng

| File | Kích thước | Dung lượng | Chụp thật? |
|---|---|---|---|
| mars-surface.jpg | 1600×900 | 275,3 KB | không (concept art) |
| storm-coming.jpg | 1600×900 | 230,8 KB | có (Curiosity, 7/6/2018) |
| storm-impact.jpg | 1600×900 | 199,4 KB | có (Curiosity, 10/6/2018) |
| departure.jpg | 1600×900 | 236,5 KB | không (concept art) |
| awake.jpg | 1600×900 | 236,8 KB | có (Apollo 11, 1969) |

Tổng dung lượng: ~1,18 MB cho cả 5 ảnh.

## Không dùng gì

Không có ảnh nào từ phim *The Martian* (tài sản của 20th Century Studios /
Disney) hay bất kỳ nguồn có bản quyền nào khác. Không dùng ảnh stock.

## Dựng lại

```bash
python scripts/build_scene_plates.py
```

Script đọc ảnh gốc từ `%LOCALAPPDATA%\hermes\cache\scratch\nasasrc`. Tải lại
ảnh gốc bằng các URL ở trên nếu cache đã bị xoá.
