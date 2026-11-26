# ABANDONN — Mô Phỏng Thiết Kế Sứ Mệnh Vũ Trụ & Sinh Tồn Sao Hỏa

> **Một phi hành gia bị bỏ lại sau cơn bão cát trên Sao Hỏa. Ba chuyên gia tại Trung tâm Điều khiển Trái Đất phải thiết kế tàu cứu hộ — và giữ cho cả đội sống sót suốt 258,9 ngày bay liên hành tinh.**

[![Chơi Trực Tiếp](https://img.shields.io/badge/Chơi_Ngay-bersious.io.vn%2Fnasa-e05a2b?style=for-the-badge)](https://bersious.io.vn/nasa)
[![NASA Space Apps 2026](https://img.shields.io/badge/NASA_Space_Apps-2026-0b3d91?style=for-the-badge)](https://www.spaceappschallenge.org/)
[![Giấy phép: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

**ABANDONN** là game mô phỏng kỹ thuật hệ thống hàng không vũ trụ, được thực hiện cho **NASA Space Apps Challenge 2026** (*Đề bài: Space Mission Design Game*).

Thay vì trực tiếp điều khiển nhân vật đi khám phá bề mặt hành tinh, bạn ngồi ở ghế điều phối sứ mệnh: tự lắp ráp từng phân hệ cho tàu cứu hộ sao cho khớp các giới hạn về **ngân sách, khối lượng và $\Delta v$**, rồi theo dõi con tàu vượt không gian qua những quyết định đánh đổi giữa kỹ thuật và tâm lý phi hành đoàn. Có lúc bạn phải tắt hệ thống sưởi để dồn điện cho cú đốt hiệu chỉnh quỹ đạo, hoặc cắt giảm khẩu phần để duy trì liên lạc về Trái Đất.

---

## Gameplay & Cốt Truyện

### 1. Mở Màn Bằng Truyện Tranh Không Lời
12 khung tranh vẽ tay mở đầu không dùng lời thoại: cơn bão bụi ập đến bất ngờ, cả đội buộc phải rút khẩn cấp lên khoang cất cánh và vô tình bỏ sót một thành viên trên bề mặt Sao Hỏa.

### 2. Quản Lý Điện Năng & Phát Tín Hiệu Cứu Hộ
Đĩa ăng-ten chính bị hỏng, chỉ còn bộ phát UHF tầm ngắn hoạt động. Lớp bụi phủ dày khiến pin mặt trời chỉ đạt **35% công suất** (**1.820 W**), trong khi bộ phát đã ngốn mất **850 W**.
* Ngắt bớt các thiết bị phụ trợ nhưng phải giữ cho hệ thống bơm oxy luôn chạy.
* Canh đúng **cửa sổ 90 giây** khi vệ tinh **Mars Reconnaissance Orbiter (MRO)** bay qua đỉnh đầu, khuếch đại tỷ số tín hiệu trên nhiễu (SNR) lên **15 dB**, nén gói tin sinh tồn vào đúng **16 byte** để gửi vượt **225 triệu km** về mạng lưới Deep Space Network của NASA (**Goldstone, Madrid hoặc Canberra**).

### 3. Xưởng Lắp Tàu & Bài Toán Đánh Đổi Kỹ Thuật
Bạn phối ghép **12 module thuộc 8 nhóm phân hệ** dưới ba ràng buộc thực tế của một chuyến bay liên hành tinh:
* **Ngân sách tối đa:** **900 triệu USD**
* **Tải trọng phóng tối đa:** **70.000 kg**
* **Tổng vận tốc đặc trưng ($\Delta v$):** Tối thiểu **6.650 m/s** qua 4 chặng bay

Theo **phương trình tên lửa Tsiolkovsky**, nếu dùng động cơ hóa học có xung riêng $I_{sp} = 320\text{ s}$, riêng nhiên liệu đã chiếm **83% tổng khối lượng tàu**. Càng gắn thêm nhiều thiết bị nặng, tàu càng khó đạt đủ $\Delta v$ hoặc trễ cửa sổ phóng.

### 4. Hành Trình 258,9 Ngày & Xung Đột Trên Tàu
Quỹ đạo chuyển tiếp **Hohmann** cùng 3 mốc đốt hiệu chỉnh (TCM) được mô phỏng trực tiếp trên HTML5 Canvas. Trong suốt **258,9 ngày** bay, **16 sự cố** (tương ứng **48 phương án xử lý**) sẽ lần lượt xảy ra.

Mỗi lựa chọn thường hợp ý một chuyên gia nhưng lại gây bất mãn cho hai người còn lại; nếu chỉ số đồng thuận chạm đáy, sứ mệnh thất bại. Khi thua cuộc, thay vì chỉ báo *"Game Over"*, game sẽ xuất **Báo cáo Phân tích Nguyên nhân Gốc rễ** để chỉ rõ điểm sai sót và phần vật lý đứng sau đó.

### 5. Hai Giai Đoạn Chơi & Chấm Điểm Chuẩn NASA
* **Giai đoạn 1:** Tiếp sóng từ Sao Hỏa, lắp ráp tàu, vượt hành trình bay và nhận bảng đánh giá tổng kết.
* **Giai đoạn 2:** Trực tiếp xử lý 4 bước kiểm duyệt chuyên sâu — *Chốt mục tiêu, Tích hợp tàu, Kiểm tra an toàn trước phóng và Điều phối hạ cánh*.
* **Đối chiếu thực tế:** Tàu của bạn được xếp hạng từ **A đến D** và so sánh thông số trực tiếp với các sứ mệnh Sao Hỏa thực tế như **Curiosity**, **Perseverance** và **MAVEN**.

### Tính Năng Khác
* **Song ngữ Việt – Anh:** Chuyển đổi tức thì (`573` khóa ngôn ngữ), tự động lưu lựa chọn của người chơi.
* **Tương thích đa thiết bị:** Giao diện tự điều chỉnh cho cả màn hình máy tính và điện thoại.

---

## Cấu Trúc Dự Án

```text
space-mission-design-game/
├── src/                        # Mã nguồn chính: 56 module JS, 34 file CSS, 573 khóa song ngữ Việt - Anh
│   └── data/
│       ├── nasa/               # Thông số sứ mệnh, module tàu, giao thức viễn thông & vai trò phi hành đoàn
│       └── events/             # 16 kịch bản sự cố trên đường bay (48 nhánh lựa chọn)
├── phase2/                     # Luồng điều khiển Giai đoạn 2 (4 bước vận hành, 12 module JS)
├── data/                       # Dữ liệu tham chiếu sứ mệnh
├── docs/                       # Tài liệu thiết kế, công thức cân bằng, nguồn trích dẫn NASA & storyboard
└── scripts/                    # Bộ test tự động (Node.js) kiểm tra dữ liệu và engine vật lý
```

Dữ Liệu Khoa Học
Các hằng số vật lý và thông số kỹ thuật được trích từ tài liệu công khai của NASA; những tham số nhóm tự ước tính để cân bằng gameplay đều được gắn nhãn rõ ràng.
| Tệp dữ liệu | Nội dung |
|---|---|
| src/data/nasa/rescue_mission.json | Ngân sách \Delta v 4 chặng (3.570 / 5.594 / 2.080 / 1.000 m/s), thời gian bay 258,9 ngày, chu kỳ giao hội 779,9 ngày, bảng độ trễ tín hiệu |
| src/data/nasa/rescue_modules.json | 12 module tàu vũ trụ và 3 cấp động cơ đẩy (I_{sp} = 320 / 450 / 900\text{ s}) |
| src/data/nasa/crew_roles.json | Hồ sơ 3 vai trò chuyên môn và các xung đột lợi ích cốt lõi |
| src/data/nasa/mars_comms_protocol.json | Ngân sách điện năng, độ đục bụi khí quyển (Mars 2020 MEDA), cửa sổ vệ tinh MRO, 6 gói telemetry, 3 trạm DSN cách nhau 120^\circ kinh độ |
| src/data/events/role_negotiations.json | 16 sự kiện trong chuyến bay và 48 phương án xử lý |
Xem chi tiết nguồn tham khảo tại docs/11-NASA-RESOURCES.md và docs/13-COMMS-SCIENCE.md.
Cài Đặt & Chạy Thử
Dự án viết bằng HTML5, CSS3 và JavaScript thuần (ES6+), không cần bước build.
Chạy trên máy cục bộ
Vì game tải dữ liệu JSON qua fetch(), bạn cần mở qua HTTP server thay vì mở trực tiếp file HTML:
cd src
python -m http.server 8311

Truy cập http://localhost:8311 trên trình duyệt.
Chạy kiểm thử tự động
Chạy từ thư mục gốc của repo (cần cài sẵn Node.js):
node scripts/test_nasa_data.mjs
node scripts/test_negotiation.mjs
node scripts/test_mission_viz.mjs
node scripts/smoke_engine.mjs

Phác Thảo Phân Cảnh Gốc
7 trang storyboard vẽ tay của Trần Minh Ngọc — bản phác thảo ý tưởng ban đầu cho 12 khung truyện tranh mở màn, nhịp kể chuyện và cơ chế đồng thuận khi đàm phán.
Xem tại docs/storyboard-sketches-minhngoc/ (có kèm README giải thích từng trang).
Nhóm Phát Triển
| Thành viên | Đóng góp |
|---|---|
| Trần Minh Ngọc (Trưởng dự án) | Ý tưởng gốc, vẽ storyboard, thiết kế UI/UX và hệ thống gameplay (luồng chơi, cân bằng tài nguyên, cơ chế đánh đổi và module tàu). |
| Nguyễn Thành Thiện Nhân | Lập trình game engine & tích hợp dữ liệu vật lý, điều phối quy trình phát triển cùng AI agents và kiểm thử toàn bộ luồng chơi. |
Bản Quyền & Ghi Công
 * Mã nguồn: Giấy phép MIT License.
 * Tư liệu hình ảnh & dữ liệu: Video mở đầu từ Wikimedia Commons (CC0 1.0); ảnh bề mặt Sao Hỏa và dữ liệu quỹ đạo thuộc phạm vi công cộng (Public Domain) của NASA và USGS.
 * Nhận diện thương hiệu: Tên gọi, biểu trưng và đồ họa của ABANDONN do nhóm tự thiết kế; logo NASA chỉ dùng trong phần ghi công theo đúng quy định sử dụng tài nguyên truyền thông của NASA.
Sản phẩm tham dự NASA Space Apps Challenge 2026.

