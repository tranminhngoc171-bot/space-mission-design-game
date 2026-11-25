# Quy tắc cho agent của cả hai bên

File này là ràng buộc kỹ thuật, không phải lời khuyên. Mọi agent đọc trước khi
viết dòng code đầu tiên. Cập nhật lần cuối: 15/11/2026.

Lý do có file này: hai người dùng hai agent khác nhau cùng đẩy vào một repo. Mỗi
agent đều tự tin mình làm đúng, và cả hai cùng sửa một file thì git sẽ không cứu
được ai. Những luật dưới đây chia vùng để hai bên không bao giờ giẫm chân nhau.

---

## 1. Vùng sở hữu file, cấm vượt ranh

Đây là luật cứng. Không có ngoại lệ, không có "chỉ sửa một dòng cho nhanh".

### Ngọc và agent của Ngọc được sửa

```
src/engine.js
src/scoring.js
src/data.generated.js
src/css/mission.css
data/*.json
src/data/nasa/*.json
scripts/build_data.py
scripts/smoke_engine.mjs
scripts/validate_data.py
docs/00-CHALLENGE-BRIEF.md
docs/01-GAME-DESIGN.md
docs/02-BALANCE-DATA.md
docs/03-SCORING.md
docs/logs/decisions.md
docs/logs/devlog.md
```

### Thiện Nhân và agent của Thiện Nhân giữ

```
src/index.html
src/story.js
src/story-data.js
src/story-fx.js
src/art.js
src/base.js
src/base-flavor.js
src/hud.js
src/clock-ui.js
src/game-time.js
src/hab-stats.js
src/farm.js
src/explore.js
src/craft.js
src/radio.js
src/comms.js
src/memories.js
src/settings.js
src/settings-ui.js
src/audio.js
src/audio-sfx.js
src/fullscreen.js
src/intro-video.js
src/mission-viz.js
src/css/tokens.css
src/css/boot.css
src/css/story.css
src/css/base.css
src/css/hud.css
src/css/clock.css
src/css/farm.css
src/css/explore.css
src/css/craft.css
src/css/radio.css
src/css/comms.css
src/css/settings.css
src/css/fx.css
src/assets/**
scripts/gen-assets.py
scripts/process-assets.py
scripts/gen-icon-sprite.py
```

### Dùng chung, sửa được nhưng phải báo trước

```
src/i18n.js          chỉ thêm khối key có tiền tố riêng, không sửa key người khác
src/data.js          bảng nạp dữ liệu, sửa được nếu thêm dataset mới
README.md
package.json
docs/11-NASA-RESOURCES.md
```

Muốn sửa file trong vùng của bên kia thì mở issue hoặc nhắn trước, không tự sửa.

### Ranh giới hợp đồng dữ liệu

`computeMission(design, scenarioId, opts)` trong `engine.js` là hợp đồng giữa hai
bên. Bên giao diện gọi hàm này, bên engine cài đặt nó. Đổi chữ ký hàm hoặc đổi
cấu trúc object trả về là phá vỡ bên kia, phải thông báo trước một vòng.

---

## 2. Quy trình git

1. `git pull origin main` trước khi bắt đầu bất cứ việc gì. Không làm việc trên
   bản clone cũ ba tiếng.
2. Không đẩy thẳng vào `main`. `main` luôn phải chạy được.
3. Tạo nhánh riêng, đặt tên theo loại việc:
   - `feat/<việc>` cho tính năng mới
   - `fix/<việc>` cho sửa lỗi
   - `docs/<việc>` cho tài liệu
   - `data/<việc>` cho số liệu cân bằng
4. Một nhánh chỉ làm một việc. Đừng gộp ba tính năng vào một PR, vì bên kia
   không review nổi và dễ merge nhầm phần chưa xong.
5. Commit theo dạng `type: mô tả ngắn`, type gồm `feat`, `fix`, `docs`, `data`,
   `chore`, `art`.
6. Mở PR vào `main`, ghi rõ trong mô tả đã test cái gì và bằng cách nào.
7. Kết thúc phiên phải push nhánh, kể cả khi chưa xong. Ghi WIP ở đầu tên PR.

### Trước khi mở PR, tự kiểm tra

```bash
node --check <mọi file .js vừa sửa>
git diff --stat origin/main...HEAD    # xem mình có sửa file ngoài vùng không
```

Nếu `git diff` cho thấy file nằm trong vùng của bên kia, dừng lại và gỡ ra.

---

## 3. Luật đường dẫn, sai là chết toàn bộ tài nguyên

Đây là lỗi đã xảy ra thật và làm hỏng cả âm thanh lẫn ảnh trên bản deploy, trong
khi máy local vẫn chạy bình thường nên không ai phát hiện.

### Luôn dùng

```js
const BASE = new URL('.', import.meta.url).href;
const url = BASE + 'assets/audio/sfx/wind-far.mp3';
```

### Cấm dùng

```js
new URL('.', location.href).href   // SAI
'assets/mars-surface.jpg'          // SAI, đường dẫn tương đối trần
fetch('data/instruments.json')     // SAI
```

### Vì sao

Trang deploy ở `https://bersious.io.vn/nasa` không có dấu gạch chéo cuối. Kiểm
chứng bằng node:

```
new URL('.', 'https://site/nasa')   ->  https://site/          SAI, mất /nasa/
new URL('.', 'https://site/nasa/')  ->  https://site/nasa/     đúng
```

`import.meta.url` là URL của chính file module nên luôn trỏ đúng thư mục chứa nó,
bất kể trang đang ở đâu và có dấu chéo cuối hay không.

Luật này áp dụng cho mọi thứ nạp từ đĩa: ảnh, âm thanh, file JSON, video, font.

---

## 4. Nội dung hiển thị

- Không dùng dấu gạch dài (em dash) trong bất kỳ chuỗi nào người chơi đọc. Đó là
  dấu hiệu nhận biết văn bản do AI viết nhanh nhất và người dùng cấm tuyệt đối.
  Thay bằng phẩy, hai chấm, hoặc tách thành hai câu.
- Mọi chuỗi hiển thị phải song ngữ Việt và Anh. Thiếu một bên là lỗi, không phải
  việc để sau. Thêm key vào `src/i18n.js` trong `STRINGS.vi` và `STRINGS.en`.
- Số liệu lấy từ NASA phải ghi nguồn. Số do nhóm tự đặt để cân bằng gameplay phải
  ghi rõ là ước tính, không được gán bừa cho NASA.

---

## 5. Không được làm hỏng

- `node --check` phải qua với mọi file JS.
- Không lỗi console trên trang khi chạy thật.
- Hit target của mọi nút ít nhất 44px. Chữ phải đạt tương phản AA.
- Tôn trọng `prefers-reduced-motion` và trường `motion` trong `localStorage`
  `smdg.settings`. Tắt chuyển động thì không có animation nhưng vẫn dùng được.
- Không tràn ngang ở 360px, 390px, 1024px, 1440px.

### Bẫy khi test âm thanh

Trình duyệt chỉ cho phát âm thanh sau cú bấm thật của người dùng. Gọi
`element.click()` trong JS **không** mở khoá âm thanh, nên test sẽ báo im lặng
dù code đúng. Phải dùng CDP:

```js
Input.dispatchMouseEvent({ type: 'mousePressed', x, y, button: 'left', clickCount: 1 })
Input.dispatchMouseEvent({ type: 'mouseReleased', x, y, button: 'left', clickCount: 1 })
```

Kiểm tra bằng `isAudioUnlocked()` trong `src/audio.js`: trước khi bấm là `false`,
sau khi bấm thật phải là `true`.

---

## 6. Deploy

Không ai đẩy tay lên `bersious-web`. Có workflow tự động ở repo đó, kéo `main` của
repo này sang thư mục `nasa/` rồi commit, Vercel thấy commit là deploy. Chạy mỗi
15 phút, hoặc bấm tay ở tab Actions của `bersious/bersious-web`.

Nghĩa là: merge vào `main` thì sau tối đa 15 phút web có. Không merge thì web
không có. Không có đường tắt nào khác.

Workflow có chặn an toàn: nếu `main` thiếu `src/index.html` hoặc có ít hơn 5 file
JS thì nó dừng và không ghi đè bản đang chạy tốt.

---

## 7. Việc cần làm ngay khi nhận file này

Agent của Ngọc, làm theo thứ tự:

1. `git fetch origin && git log origin/main --oneline -10` để thấy `main` đã đi
   tới đâu. Nhánh `feat/engine-core` của bạn đã lạc hậu so với `main`.
2. PR #6 đang mở và có 13 file. Trong đó `src/engine.js`, `src/data.generated.js`,
   `scripts/build_data.py`, `docs/08-RESEARCH-SOURCES.md` đã được lấy vào `main`,
   không cần gửi lại.
3. Phần **chưa** vào `main` và vẫn cần: `src/css/mission.css`,
   `scripts/smoke_engine.mjs`, `docs/logs/*`. Tạo nhánh mới từ `main` hiện tại,
   chỉ đặt ba thứ đó vào, mở PR mới.
4. **Bỏ `src/ui.js` và `src/index.html` khỏi PR.** Giao diện do bên Thiện Nhân
   giữ, và `index.html` trên `main` hiện đã có luồng chạy đầy đủ: màn khởi động,
   video intro, 40 lượt kể chuyện, rồi màn căn cứ. Đưa `index.html` của bạn vào
   là ghi đè toàn bộ phần đó.
5. Đóng PR #6 kèm ghi chú đã tách phần cần giữ sang PR mới.
6. Từ đó về sau bám đúng mục 1 của file này.

Bên Thiện Nhân, kiểm tra lại sau mỗi lần người kia mở PR:

```bash
gh pr view <số> --json files --jq '.files[].path'
```

Nếu thấy file ngoài vùng của họ, yêu cầu tách trước khi merge.
