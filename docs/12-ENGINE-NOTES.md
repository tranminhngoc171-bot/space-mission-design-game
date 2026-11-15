# Ghi chú kỹ thuật: engine sứ mệnh và việc còn thiếu

Ghi ngày 15/11/2026, trong lúc chờ kết quả nghiên cứu tài nguyên NASA.

---

## 1. Engine đã có, nằm ở branch `feat/engine-core` (PR #6)

File `src/engine.js` 400 dòng do Ngọc viết, chạy được, đúng hợp đồng trong `src/README.md`:

```js
computeMission(design, scenarioId, opts) -> {
  resources, checks, objectives, events, score, analysis
}
```

Kiểm tra bằng node, không qua trình duyệt:

- Nạp được 12 instruments, 3 bus, 5 launcher, 4 orbit, 3 scenario
- Một cấu hình hợp lệ ra `band: good, mission_success: 70`
- Một cấu hình sai ra `band: failed, mission_success: 0`, có chỉ rõ check nào trượt

Vậy engine không phải phần cần làm lại. Nó chỉ chưa được gộp vào nhánh chính và chưa nối vào giao diện của mình.

---

## 2. Lỗi thật trong engine, đã tìm ra và đã sửa thử

**Triệu chứng:** gọi `computeMission` với design không có trường `duration_months` thì:

```
score.total = null
score.resource_efficiency = null
resources.budget.value = null   detail: "ops NaNM cho NaN năm"
resources.time.value = null
```

**Nguyên nhân:** dòng 105 của `engine.js`:

```js
const years = design.duration_months / 12;
```

Hàm đọc thời lượng từ `design`, nhưng thời lượng là thuộc tính của **scenario** chứ không phải của bản thiết kế. Chỉ hàm `emptyDesign()` mới copy trường đó sang design, nên ai gọi thẳng `computeMission` với design tự dựng sẽ dính lỗi. Người chơi thật sẽ gặp ngay nếu giao diện dựng design từ form mà quên trường này.

**Cách sửa:** lấy từ scenario, chỉ dùng của design khi design có giá trị hợp lệ:

```js
const durationMonths = Number.isFinite(design.duration_months) && design.duration_months > 0
  ? design.duration_months
  : scenario.duration_months;
const years = durationMonths / 12;
```

Sau khi sửa, cùng cấu hình đó ra `total: 55, resource_efficiency: 47, band: marginal`. Điểm tính đúng.

**Việc cần làm:** đưa bản sửa này vào branch `feat/engine-core` rồi mới mở PR, hoặc báo Ngọc sửa bên đó để không xung đột. Tớ chưa commit vì file chưa nằm trên nhánh đang làm.

---

## 3. Kết quả thử cân bằng sơ bộ

Bốn cấu hình cho scenario `climate_watch`, seed 42:

| Cấu hình | Điểm | Band | Check trượt |
|---|---|---|---|
| bus_small, solar_medium, bat_small, LEO 400, rideshare, cam_hires + spec_tir | 53 | marginal | không |
| bus_medium, solar_medium, bat_small, LEO 550, rideshare, 4 thiết bị | 34 | failed | power |
| bus_medium, solar_large, bat_medium, LEO 550, rideshare, cam_stereo + spec_tir + radiometer | 60 | good | không |
| bus_small, solar_medium, bat_medium, LEO 550, rideshare, cam_hires + radiometer | 61 | good | không |

Cân bằng hợp lý: có cấu hình thắng rõ, có cấu hình chết vì thiếu điện, và cấu hình thắng không phải kiểu nhồi thật nhiều thiết bị. Đúng ý đồ đánh đổi của đề.

---

## 4. Phần đề bài yêu cầu mà chưa có

Đề đặt 85% trọng tâm vào **sứ mệnh giải cứu 3 phi hành gia**, gồm bốn thứ chưa tồn tại trong mã nguồn:

1. **Màn thiết kế tàu cứu hộ** nối vào engine đã có. Engine tính được nhưng chưa có giao diện nào gọi nó. Hiện `src/index.html` chỉ có luồng kể chuyện và màn căn cứ sinh tồn.
2. **Đàm phán 3 vai trò** (Commander, Flight Engineer, Comms & Resource Officer) với chỉ số đồng thuận nhóm. Chưa có file dữ liệu sự kiện nào.
3. **Mission Viz 2D** vẽ quỹ đạo Trái Đất tới Sao Hỏa, các mốc đốt động cơ TCM, thời gian trễ tín hiệu.
4. **Báo cáo hậu sứ mệnh** chấm điểm theo tỷ lệ cứu sống, hiệu suất tài nguyên, giá trị khoa học, mức phối hợp nhóm.

Ngoài ra màn Sao Hỏa hiện tại là game sinh tồn 35 Sol đầy đủ, trong khi đề muốn nó chỉ là **mở đầu ngắn 15%** để kích hoạt tín hiệu cầu cứu. Cần quyết định giữ nguyên bản đầy đủ hay rút ngắn, vì bản đầy đủ tốn nhiều thời gian người chơi hơn đề dự kiến.

---

## 5. Đang chờ

Sub-agent `sa-0-86a3aaa1` đang mở trang đề bài và bấm từng resource link để lấy dữ liệu NASA thật, ghi vào `docs/11-NASA-RESOURCES.md`. Khi có kết quả mới chia việc cho các sub-agent còn lại, để phần thiết kế tàu và quỹ đạo bám đúng số liệu nguồn thay vì số tự nghĩ.
