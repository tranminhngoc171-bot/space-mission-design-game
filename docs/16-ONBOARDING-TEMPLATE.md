# 16 · Khuôn mẫu hướng dẫn người chơi

Mỗi lần nhóm thêm một tính năng mới, người chơi cần biết bấm vào đâu và vì sao nó quan trọng. Hệ thống này gom toàn bộ nội dung hướng dẫn vào **một file JSON**, nên thêm hướng dẫn không phải sờ vào code giao diện.

Bốn file của hệ thống:

| File | Việc của nó |
| --- | --- |
| `src/data/onboarding_tutorials.json` | Toàn bộ nội dung 8 thẻ, song ngữ VI + EN |
| `src/onboarding.js` | `showTutorial`, `maybeShow`, `resetTutorials`, `openHandbook` |
| `src/css/onboarding.css` | Thẻ, lớp spotlight, sổ tay |
| `docs/16-ONBOARDING-TEMPLATE.md` | File bạn đang đọc |

---

## Ba bước thêm một thẻ hướng dẫn

### Bước 1 · Thêm một phần tử vào JSON

Mở `src/data/onboarding_tutorials.json`, chèn một phần tử mới vào mảng `tutorials`. Bốn khối nội dung bắt buộc phải có cả tiếng Việt và tiếng Anh.

- `id`: mã duy nhất, không dấu, dùng gạch dưới. Đây là khoá lưu trạng thái đã xem, nên **đổi id là thẻ hiện lại từ đầu**.
- `phase`: `1` hoặc `2`. Sổ tay chia hai nhóm theo trường này.
- `order`: số thứ tự hiện trong sổ tay và dòng "Thẻ n trên m".
- `trigger.type`:
  - `firstEnter` · hiện lần đầu vào một màn. Kèm `trigger.screen`, khớp với mã màn truyền vào `maybeShow`.
  - `firstOpenPanel` · hiện lần đầu mở một panel. Kèm `trigger.panel`. Có thể khai nhiều mã cách nhau dấu phẩy khi một thẻ dùng chung cho nhiều nút.
  - `manual` · **không tự hiện**, chỉ hiện khi bấm trong sổ tay.
- `spotlight`:
  - `"all"` · làm tối cả màn hình, thẻ nằm giữa.
  - Mảng selector CSS · khoanh sáng đúng vùng đó, phần còn lại tối. Ví dụ `[".bs-hot[data-id='comms']"]`. Khai nhiều selector thì vùng sáng là hình chữ nhật bao trọn tất cả.
- `action`, `nasaFact`, `survivalTip`, `button` · bốn khối nội dung, mỗi khối một cặp `vi` / `en`.

### Bước 2 · Gọi `maybeShow` ở chỗ mở tính năng

```js
import { maybeShow } from './onboarding.js';

// Panel: đặt ngay đầu hàm mở panel, trước khi dựng giao diện.
maybeShow({ trigger: 'firstOpenPanel', panel: 'comms' });

// Màn: đặt sau khi màn đã dựng xong DOM.
maybeShow({ trigger: 'firstEnter', screen: 'assembly' });
```

`maybeShow` **không chặn** hàm mở panel: nó trả về ngay một Promise, giao diện vẫn dựng bình thường. Thẻ đã xem thì không hiện lại lần nào nữa.

### Bước 3 · Test lại

```js
// Trong Console của trình duyệt
window.__devOnboarding.resetTutorials();
location.reload();
```

Hoặc gọi thẳng một thẻ bất kỳ:

```js
const { showTutorial } = await import('./src/onboarding.js');
showTutorial({ id: 'comms_mro' });
```

---

## Mẫu JSON đầy đủ để copy

```json
{
  "id": "farm_water",
  "phase": 1,
  "trigger": { "type": "firstOpenPanel", "panel": "farm" },
  "spotlight": [".bs-hot[data-id='lifesupport']"],
  "order": 9,
  "title": {
    "vi": "Tưới nước cho khay khoai tây",
    "en": "Water your potato trays"
  },
  "action": {
    "vi": "Bấm vào khay để chọn, rồi bấm Tưới. Mỗi lần tưới tốn nước uống của bạn.",
    "en": "Click a tray to select it, then hit Water. Every watering costs you drinking water."
  },
  "nasaFact": {
    "vi": "NASA đã trồng khoai tây trong môi trường mô phỏng đất Sao Hỏa ở Peru để thử nghiệm.",
    "en": "NASA grew potatoes in simulated Martian soil in Peru to test the idea."
  },
  "survivalTip": {
    "vi": "Đừng tưới cả ba khay cùng lúc, bạn sẽ chết khát trước khi khoai kịp mọc.",
    "en": "Don't water all three trays at once, you'll die of thirst before the potatoes sprout."
  },
  "button": {
    "vi": "Hiểu rồi, tưới thôi!",
    "en": "Got it, let's water!"
  }
}
```

---

## Quy ước viết nội dung

- **Không dấu gạch dài** trong chuỗi hiển thị. Dùng dấu phẩy hoặc chấm chia câu.
- Số phần trăm viết thành chữ: `80 phần trăm` thay vì `80%`, để trình đọc màn hình đọc đúng.
- Khối `action` là phần chính, chữ to nhất. Viết như hướng dẫn viên đang đứng cạnh người chơi, không viết như tài liệu kỹ thuật.
- Khối `nasaFact` là móc nối với kiến thức thật. Đây là phần khiến game có giá trị giáo dục, đừng bỏ trống.
- Khối `survivalTip` là cảnh báo cụ thể, có hậu quả rõ ràng nếu người chơi làm sai.
- `button` là câu xác nhận ngắn, dưới 40 ký tự.

---

## Sổ tay và spotlight

Sổ tay mở từ nút `[?]` trên HUD (`hud-compact.js`) và liệt kê **tất cả** thẻ trong JSON, kể cả thẻ chưa từng hiện. Thẻ đã xem có nhãn mờ, thẻ chưa xem có nhãn hổ phách. Bấm một thẻ thì mở ở chế độ chỉ đọc, đóng thì quay lại đúng vị trí cũ.

Spotlight dựng bằng **bốn lớp tối** bao quanh vùng sáng thay vì một lớp có lỗ khoét. Cách này không cần `clip-path` nên chạy đúng trên mọi trình duyệt và không cắt mất phần tử đang khoanh. Vùng sáng chừa 12px quanh phần tử đích, có viền hổ phách.

Thẻ nội dung tự tránh vùng sáng: vùng sáng ở nửa trên thì thẻ xuống dưới, ngược lại thì thẻ lên trên. Trên màn hẹp (dưới 640px) thẻ bám sát cạnh còn lại theo chiều dọc và cuộn được bên trong.

---

## Giai đoạn 2: móc tạm

Phase 2 dựng giao diện trong các file `feature-*.js` mà đợt này **không được sửa**, nên không có chỗ gọi `maybeShow` trực tiếp. `registerPhase2Hooks()` bắc cầu bằng `MutationObserver`: nó theo dõi DOM, lần đầu thấy class đặc trưng của từng màn thì gọi `maybeShow` với mã màn tương ứng.

Cách này là **tạm**. Khi nào được phép sửa Phase 2 thì xoá hook, thay bằng lệnh gọi trực tiếp ở chỗ dựng xong giao diện của từng feature.

---

## Kiểm tra trước khi xong

- `node --check src/onboarding.js` phải qua.
- Mở Console, xoá `localStorage.smdg.tutorialsSeen`, tải lại: thẻ đầu tiên phải tự hiện.
- Bấm nút trong thẻ: `localStorage.getItem('smdg.tutorialsSeen')` phải có id vừa xem.
- Tải lại: thẻ đó **không** được hiện lại.
- Đổi ngôn ngữ VI sang EN: mọi chuỗi trong thẻ phải đổi hết.
- Thử 1440×900 và 390×844: thẻ không tràn, chữ không bị cắt.
- Bật "giảm chuyển động" (hoặc `html.motion-off`): thẻ hiện ngay, không mờ dần.
