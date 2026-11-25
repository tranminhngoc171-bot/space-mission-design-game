
# ABANDONN — Mô Phỏng Thiết Kế Sứ Mệnh Vũ Trụ & Sinh Tồn Sao Hỏa

> **Một phi hành gia bị bỏ lại giữa bão cát Sao Hỏa. Ba chuyên gia tại Trung tâm Điều khiển Trái Đất phải chế tạo một con tàu cứu hộ — và cùng nhau sống sót qua 258,9 ngày bay xuyên hành tinh.**

[![Chơi Trực Tiếp](https://img.shields.io/badge/Chơi_Ngay-bersious.io.vn%2Fnasa-e05a2b?style=for-the-badge)](https://bersious.io.vn/nasa)
[![NASA Space Apps 2026](https://img.shields.io/badge/NASA_Space_Apps-2026-0b3d91?style=for-the-badge)](https://www.spaceappschallenge.org/)
[![Giấy phép: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

**ABANDONN** là tựa game mô phỏng kỹ thuật hệ thống hàng không vũ trụ được phát triển cho **NASA Space Apps Challenge 2026** (*Đề bài: Space Mission Design Game*). 

Ở đây, bạn không điều khiển một anh hùng chạy nhảy trên những cồn cát đỏ. Bạn ngồi trong phòng điều khiển sứ mệnh — tự tay lắp ráp từng phân hệ cho con tàu cứu hộ, nhìn ba thanh **ngân sách, khối lượng và $\Delta v$** ép sát giới hạn vật lý, rồi phóng tàu vào không gian và đối mặt với những cuộc tranh cãi nghẹt thở giữa ba thành viên phi hành đoàn.

*Có lúc bạn buộc phải ngắt hệ thống sưởi khoang lái để dồn điện cho cú đốt hiệu chỉnh quỹ đạo. Có lúc bạn phải giữ kênh liên lạc với Trái Đất và trả giá bằng chính khẩu phần ăn của cả đội. Trong cơ học quỹ đạo, không có lựa chọn nào là miễn phí — và ABANDONN được tạo ra để bạn cảm nhận trọn vẹn sức nặng của từng cái giá đó.*

---

## Câu Chuyện & Trải Nghiệm Gameplay

### 1. Mở Màn Bằng Truyện Tranh Không Lời
Mười hai khung hình truyện tranh vẽ tay mở ra không một dòng thoại. Cơn bão bụi khổng lồ bất ngờ ập tới, cả đội hối hả rút về khoang cất cánh và vô tình bỏ lại một người phía sau. Mọi diễn biến được kể hoàn toàn bằng ngôn ngữ thị giác, như những phút mở đầu của một bộ phim điện ảnh sinh tồn.

### 2. Phân Phối Điện Năng & Bắt Sóng Vệ Tinh (Sao Hỏa)
Đĩa ăng-ten chính đã gãy vụn, chỉ còn bộ phát UHF tầm ngắn hoạt động được. Lớp bụi dày đặc làm tấm pin mặt trời sụt xuống còn **35% công suất** (chỉ cấp được **1.820 W** trong khi bộ phát cần tới **850 W**). 
* Bạn phải tính toán ngắt bớt thiết bị phụ trợ nhưng tuyệt đối không được để hệ thống bơm oxy ngừng chạy.
* Canh chuẩn **cửa sổ 90 giây** khi vệ tinh **Mars Reconnaissance Orbiter (MRO)** bay ngang đỉnh đầu, khuếch đại tỷ số tín hiệu trên nhiễu (SNR) lên **15 dB**, nén gói dữ liệu sinh tồn vào đúng **16 byte** và phóng tín hiệu vượt **225 triệu km** về mạng lưới Deep Space Network của NASA (**Goldstone, Madrid hoặc Canberra**).

### 3. Xưởng Lắp Tàu & Bài Toán Đánh Đổi Kỹ Thuật
Bạn được tự do phối ghép **12 module thuộc 8 nhóm phân hệ** dưới những ràng buộc khắt khe của một sứ mệnh liên hành tinh thật sự:
* **Trần ngân sách:** Không vượt quá **900 triệu USD**
* **Giới hạn tải trọng phóng:** Không vượt quá **70.000 kg**
* **Tổng vận tốc đặc trưng ($\Delta v$):** Phải đạt tối thiểu **6.650 m/s** cộng dồn qua bốn chặng bay

Theo **phương trình tên lửa Tsiolkovsky**, nếu chọn động cơ hóa học có xung riêng $I_{sp} = 320\text{ s}$, tới **83% tổng khối lượng con tàu** bắt buộc phải là nhiên liệu. Càng tham lam chất thêm hàng hóa hay thiết bị nặng, tàu càng ì ạch và đội nguy cơ trễ hẹn cứu hộ.

### 4. Hành Trình 258,9 Ngày & Cuộc Chiến Tâm Lý Trên Khoang Tàu
Đường quỹ đạo chuyển tiếp **Hohmann** được vẽ trực tiếp theo thời gian thực trên nền HTML5 Canvas cùng ba mốc đốt hiệu chỉnh (TCM). Trong suốt **258,9 ngày** lơ lửng giữa khoảng không, **16 biến cố** (tương ứng **48 phương án xử lý**) sẽ lần lượt ập tới. 

Mỗi quyết định đều làm hài lòng một chuyên gia nhưng lại chọc giận hai người còn lại. Nếu chỉ số đồng thuận sụp đổ, nội bộ tan rã và sứ mệnh thất bại. Đặc biệt, khi thua cuộc, game không hiện dòng chữ *"Game Over"* vô hồn — hệ thống sẽ xuất một **Báo cáo Phân tích Nguyên nhân Gốc rễ**, chỉ rõ bạn đã đánh đổi sai ở khâu nào và giải thích cơ sở vật lý phía sau.

### 5. Hai Nhánh Kết Thúc & Đối Chiếu Thực Tế NASA
* **Hoàn tất Giai đoạn 1:** Kết thúc hành trình tiếp sóng, lắp tàu và vượt không gian để nhận bảng đánh giá tổng kết.
* **Tiếp bước Giai đoạn 2:** Trực tiếp điều hành bốn bước kiểm duyệt sứ mệnh chuyên sâu — *Chốt mục tiêu, Tích hợp tàu, Kiểm tra an toàn trước phóng và Điều phối hạ cánh*.
* **Chấm điểm chuẩn NASA:** Thiết kế của bạn được xếp hạng từ **A đến D** và đối chiếu thông số trực tiếp với các sứ mệnh Sao Hỏa huyền thoại: **Curiosity**, **Perseverance** và **MAVEN**.

### Tính Năng Nổi Bật
* **Song ngữ Việt – Anh liền mạch:** Chuyển đổi tức thì chỉ với một cú bấm (`573` khóa ngôn ngữ), tự động ghi nhớ lựa chọn của người chơi.
* **Tương thích đa nền tảng:** Giao diện tự động co giãn tối ưu cho cả màn hình máy tính lẫn điện thoại di động.

---

## Kiến Trúc Mã Nguồn

```text
space-mission-design-game/
├── src/                        # Lõi game: 56 module JS, 34 file CSS, 573 khóa song ngữ Việt - Anh
│   └── data/
│       ├── nasa/               # Thông số sứ mệnh, module tàu, giao thức viễn thông & vai trò phi hành đoàn
│       └── events/             # 16 kịch bản khủng hoảng trên đường bay (48 nhánh lựa chọn)
├── phase2/                     # Luồng điều khiển Giai đoạn 2 (4 bước vận hành, 12 module JS)
├── data/                       # Bộ dữ liệu tham chiếu sứ mệnh
├── docs/                       # Tài liệu thiết kế game, công thức cân bằng, trích dẫn NASA & kịch bản
└── scripts/                    # Bộ kiểm thử tự động Node.js xác thực dữ liệu và engine vật lý

```

---

## Cơ Sở Dữ Liệu Khoa Học

Mọi hằng số vật lý và thông số kỹ thuật trong game đều được trích xuất từ tài liệu khoa học công khai; các tham số được nhóm ước tính để cân bằng trải nghiệm chơi đều được gắn nhãn rõ ràng, không gán ghép tùy tiện cho NASA.

| Tệp dữ liệu | Nội dung chi tiết |
| --- | --- |
| `src/data/nasa/rescue_mission.json` | Ngân sách $\Delta v$ 4 chặng (`3.570 / 5.594 / 2.080 / 1.000 m/s`), thời gian bay `258,9 ngày`, chu kỳ giao hội `779,9 ngày`, bảng độ trễ tín hiệu |
| `src/data/nasa/rescue_modules.json` | 12 module tàu vũ trụ và 3 cấp động cơ đẩy ($I_{sp} = 320 / 450 / 900\text{ s}$) |
| `src/data/nasa/crew_roles.json` | Hồ sơ 3 vai trò chuyên môn trên tàu và các xung đột lợi ích cốt lõi |
| `src/data/nasa/mars_comms_protocol.json` | Ngân sách điện năng, độ đục bụi khí quyển (Mars 2020 MEDA), cửa sổ vệ tinh MRO, 6 gói telemetry, 3 trạm DSN cách nhau $120^\circ$ kinh độ |
| `src/data/events/role_negotiations.json` | 16 sự kiện phát sinh trong chuyến bay và 48 phương án giải quyết |

Chi tiết nguồn tham chiếu khoa học được lưu tại [`docs/11-NASA-RESOURCES.md`](https://www.google.com/search?q=docs/11-NASA-RESOURCES.md) và [`docs/13-COMMS-SCIENCE.md`](https://www.google.com/search?q=docs/13-COMMS-SCIENCE.md).

---

## Cài Đặt & Chạy Thử Trên Máy

Dự án được xây dựng hoàn toàn bằng **HTML5, CSS3 và JavaScript thuần (ES6+)**, không cần bước biên dịch (build).

### Khởi chạy cục bộ

Do game nạp dữ liệu JSON qua `fetch()`, bạn cần chạy qua một máy chủ HTTP cục bộ thay vì mở trực tiếp file qua giao thức `file://`:

```bash
cd src
python -m http.server 8311

```

Sau đó mở trình duyệt tại địa chỉ `http://localhost:8311`.

### Chạy bộ kiểm thử tự động

Từ thư mục gốc của repository (yêu cầu đã cài đặt Node.js):

```bash
node scripts/test_nasa_data.mjs
node scripts/test_negotiation.mjs
node scripts/test_mission_viz.mjs
node scripts/smoke_engine.mjs

```

---

## Nhóm Phát Triển

| Thành viên | Vai trò & Đóng góp |
| --- | --- |
| **Trần Minh Ngọc** *(Trưởng dự án)* | Ý tưởng gốc, phác họa storyboard truyện tranh, thiết kế bố cục UI/UX và kiến trúc hệ thống (luồng trải nghiệm, kinh tế tài nguyên, cơ chế đánh đổi và hệ thống module). |
| **Nguyễn Thành Thiện Nhân** | Hiện thực hóa kỹ thuật, lập trình game engine & tích hợp dữ liệu vật lý, điều phối quy trình phát triển cùng AI agents và kiểm thử toàn diện các luồng chơi. |

---

## Bản Quyền & Ghi Công

* **Mã nguồn:** Phát hành theo giấy phép [MIT License](https://www.google.com/search?q=LICENSE).
* **Tư liệu hình ảnh & dữ liệu:** Video mở đầu sử dụng từ Wikimedia Commons theo giấy phép **CC0 1.0**. Ảnh bề mặt Sao Hỏa và dữ liệu quỹ đạo thuộc phạm vi công cộng (Public Domain) của **NASA** và **USGS**.
* **Quy chuẩn nhận diện:** Toàn bộ tên gọi, biểu trưng và nhận diện đồ họa của **ABANDONN** đều do nhóm tự thiết kế; logo NASA chỉ xuất hiện trong mục ghi công tuân thủ quy định sử dụng tài nguyên truyền thông của NASA.

*Dự án được thực hiện cho NASA Space Apps Challenge 2026.*
