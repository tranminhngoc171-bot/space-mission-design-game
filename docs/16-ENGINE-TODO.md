# Việc cần làm cho engine: nối vào game, và bổ sung ba tài nguyên

Ghi ngày 15/11/2026. Người viết: Thiện Nhân (bên giao diện).

File này nói rõ engine hiện có gì, game đang thiếu gì, và phần nào Ngọc cần làm để
engine thật sự được tính điểm. Đọc hết trước khi sửa dòng nào.

---

## 1. Tình trạng thật, kiểm bằng máy

Tôi đã grep toàn repo. Kết quả:

```
grep -rn "computeMission" src/*.js | grep -v "^src/engine.js"
→ không có kết quả
```

Nghĩa là `engine.js` 400 dòng của Ngọc **chưa được gọi ở bất kỳ đâu**. Đây là code
chết trên bản deploy. Người chơi bay xong 258,9 ngày thì màn `flight.js` gọi
`onDone({success})`, `index.html` ghi localStorage, và **không hiện gì thêm**. Không
điểm, không báo cáo, không giải thích vì sao thắng hay thua.

Đây là lỗ hổng nghiêm trọng nhất so với đề bài, vì đề ghi rõ:

> Mission simulation + evaluation system with feedback on **why** it succeeded/failed

Và trong phần ưu tiên của chúng ta, **Post-mission analysis** được xếp hạng 4 với ghi
chú "mentioned 3× in the brief". Đây là thứ được chấm cao nhất ở tiêu chí Impact.

---

## 2. Sửa lại điều tôi nói sai lúc trước

Lúc đầu tôi nói game thiếu ba trong sáu tài nguyên là Data, Comms, Time. **Điều đó
đúng với phần giao diện, nhưng sai với engine.**

Engine của Ngọc đã tính **đủ bảy** chỉ số:

| Chỉ số trong `resources` | Đơn vị | Ngưỡng |
|---|---|---|
| `mass` | kg | <= sức chở tên lửa |
| `power` | W | <= công suất phát sau sự kiện |
| `battery` | Wh | >= nhu cầu cho phút tối |
| `budget` | triệu USD | <= ngân sách kịch bản |
| **`data`** | GB/ngày | >= 90 phần trăm gửi được |
| **`comms`** | phần trăm quỹ đạo | >= 40 phần trăm cửa sổ |
| **`time`** | năm | <= tuổi thọ sau suy giảm |

Vậy phần khó nhất đã xong. Việc còn lại là **nối nó vào giao diện và vào màn chơi**,
không phải viết lại công thức.

---

## 3. Vấn đề lớn thứ hai: hai bên dùng cấu trúc dữ liệu khác nhau

Đây là chỗ sẽ làm hỏng việc nối nếu không xử lý trước.

### Engine mong đợi

```js
computeMission(design, scenarioId)
→ design = {
    instruments: [...],   // mảng id thiết bị
    bus: 'id',
    power: 'id',
    battery: 'id',
    orbit: 'id',
    launcher: 'id',
    duration_months: 36,
  }
```

Lấy từ `data/instruments.json`, `data/orbits.json`, `data/launch_vehicles.json`.

### Màn thiết kế tàu hiện trả về

```js
// src/rescue-designer.js, dòng 959
payload = {
  ...design,
  summary,
  deltaV_ms: 38xx,        // số thực tính được
  launcherId: 'sls_block1',
  crewCount: 3,
}
```

Nó dựng trên `src/data/nasa/rescue_modules.json`, mười hai module chia tám nhóm
(động cơ, điện, liên lạc, nhiên liệu, sinh hoạt, chắn bức xạ, hạ cánh, khoa học). Mỗi
module có `mass_kg`, `power_w`, `cost_musd`, `isp_s`, `tradeoff_vi/en`, `source`.

**Hai mô hình này không khớp nhau.** Không phải sai, chỉ là hai cách mô tả khác nhau
cùng một sứ mệnh. Cần một lớp chuyển đổi ở giữa.

---

## 4. Việc cần làm, theo thứ tự

### Việc 1, quan trọng nhất: hàm chuyển đổi

Viết trong `src/engine-adapter.js` (tạo mới), export:

```js
export function rescueDesignToMissionDesign(payload, scenarioId)
```

Nhiệm vụ: nhận `payload` từ `startRescueDesigner`, trả về object đúng hình dạng
`computeMission` cần. Cách ánh xạ:

| Từ rescue payload | Sang design | Ghi chú |
|---|---|---|
| `modules` nhóm `propulsion` | `bus` | chọn bus theo khối lượng tổng |
| `modules` nhóm `power` | `power` | |
| `modules` nhóm `communications` | orbit comms | |
| `deltaV_ms` tính được | kiểm tra riêng, không có trong engine | thêm như `checks` mới |
| `deltaV_ms`, `crewCount: 3` | tạo `scenario` mới thay vì dùng ba kịch bản cũ | |

Nếu không ánh xạ được sạch, có phương án hai: **viết ba scenario mới vào
`data/scenarios.json` dành riêng cho sứ mệnh cứu hộ**, thay vì gắn vào astronomy.
Ba kịch bản cũ là `climate_watch`, `disaster_response`, `space_weather`, đều là vệ
tinh quan sát Trái Đất, không liên quan gì tới cứu người trên Sao Hỏa.

Tôi nghiêng về phương án hai. Lý do: đề bài là "Space Mission Design Game" nói chung,
nhưng game chúng ta đang làm là sứ mệnh cứu hộ. Gắn kịch bản quan sát khí hậu vào
màn cứu người sẽ ra báo cáo vô nghĩa.

### Việc 2: màn báo cáo hậu sứ mệnh

Ngọc dựng phần tính, tôi dựng giao diện. Cần `computeMission` trả thêm ba thứ mà đề
bài nhấn mạnh:

**a) Danh sách nguyên nhân thất bại, có thứ tự ưu tiên.** Engine đã trả `checks`
nhưng cần thêm trường `why_vi` / `why_en` cho mỗi check trượt, viết như người giải
thích chứ không như máy đọc mã lỗi.

Ví dụ sai (máy đọc):
```
mass_limit_exceeded
```

Ví dụ đúng (người giải thích):
```
Khối lượng 74.200 kg vượt sức chở 70.000 kg của SLS Block 1 khoảng 4.200 kg.
Bớt một thiết bị khoa học hoặc đổi sang tên lửa lớn hơn.
```

**b) Điểm bốn thành phần kèm trọng số, giải thích điểm nào mất vì đâu.** Engine đã có
`score.total`, `mission_success`, `science_value`, `resource_efficiency`. Cần thêm
`breakdown` dạng mảng, mỗi phần tử có `name_vi/en`, `points`, `max`, `reason_vi/en`.

**c) Truy vết từng quyết định.** Đây là phần có giá trị giáo dục cao nhất. Cần trả về
mảng các quyết định trong suốt ván, mỗi cái ghi: người chơi chọn gì, mất gì, được gì,
và hệ quả về sau. Ví dụ:

```
Chọn động cơ Isp 320 thay vì 900
  Mất: phải mang 83 phần trăm khối lượng là nhiên liệu
  Được: tiết kiệm 120 triệu USD
  Hệ quả: phải bỏ gói khoa học để đủ tải trọng, mất 18 điểm khoa học
```

Phần này cần dữ liệu từ cả ba màn: chọn module ở `rescue-designer`, chọn phương án
đàm phán ở `flight`, và kết quả tính ở `engine`. Đề nghị Ngọc định nghĩa một mảng
`decisions[]` mà cả ba nơi cùng ghi vào, rồi engine đọc mảng đó khi chấm.

### Việc 3: thêm ba thanh vào giao diện thiết kế

Đây là việc của tôi, nhưng cần Ngọc xác nhận công thức trước khi tôi dựng.

Ba thanh hiện có: ngân sách, tải trọng, delta-v. Cần thêm:

**Thanh Data.** Lượng dữ liệu sinh ra mỗi ngày so với băng thông tải về. Với sứ mệnh
cứu hộ thì dữ liệu là telemetry sinh hiệu của ba phi hành gia cộng dữ liệu khoa học.
Cần công thức: bao nhiêu GB/ngày, băng thông bao nhiêu GB/ngày.

Dữ liệu đã có trong `src/data/nasa/mars_comms_protocol.json`: `telemetry_packets` sáu
gói tổng 16 byte, `mro_satellite.data_rate_kbps`. Nhưng đơn vị byte của một gói tin cứu
hộ khác hẳn GB/ngày của engine. Cần Ngọc chốt cách quy đổi.

**Thanh Comms.** Phần trăm thời gian trong quỹ đạo có cửa sổ liên lạc được với Trái
Đất. Với sứ mệnh Sao Hỏa thì đây là bài toán trễ 3 tới 22 phút, và ba trạm DSN có
khoảng trống khi Sao Hỏa ở phía đối diện. Đã có bảng trễ trong
`src/data/nasa/rescue_mission.json` trường `signal_delay_table`, ba mốc 3,0 và 12,5 và
22,3 phút.

**Thanh Time.** Ngân sách thời gian. Với sứ mệnh cứu hộ thì đây là cửa sổ phóng: chu
kỳ giao hội 779,9 ngày, bay 258,9 ngày. Nếu bỏ lỡ cửa sổ thì phải chờ hai năm, và
người trên Sao Hỏa không sống được hai năm với lượng nhu yếu phẩm hiện có. Đây là
ràng buộc mạnh nhất và cũng kịch tính nhất, nên đáng làm thành thanh riêng.

### Việc 4: sự kiện ngẫu nhiên trong lúc bay

Engine đã có `data/events.json` và `computeMission` trả `events` đã bắn. Nhưng màn bay
hiện chỉ dùng mười sáu sự kiện đàm phán của tôi
(`src/data/events/role_negotiations.json`), không dùng sự kiện kỹ thuật của Ngọc.

Đề nghị: giữ đàm phán là trục chính vì đó là phần "competing priorities" của đề, nhưng
cho sự kiện kỹ thuật bắn xen vào giữa các mốc đàm phán. Ví dụ đang bay thì pin tụt,
hoặc cảm biến hỏng. Ngọc định nghĩa `trigger_day` cho từng sự kiện để tôi chèn vào
đúng chỗ trên bản đồ quỹ đạo.

---

## 5. Những gì tôi làm, Ngọc không cần đụng

Để tránh giẫm chân theo `docs/14-AGENT-RULES.md`:

Tôi giữ: `prologue.js`, `story.js`, `base.js`, `comms.js`, `rescue-designer.js`,
`flight.js`, `save-game.js`, `i18n.js`, toàn bộ `css/`, toàn bộ `assets/`.

Ngọc giữ: `engine.js`, `scoring.js` (nếu có), `data.generated.js`, `data/*.json`,
`src/data/nasa/*.json`, `scripts/build_data.py`, `scripts/smoke_engine.mjs`.

Tôi sẽ tạo `src/report.js` và `src/css/report.css` cho màn báo cáo. Ngọc chỉ cần đảm
bảo `computeMission` trả đủ dữ liệu như mục 4 việc 2, tôi lo phần vẽ.

---

## 6. Nếu chỉ kịp làm một việc

Làm việc 1 và việc 2a. Cụ thể:

1. Hàm chuyển đổi để `computeMission` chạy được với dữ liệu từ màn thiết kế tàu.
2. Trường `why_vi` và `why_en` cho từng check trượt.

Có hai thứ đó là đã có báo cáo hậu sứ mệnh có ý nghĩa, và đó là phần được chấm cao
nhất trong đề. Ba thanh Data, Comms, Time và truy vết quyết định làm sau vẫn kịp.
