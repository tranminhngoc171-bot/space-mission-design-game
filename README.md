# ABANDONN — Space Mission Design Game

*Một người mắc lại trên Sao Hỏa. Ba người ở Trái Đất phải thiết kế một con tàu đi đón người đó, rồi sống sót cùng nhau trong 258,9 ngày bay.*

Cậu không điều khiển một phi hành gia chạy nhảy trên bề mặt Sao Hỏa. Cậu ngồi trong phòng điều khiển, chọn từng module cho con tàu cứu hộ, nhìn ba thanh ngân sách, khối lượng và delta-v nhích lên, rồi đẩy con tàu đi và nghe ba người bên trong tranh cãi nhau về mọi quyết định. Có lần cậu phải cắt sưởi để dồn điện cho lần đốt hiệu chỉnh. Có lần cậu giữ kênh liên lạc với Trái Đất và trả giá bằng khẩu phần. Không có lựa chọn nào cho không cả. Game này được làm ra để cậu cảm thấy cái giá đó.

**NASA Space Apps Challenge 2026** · Đề bài: [Space Mission Design Game](https://www.spaceappschallenge.org/2026/challenges/space-mission-design-game/)

Chơi thử: **https://bersious.io.vn/nasa**

---

## Câu chuyện và cách chơi

Mười hai khung comic mở đầu không một lời thoại. Cơn bão cát ập tới, đội chạy về tàu, một người bị bỏ lại phía sau. Cậu hiểu chuyện bằng mắt, như xem đoạn mở của một bộ phim.

Sau đó là ba bước gọi tín hiệu về Trái Đất. Ăng-ten chính đã gãy, chỉ còn bộ phát UHF tầm ngắn. Bụi làm tấm pin chỉ còn 35 phần trăm công suất, cấp được 1.820 W mà bộ phát cần 850 W. Cậu phải tắt bớt thiết bị nhưng không được cắt bơm oxy. Rồi bắt đúng cửa sổ 90 giây khi vệ tinh MRO bay ngang, nâng tín hiệu lên 15 dB, đóng gói dữ liệu vào 16 byte và gửi đi 225 triệu km. Tín hiệu tới một trong ba trạm Deep Space Network: Goldstone, Madrid hoặc Canberra.

Đến màn thiết kế tàu, cậu có 12 module chia 8 nhóm. Mỗi module có khối lượng, công suất, giá tiền và một câu nói thật lòng về nó đánh đổi cái gì. Ngân sách không quá 900 triệu USD, tải trọng không quá 70.000 kg, delta-v phải đủ 6.650 m/s cộng dồn qua bốn chặng. Công thức Tsiolkovsky nói rằng ở Isp 320 thì 83 phần trăm khối lượng phải là nhiên liệu. Đó là lý do con tàu cứu hộ không thể nhỏ, và cũng là bài học chính của màn này.

Chặng cuối là chuyến bay. Đường chuyển Hohmann được vẽ thật trên Canvas, có ba mốc đốt hiệu chỉnh. Trong 258,9 ngày có 16 tình huống nảy ra, mỗi tình huống ba phương án. Mỗi phương án làm một vai hài lòng và chọc giận hai vai kia. Đồng thuận tụt quá sâu thì đội tan rã, và cậu không về được tới Sao Hỏa. Nếu thua, game không hiện chữ "Game Over" cho xong chuyện. Nó chỉ ra đúng chỗ cậu đánh đổi sai và giải thích vì sao.

Có hai nhánh kết thúc. Đi hết Giai đoạn 1 thì vào báo cáo tổng kết qua màn bay. Đi tiếp Giai đoạn 2 thì có thêm bốn bước chốt mục tiêu, lắp tàu, kiểm tra và phóng. Báo cáo xếp hạng từ A đến D, đối chiếu thiết kế của cậu với Curiosity, Perseverance và MAVEN.

Giao diện song ngữ Việt và Anh, chuyển bằng một cú bấm, nhớ lựa chọn của cậu giữa các lần mở lại. Chạy tốt trên điện thoại lẫn máy tính.

---

## Nhóm làm game

| Thành viên | Vai trò |
|---|---|
| **Trần Minh Ngọc** — Trưởng dự án | Ý tưởng gốc. Phác họa khung hình, bố cục comic và UI/UX. Thiết kế hệ thống: luồng chơi, bảng tài nguyên, bộ luật đánh đổi và kiến trúc các module. |
| **Nguyễn Thành Thiện Nhân** | Triển khai ý tưởng thành game chạy được. Dựng các màn chơi, nối dữ liệu với engine, kiểm soát các AI agent trong quá trình phát triển, rà soát từng luồng từ mở màn tới kết thúc. |

Repo gốc: https://github.com/tranminhngoc171-bot/space-mission-design-game

Trang web: https://bersious.io.vn/nasa

---

## Đồ đã làm

### Game và mã nguồn

| Thứ | Link hoặc nơi lấy |
|---|---|
| Game chạy trực tiếp | https://bersious.io.vn/nasa |
| Repo chính của nhóm | https://github.com/tranminhngoc171-bot/space-mission-design-game |
| Màn chơi, engine và dữ liệu | [`src/`](src/) — 56 module JavaScript, 34 file CSS, 573 khóa song ngữ Việt và Anh |
| Giai đoạn 2 | [`phase2/`](phase2/) — bốn bước điều khiển sứ mệnh, 12 module JavaScript |
| Dữ liệu gốc | [`data/`](data/) và [`src/data/`](src/data/) — mọi số đều có trường `source`, số ước tính của nhóm được ghi là ước tính |
| Tài liệu thiết kế | [`docs/`](docs/) — đề bài, game design, cân bằng, chấm điểm, nguồn NASA, quy tắc agent, art slot |
| Kịch bản game | `docs/kich-ban-game.txt` |
| Bộ test | [`scripts/`](scripts/) — `test_nasa_data.mjs`, `test_negotiation.mjs`, `test_mission_viz.mjs`, `smoke_engine.mjs` |

### Trình bày và hình ảnh

| Thứ | Nơi lấy |
|---|---|
| Pitch deck chính thức | `ABANDONN - NASA Space Apps Pitch Deck.pptx` |
| Slide thuyết trình bản dựng | `NASA-Game-Thuyet-Trinh.pptx` |
| Bộ logo vector và raster | `NASA-Game-Logo/` — SVG nguồn, PNG các cỡ 32/192/512/1024, WebP, favicon.ico, bản sáng và bản tối |
| Prompt tạo logo | `NASA-Game-Logo-Prompts.md` |
| Hướng dẫn nghệ thuật | `UI_ART_DIRECTION_REPORT.md` |
| Báo cáo ca làm việc | `NIGHT_SHIFT_REPORT.md` |

Các file trình bày và logo nằm trong thư mục lưu trữ trên máy của nhóm, không nằm trong repo vì dung lượng lớn. Cần bản sao thì liên hệ một trong hai người ở bảng trên.

---

## Dữ liệu lấy từ đâu

Mọi con số trong game đều có nguồn. Số nào là ước tính của nhóm thì ghi thẳng là ước tính, không gán bừa cho NASA.

| File | Nội dung |
|---|---|
| `src/data/nasa/rescue_mission.json` | Bốn chặng delta-v 3.570 / 5.594 / 2.080 / 1.000 m/s, thời gian bay 258,9 ngày, chu kỳ giao hội 779,9 ngày, bảng trễ tín hiệu |
| `src/data/nasa/rescue_modules.json` | 12 module tàu, ba loại động cơ Isp 320 / 450 / 900 |
| `src/data/nasa/crew_roles.json` | Ba vai và chủ đề họ phản đối mạnh nhất |
| `src/data/nasa/mars_comms_protocol.json` | Ngân sách điện, dữ liệu MEDA, vệ tinh MRO, sáu gói telemetry, ba trạm DSN cách nhau 120 độ kinh độ |
| `src/data/events/role_negotiations.json` | 16 sự kiện, 48 phương án |

Đọc kỹ hơn tại [`docs/11-NASA-RESOURCES.md`](docs/11-NASA-RESOURCES.md) và [`docs/13-COMMS-SCIENCE.md`](docs/13-COMMS-SCIENCE.md).

---

## Chạy ở máy

Game là HTML, CSS và JavaScript thuần, không cần bước build.

```bash
cd src
python -m http.server 8311
```

Rồi mở http://localhost:8311. Mở thẳng `index.html` bằng `file://` sẽ không chạy, vì game đọc JSON qua `fetch` và trình duyệt chặn ở giao thức file.

Chạy kiểm thử từ gốc repo:

```bash
node scripts/test_nasa_data.mjs
node scripts/test_negotiation.mjs
node scripts/test_mission_viz.mjs
node scripts/smoke_engine.mjs
```

---

## Ghi công

Mã nguồn theo giấy phép MIT. Video intro lấy từ Wikimedia Commons theo giấy phép CC0 1.0. Ảnh bề mặt Sao Hỏa và dữ liệu quỹ đạo thuộc phạm vi công cộng của NASA và USGS. Logo và nhận diện của game do nhóm tự dựng, không dùng biểu trưng NASA làm nhận diện sản phẩm. Biểu trưng NASA chỉ xuất hiện trong trang ghi công.

NASA Space Apps Challenge 2026. Làm bởi Trần Minh Ngọc và Nguyễn Thành Thiện Nhân.
