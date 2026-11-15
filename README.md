# Space Mission Design Game

Một người sống sót trên Sao Hỏa, một đội cứu hộ ba người ở Trái Đất, và 258,9 ngày bay giữa hai nơi.

Người chơi gửi được tín hiệu cầu cứu, thiết kế con tàu đi đón mình, rồi bay suốt tám tháng rưỡi trong khi ba phi hành gia tranh cãi nhau về từng quyết định. Mỗi lựa chọn đều mất một thứ để được một thứ khác, và game luôn nói rõ cái giá trước khi bắt người chơi trả.

**NASA Space Apps Challenge 2026** · Đề bài: [Space Mission Design Game](https://www.spaceappschallenge.org/2026/challenges/space-mission-design-game/)

Địa chỉ chơi: **https://bersious.io.vn/nasa**

---

## Đội

| GitHub | Phụ trách |
|---|---|
| [@tranminhngoc171-bot](https://github.com/tranminhngoc171-bot) | Engine mô phỏng, chấm điểm, dữ liệu NASA, đàm phán vai trò |
| [@bersious](https://github.com/bersious) | Giao diện, màn chơi, kể chuyện, art, âm thanh, deploy |

Ngọc giữ quyền admin repo, Thiện Nhân giữ quyền write. Quy tắc chia vùng file nằm trong `docs/14-AGENT-RULES.md`, đọc trước khi viết dòng code đầu tiên vì hai agent chạy song song.

---

## Bốn chặng chơi

```
Tỉnh dậy          Gửi cầu cứu       Thiết kế tàu       Bay 258,9 ngày
trong Hab    →    3 bước viễn thông  → 12 module    →  16 tình huống đàm phán
(comic 12 khung)  (trạm MRO, DSN)    (ngân sách,       (đồng thuận đội,
                                      khối lượng,      3 mối quan hệ)
                                      delta-v)
```

### Chặng 1: mở màn dạng truyện tranh

Mười hai khung hình không một chữ nào. Một cơn bão cát, một đội chạy về tàu, một người bị bỏ lại. Người chơi hiểu chuyện bằng mắt, giống đoạn mở phim, không có phụ đề giải thích.

Các khung dồn lại thành trang truyện: khung cũ thu nhỏ thành ô nhỏ góc trên trái trong khi khung mới hiện lớn bên cạnh, ô vát chéo cho khoảnh khắc phát hiện nguy hiểm, khung kết chương viền kép. Bố cục này do người vẽ phác thảo tay, xem `docs/15-ART-SLOTS.md`.

### Chặng 2: liên lạc Trái Đất, ba bước

Ăng-ten chính gãy, chỉ còn bộ phát UHF tầm ngắn. Người chơi phải:

1. **Cân bằng điện năng.** Bụi dày làm pin mặt trời chỉ còn 35 phần trăm, cấp được 1.820 W. Bộ phát cần 850 W. Phải tắt bớt thiết bị để dôi ra 650 W, nhưng không được tắt bơm oxy và sưởi chính.
2. **Bắt nhịp vệ tinh.** Mars Reconnaissance Orbiter bay ngang qua trong cửa sổ 90 giây. Chỉnh góc ngẩng và tần số UHF 401,5 MHz cho tín hiệu đạt 15 dB trở lên.
3. **Đóng gói dữ liệu.** Sáu gói telemetry, chỉ được gửi ba gói trong 16 byte. Gửi xong thì tín hiệu đi 225 triệu km, mất 12 phút 30 giây, bắt vào một trong ba trạm Deep Space Network: Goldstone, Madrid, Canberra.

### Chặng 3: thiết kế tàu cứu hộ

Mười hai module chia tám nhóm: động cơ, điện, liên lạc, nhiên liệu, sinh hoạt, chắn bức xạ, hạ cánh, khoa học. Mỗi module có khối lượng, công suất, giá tiền, và một câu nói rõ nó đánh đổi cái gì.

Ba thanh không được vượt:

| Giới hạn | Ngưỡng | Vượt thì |
|---|---|---|
| Ngân sách | 900 triệu USD | Không phóng được |
| Tải trọng tên lửa | 70.000 kg lên quỹ đạo thấp | Không phóng được |
| Delta-v | 6.650 m/s cộng dồn bốn chặng | Không tới được Sao Hỏa |

Delta-v bốn chặng: rời quỹ đạo thấp 3.570, bay nhật tâm 5.594, bắt vào quỹ đạo Sao Hỏa 2.080, hạ cánh 1.000 m/s. Công thức Tsiolkovsky cho biết ở Isp 320 cần **83 phần trăm khối lượng là nhiên liệu** để có 5.600 m/s. Đó là lý do tàu cứu hộ phải to, và cũng là bài học chính của màn này.

### Chặng 4: bay và đàm phán

Bản đồ quỹ đạo vẽ đường chuyển Hohmann thật trên Canvas, có ba mốc đốt hiệu chỉnh quỹ đạo. Trong 258,9 ngày, mười sáu tình huống nảy ra theo bốn giai đoạn: bay xa Trái Đất, tiếp cận Sao Hỏa, hạ cánh, trên mặt đất.

Mỗi tình huống có ba phương án, mỗi phương án làm hài lòng một vai và chọc giận hai vai còn lại. Chỉ số đồng thuận tụt thì đội tan rã và màn chơi thua. Ví dụ: tắt sưởi để dồn điện cho lần đốt hiệu chỉnh, hay giữ liên lạc với Trái Đất thay vì tiết kiệm điện, hay bỏ bốn mươi ký mẫu đá để kịp cửa sổ về.

---

## Dữ liệu lấy từ đâu

Mọi con số đều có trường `source` ghi rõ nguồn. Số nào là ước tính của nhóm làm game thì ghi thẳng là ước tính, không gán bừa cho NASA.

| File | Nội dung |
|---|---|
| `src/data/nasa/rescue_mission.json` | Bốn chặng delta-v, thời gian bay, chu kỳ giao hội 779,9 ngày, bảng trễ tín hiệu, hằng số vật lý |
| `src/data/nasa/rescue_modules.json` | Mười hai module tàu, ba loại động cơ Isp 320, 450, 900 |
| `src/data/nasa/crew_roles.json` | Ba vai, chủ đề họ phản đối mạnh, chỉ số họ cải thiện |
| `src/data/nasa/mars_comms_protocol.json` | Ngân sách điện, dữ liệu MEDA, vệ tinh MRO, sáu gói telemetry, ba trạm DSN |
| `src/data/events/role_negotiations.json` | Mười sáu sự kiện, bốn mươi tám phương án |
| `data/*.json` | Bảng cân bằng gốc: thiết bị, quỹ đạo, tên lửa, sự kiện, bối cảnh |

Tài liệu phân tích: `docs/11-NASA-RESOURCES.md` (777 dòng, chín nguồn NASA đã mở và đọc), `docs/13-COMMS-SCIENCE.md` (vì sao phải có trạm trung chuyển, vì sao 401,5 MHz, vì sao cần ba trạm DSN cách nhau 120 độ kinh độ).

---

## Cấu trúc repo

```
docs/                 tài liệu thiết kế và phân tích
  logs/               nhật ký làm việc, ghi quyết định
data/                 bảng số liệu gốc, nguồn sự thật cho mọi con số cân bằng
src/                  37 module JavaScript, 20 file CSS
  data/nasa/          dữ liệu NASA đã kiểm nguồn
  data/events/        16 sự kiện đàm phán
  assets/art/         ảnh cảnh và icon (WebP)
  assets/audio/       nhạc nền, hiệu ứng
  assets/video/       video intro
  css/tokens.css      toàn bộ màu, cỡ chữ, khoảng cách
scripts/              sinh ảnh, xử lý ảnh, mô phỏng cân bằng, xuất kịch bản
```

### Các module chính

| File | Việc nó làm |
|---|---|
| `prologue.js` | Mười hai khung comic không lời thoại, hiệu ứng thu nhỏ ô và mở mí mắt |
| `story.js` | Màn kể chuyện dự phòng, 24 lượt song ngữ |
| `comms.js` | Ba bước viễn thông: điện, ăng-ten, gói tin |
| `rescue-designer.js` | Thiết kế tàu, ba thanh giới hạn, kiểm tra thiết kế |
| `flight.js` | Bản đồ quỹ đạo ghép panel đàm phán |
| `negotiation.js` | Logic đồng thuận đội, không dính DOM, test được bằng node |
| `nasa-data.js` | Tám hàm thuần: Tsiolkovsky, trễ tín hiệu, kiểm tra thiết kế |
| `mission-viz.js` | Vẽ quỹ đạo Hohmann trên Canvas |
| `base.js` | Màn căn cứ sinh tồn, bảy chỉ số, sáu hành động |
| `save-game.js` | Lưu tiến trình tự động, gói chín khóa thành một bản lưu |
| `i18n.js` | 802 khóa song ngữ Việt và Anh |

---

## Chạy thử ở máy

Game là HTML, CSS, JavaScript thuần, không cần bước build.

```bash
cd src
python -m http.server 8311
# mở http://localhost:8311
```

Mở thẳng file `index.html` bằng `file://` sẽ không chạy, vì game đọc dữ liệu JSON qua `fetch` và trình duyệt chặn thao tác đó ở giao thức file.

### Chạy kiểm thử

```bash
node scripts/test_nasa_data.mjs       # 26 mục
node scripts/test_negotiation.mjs     # 1026 mục
node scripts/test_mission_viz.mjs     # 119 mục
node scripts/smoke_engine.mjs         # engine và chấm điểm
python scripts/sim-35-sol.py          # mô phỏng 35 ngày sinh tồn
```

---

## Bản quyền và ghi công

Mã nguồn theo giấy phép MIT.

Video intro lấy từ Wikimedia Commons, giấy phép CC0 1.0. Ảnh bề mặt Sao Hỏa và các dữ liệu quỹ đạo thuộc phạm vi công cộng của NASA và USGS. Tra cứu chi tiết từng ảnh trong `src/assets/video/README.md` và `src/assets/art/asset-manifest.json`.
