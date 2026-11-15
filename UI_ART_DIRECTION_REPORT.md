# Báo cáo đợt cập nhật giao diện theo đặc tả Art Direction

Ngày 15/11/2026. Làm theo file đặc tả đồ hoạ, UI/UX, item và pipeline tự động hoá.

---

## 1. HUD: thanh chia 10 vạch thay thanh trơn

Viết lại `src/hud.js` và `src/css/hud.css`.

**Thanh chia 10 vạch.** Mỗi chỉ số là 10 ô, ô đã đầy thì tô màu và có quầng sáng nhẹ. Làm tròn lên để chỉ số còn sống mà thấp vẫn hiện ít nhất một vạch, nhìn là biết chưa chết hẳn.

**Icon riêng cho từng chỉ số.** Bảy icon vector nội tuyến vẽ theo nghĩa: tia sét cho Thể lực, dao nĩa và củ khoai cho Calo, giọt nước cho Nước, bóng đèn cho Tinh thần, pin cho Điện, hai vòng tròn cho Oxy, khiên có dấu tích cho Độ kín. Vẽ nội tuyến vì bảy icon nhỏ mà mỗi cái một request file thì phí, và vector vẫn nét ở mọi cỡ màn hình.

**Màu đúng bảng Art Direction**, không tự pha:

| Chỉ số | Mã màu |
|---|---|
| Thể lực | `#EAB308` |
| Calo | `#F97316` |
| Nước | `#0EA5E9` |
| Tinh thần | `#A855F7` |
| Điện | `#22C55E` |
| Oxy | `#38BDF8` |
| Độ kín | `#94A3B8` |

**Mũi tên sạc/xả.** Riêng chỉ số Điện có mũi tên ▲ khi đang tăng, ▼ khi đang hao, so với lần vẽ trước. Không đổi thì giữ nguyên mũi tên cũ để không nhấp nháy.

**Sọc cảnh báo dưới 25 phần trăm.** Cả ô chuyển viền đỏ, nền đỏ mờ, và thanh hiện sọc chéo công trường nhấp nháy chậm 1,5 giây một nhịp. Nhấp nháy chậm chứ không giật liên tục, để nhìn lâu không mỏi mắt.

**Khung nhóm vát góc.** Mỗi nhóm chỉ số nằm trong khung có góc trên phải vát, cho ra dáng thiết bị dã chiến thay vì ô chữ nhật phẳng.

---

## 2. Đồng hồ LCD dã chiến và ba nút tốc độ

Thêm hai file mới: `src/clock-ui.js` và `src/css/clock.css`.

**Màn hình LCD.** Hiện SOL và giờ cạnh nhau, font đơn cách, màu hổ phách `#F59E0B`, có quầng sáng như đèn huỳnh quang. Khung có lớp quét màn hình rất mờ, bốn ốc vít ở bốn góc, viền kép để trông có độ dày như tấm kim loại.

**Ô tròn xoay ngày/đêm.** Mặt trời ban ngày, mặt trăng ban đêm, xoay nửa vòng khi chuyển và đổi màu từ hổ phách sang xanh lạnh.

**Ba nút tốc độ** dưới khung: `1x`, `2x`, `⏩ Chờ nhanh`. Đã thêm vào `game-time.js`:

```js
const SPEEDS = [1, 2, 6];
```

Đo thật trên trình duyệt, mỗi 3 giây thực:

| Tốc độ | Phút game trôi được |
|---|---|
| 1x | 6 phút |
| 2x | 12 phút |
| 6x (chờ nhanh) | 36 phút |

Tỉ lệ đúng 1 : 2 : 6. Không cho nhanh hơn 6x vì chỉ số trôi theo thời gian, tua quá nhanh thì người chơi không kịp phản ứng khi có chỉ số tụt.

Mốc ngày/đêm cũng sửa lại theo GDD: từ 20:00 xuống **18:00**, đúng mốc 06:00–18:00 mà đặc tả đặt ra.

---

## 3. Xử lý ảnh: 128×128 có viền, đệm đều, kèm manifest

Cập nhật `scripts/process-assets.py`.

**Icon chuẩn 128×128** đúng đặc tả, thay vì 256 như trước. Viền tối 2px quanh mép, vẽ **sau** khi thu nhỏ nên nét luôn đúng 2px ở mọi ảnh gốc.

**Dò khung bao vật thể theo độ sáng.** Ảnh sinh ra có nền gradient tối, không phải nền trong suốt, nên `getbbox()` của Pillow không dùng được. Thay bằng: lấy mức sáng trung bình bốn góc làm mức nền, pixel sáng hơn ngưỡng là vật thể, cắt sát rồi canh giữa. Vật thể chỉ chiếm 82 phần trăm khung để đệm đều bốn phía.

Đo lại bằng script: **0 phần trăm pixel sáng trong 12px đầu mỗi cạnh**, vật thể hoàn toàn tách khỏi mép.

**`asset-manifest.json`** ghi từng file kèm đường dẫn, kích thước và dung lượng, để phía web không phải mò đường dẫn hay đoán ảnh nào đã xử lý.

Tổng dung lượng: 1750 KB xuống **939 KB**, giảm **47 phần trăm**.

---

## 4. Năm lỗi bố cục tìm ra và sửa

**1. Khung HUD rộng hơn màn hình 20px trên điện thoại.** `.hud-group` có `min-width: 100%` cộng padding mà thiếu `box-sizing: border-box`, nên trên màn 390px khung phình lên 410px và đẩy số cùng thanh chỉ số tràn ra mép phải. Đây là lỗi nặng nhất vì rơi đúng vào vùng người chơi liếc liên tục.

**2. Nút tốc độ thứ ba bị nút cài đặt đè.** Nút cài đặt là `position: fixed` ở góc phải trên, đè lên 80 phần trăm nút `⏩`. Sửa: chừa 66px padding phải cho topbar trên điện thoại, và ẩn nhãn pha ngày vì ô tròn trên đồng hồ đã nói ban ngày hay ban đêm rồi.

**3. Topbar cao 123px trên điện thoại** vì ba khối xếp ba hàng dọc. Sửa: cho tên phi hành gia, đồng hồ và nút thành một hàng ngang, topbar xuống còn **71px**.

**4. Số Điện lệch trục canh phải** vì mũi tên ▲ chiếm chỗ trong vùng canh phải. Sửa: cho `.hud-value` bề ngang cố định `2.1em` và mũi tên một chỗ riêng `0.7em`. Đo lại: cả 7 số giờ kết thúc đúng 373px, thẳng cột tuyệt đối.

**5. Tràn dọc 75px trên màn 390×844** vì HUD kiểu mới có padding khung và icon nên cao hơn bản cũ khoảng 26px mỗi nhóm. Sửa: bậc thang `max-height` cho ảnh cảnh theo chiều cao màn, từ 27dvh xuống 9dvh, màn rất thấp thì ẩn hẳn ảnh và nhật ký.

---

## 5. Kiểm thử

**13 trên 13 kích thước sạch**, đo cả ba thứ: tràn dọc, tràn ngang, và chữ bị cắt mép:

| Kích thước | Kết quả |
|---|---|
| 1920×1080 | sạch |
| 1440×900 | sạch |
| 1366×768 | sạch |
| 1280×600 | sạch |
| 1024×768 | sạch |
| 768×1024 | sạch |
| 428×926 | sạch |
| 414×896 | sạch |
| 412×915 | sạch |
| 390×844 | sạch |
| 375×667 | sạch |
| 360×800 | sạch |
| 2560×1080 | sạch |

**6 trên 6 nút mở đúng**: Nông trại, Túi đồ, Đi thám hiểm, Bàn chế tạo, Liên lạc, Đi ngủ.

**0 lỗi console**, **0 ảnh 404** trên toàn bộ luồng.

**Ba tốc độ đúng tỉ lệ** 1 : 2 : 6 khi đo bằng đồng hồ thật.

---

## 6. Những gì trong đặc tả chưa làm

**Ba ảnh mặt cắt ngang trạm Hab** (`hab_main_day`, `hab_main_night`, `hab_main_storm`) cùng góc máy với các điểm bấm trực tiếp vào đồ vật. Hiện màn căn cứ dùng **một ảnh nền đổi theo hành động** (5 ảnh: trạm, nhà kính, bàn chế tạo, radio, cửa khí), không phải một mặt cắt cố định có hotspot. Làm mặt cắt cần vẽ 3 ảnh cùng bố cục rồi đặt vùng bấm theo toạ độ, mất khoảng 2 tới 3 giờ, và đổi hẳn cách người chơi tương tác. Tớ để cậu quyết vì đây là thay đổi lớn về trải nghiệm, không phải chỉnh giao diện.

**Tách nền bằng `rembg`.** Đặc tả đề xuất thư viện này, nhưng nó cần tải model onnx khoảng 170 MB và chạy trên CPU mất vài giây mỗi ảnh. Với 12 icon nền tối đồng nhất, cách dò độ sáng ở trên cho kết quả sạch hơn và không thêm phụ thuộc. Nếu sau này cần tách nền ảnh phức tạp (nền có chi tiết, vật thể trong suốt) thì mới đáng dùng.

**Giao diện riêng cho từng modal theo mô tả chi tiết** (thùng Pelican cam đen cho túi đồ, bản vẽ blueprint xanh cho bàn chế tạo, dao động ký cho radio). Hiện bốn modal dùng chung một hệ khung tối, có ảnh riêng cho từng màn nhưng chưa có chất liệu riêng. Đây là việc trang trí, không ảnh hưởng chức năng, làm sau cũng được.
