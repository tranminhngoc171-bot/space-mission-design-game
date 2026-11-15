# phase2 — Giai đoạn 2: Earth Mission Control (NASA MDL / CML 1-4)

Thư mục này **hoàn toàn độc lập** với `src/` (Giai đoạn 1 trên Sao Hỏa). Không file
nào trong `phase2/` import, sửa hay phụ thuộc trực tiếp vào mã của Giai đoạn 1;
hai bên chỉ nói chuyện qua `window.CustomEvent` và
`window.MARS_RESCUE_SHARED_STATE`.

## Mở thử ngay

```bash
cd phase2
python -m http.server 5174
# http://localhost:5174/phase2-demo.html
```

Hoặc mở thẳng `phase2/phase2-demo.html` bằng trình duyệt (không cần build, không
cần fetch, không có asset ngoài).

Bảng thử nghiệm trên đầu trang có hai nút giả lập đúng hai sự kiện của Giai đoạn 1
để chạy độc lập.

## Bộ giả lập Giai đoạn 1 (tab SAO HỎA)

Trang demo có hai tab: **TAB TRÁI ĐẤT** (Giai đoạn 2) và **TAB SAO HỎA** (giả lập
Giai đoạn 1). Tab Sao Hỏa **không phải** game sinh tồn thật, nó chỉ phát đúng ba
sự kiện trong hợp đồng với dữ liệu do người test chỉnh:

| Điều khiển | Ảnh hưởng |
|---|---|
| Thanh trượt *Phi hành gia còn sống* (120-420 Sol) | `astronautSurvivalSols`, quyết định bài toán thời gian ở Hồi 1 |
| Thanh trượt *Sức khỏe vườn cây* | `cropHealthPercent` |
| Thanh trượt *Khoảng cách* (55-400 triệu km) | `earthMarsDistanceKm` → đổi độ trễ ánh sáng hiển thị |
| Công tắc *Bão bụi* | `dustStormActive`, bật thì pin mặt trời tụt biên độ và bị cảnh báo đỏ |
| Ba nút preset Dễ / Chuẩn / Khó | đặt nhanh bộ số, khỏi kéo từng thanh |

Luồng test đầy đủ:

1. Tab SAO HỎA, chọn preset, bấm **Gửi SOS về Trái Đất** → tự nhảy sang tab Trái Đất.
2. Hồi 1 → 2 → 3, chọn kiến trúc, bật hai công tắc, bấm **LAUNCH MISSION**.
3. Ở mốc 75%, tab SAO HỎA nhấp nháy và nút **EVA: cắm đèn hiệu** được mở khoá.
4. Bấm nút đó → `mars:beacon-deployed` → tàu hạ cánh, hiện tổng kết NASA analogue.

Nhật ký sự kiện ở cuối tab Sao Hỏa ghi lại từng `CustomEvent` kèm payload, nên
nhìn được đúng hợp đồng hai chiều đang chạy.

Preset **Dễ (320 Sol)** cho nhiều tổ hợp qua cổng CML 4 hơn; preset **Khó (200 Sol)**
gần như không có đường thắng, dùng để test nhánh thất bại.


## Các file

| File | Vai trò |
|---|---|
| `phase2-engine.js` | Bộ não cho sẵn (UMD). Không sửa. Mọi số liệu đi qua đây. |
| `phase2-i18n.js` | Chuỗi VI/EN của riêng phase 2 (`Phase2I18N.t`). |
| `bridge-adapter.js` | Cầu CustomEvent hai chiều + `Phase2Util` dựng DOM + shared state. |
| `feature-cml1-telemetry.js` | Hồi 1: telemetry Sao Hỏa, thanh sinh tồn, chọn mục tiêu KPP. |
| `feature-cml3-tradespace.js` | Hồi 2: bốn phân khu, bốn đồng hồ biên độ, cảnh báo xung đột pin/bão bụi. |
| `feature-cml4-checklist.js` | Hồi 3: bảng RYG, thẻ kiến thức, công tắc quy trình, khoá LAUNCH. |
| `feature-execution-viz.js` | Hồi 4-5: canvas quỹ đạo, sóng DSN, đèn hiệu, tổng kết NASA analogue. |
| `phase2-app.js` | Tạo `window.phase2Engine`, mount bốn feature, định tuyến hồi, bảng thử nghiệm. |
| `phase1-mock.js` | Giả lập Giai đoạn 1: thanh trượt dữ liệu, nút gửi SOS, nhiệm vụ EVA đèn hiệu, nhật ký sự kiện. |
| `phase2.css` | Toàn bộ style, biến trong `:root`. JS chỉ toggle class trạng thái. |

## Hợp đồng sự kiện với Giai đoạn 1

| Sự kiện | Chiều | Payload |
|---|---|---|
| `mars:sos-received` | 1 → 2 | `{ astronautSurvivalSols, cropHealthPercent, dustStormActive, earthMarsDistanceKm }` |
| `earth:dsn-command-sent` | 2 → 1 | `{ commandType: 'DEPLOY_LANDING_BEACON_AND_CLEAR_ZONE', lightTimeMinutes }` |
| `mars:beacon-deployed` | 1 → 2 | `{ cleared: true }` (giá trị khác cũng được) |
| `phase2:goto-mars` | 2 → 1 | không có, chỉ là tín hiệu yêu cầu chuyển tab |

Phát từ phía Giai đoạn 1:

```js
window.dispatchEvent(new CustomEvent('mars:sos-received', { detail: {
  astronautSurvivalSols: 250, cropHealthPercent: 75,
  dustStormActive: true, earthMarsDistanceKm: 215000000
} }));
```

Nghe phía Giai đoạn 1:

```js
window.addEventListener('earth:dsn-command-sent', (e) => {
  // mở nhiệm vụ EVA cắm đèn hiệu
  console.log(e.detail.commandType, e.detail.lightTimeMinutes);
});
window.addEventListener('phase2:goto-mars', () => { /* chuyển tab Sao Hỏa */ });
```

Giai đoạn 2 còn ghi lại trạng thái vào `window.MARS_RESCUE_SHARED_STATE.phase2`
(`execution`, `selection`, `compliance`, `canLaunch`, `mars`, `lastDsnCommand`)
để đổi tab giữa chừng không lệch nhịp.

## Nhúng vào game chính

Hai cách, cả hai đều không cần sửa engine:

1. **iframe**: `<iframe src="phase2/phase2-demo.html">`. Cách này cô lập CSS tuyệt
   đối, nhưng CustomEvent không xuyên qua iframe, phải `postMessage` thêm.
2. **Cùng trang**: copy các khối `<section data-step="…">` và `<aside>` trong
   `phase2-demo.html` vào màn hình mong muốn, thêm 8 thẻ `<script>` theo đúng thứ
   tự, và nạp `phase2.css`. Cách này giữ nguyên CustomEvent, đơn giản hơn.

Không đặt `id` trùng với Giai đoạn 1: mọi id của phase 2 đều có tiền tố `dev-`
hoặc nằm trong `data-phase2`/`data-step`, không dùng id chung.

## Kiểm thử

```bash
node scripts/test_phase2_lifecycle.mjs   # luồng engine: SOS -> CML 4 -> launch -> EDL
node scripts/test_phase2_dom.mjs         # mount 8 file trong shim DOM, kiểm tra render
```

Cả hai chạy bằng node, không cần trình duyệt. Test DOM dựng shim tối thiểu
(`createElement`, `querySelector`, `CustomEvent`, `requestAnimationFrame`) nên bắt
được lỗi runtime mà `node --check` bỏ qua.

## Ghi chú cân bằng (đo bằng máy, không phải cảm tính)

Với giới hạn sinh tồn 250 Sol mặc định, chỉ **2/64 tổ hợp** kiến trúc qua được
cổng CML 4. Đó là chủ ý của engine (trade space hẹp như thật), nhưng nếu muốn dễ
thở hơn cho demo thì tăng `astronautSurvivalSols` trong payload SOS: ở 300 Sol có
6/64 tổ hợp qua. Giai đoạn 1 quyết định con số này.
