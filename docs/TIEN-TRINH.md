# TIẾN TRÌNH DỰ ÁN — lưu lúc tạm dừng

Cập nhật lần cuối: đêm 15/11/2026, trước khi tắt máy đi ngủ.
Đọc file này trước khi làm tiếp bất cứ việc gì.

---

## 1. Trạng thái tổng thể

Game đã chơi được từ đầu tới cuối trên bản live. Không còn lỗi chặn luồng nào đã biết.

**Bản live:** https://bersious.io.vn/nasa (không có dấu chéo cuối)
**Repo game:** `C:\Users\nguye\workspace\nasa-space-apps-2026\team-repo`, nhánh `feat/ui-scaffold`
**Repo deploy:** `C:\Users\nguye\bersious-web`

---

## 2. Hai cái bẫy phải nhớ, nếu quên là sập cả site

### Bẫy 1: `middleware.ts` làm cả website trả 500

File `~/bersious-web/middleware.ts` là script đếm lượt truy cập, nó gây
`MIDDLEWARE_INVOCATION_FAILED` trên mọi đường dẫn, không riêng trang game.
Tháng 10 đã đổi tên thành `middleware.ts.disabled`.

**Mỗi lần rebase hoặc reset repo bersious-web phải kiểm lại file này.**
Nếu thấy `middleware.ts` xuất hiện thì đổi tên ngay:

```bash
cd ~/bersious-web && ls middleware*
# nếu có middleware.ts thì:
git mv middleware.ts middleware.ts.disabled && git commit -m "fix: tắt middleware, nó làm site 500" && git push origin main
```

### Bẫy 2: workflow chỉ chép `src/`, không chép `phase2/`

Phase 2 nằm NGOÀI `src/` (thiết kế cũ) nhưng game nạp nó qua `../phase2`.
Workflow `sync-game.yml` đã được sửa để có bước rsync riêng cho `phase2/`.
Nếu ai sửa lại workflow, phải giữ bước đó, không thì cả Giai đoạn 2 trả 404.

### Bẫy 3: đường dẫn import của `phase2/` phải là `../`, KHÔNG phải `../src/`

Đây là bẫy đã làm sập Giai đoạn 2 hai lần, ngày 16/11. Đọc kỹ trước khi
sửa bất kỳ dòng import nào trong `phase2/`.

**Vì sao:** workflow `sync-game.yml` chép `_source/src/` vào **gốc** thư mục
`nasa/`, tức là trên bản deploy KHÔNG có thư mục `src/`. Trong khi đó
`phase2/` được chép thành `nasa/phase2/`. Nên từ trong `phase2/`:

| Viết | Trên deploy trỏ tới | Kết quả |
|---|---|---|
| `../i18n.js` | `/nasa/i18n.js` | **200 đúng** |
| `../src/i18n.js` | `/nasa/src/i18n.js` | **404, sập bước 1-3** |

**Nhưng ở máy local thì ngược lại** (repo có `src/` thật, serve ở
`team-repo` root thì `../i18n.js` = `/i18n.js` = 404). Đây chính là lý do
lỗi này tái đi tái lại: sửa cho một môi trường thì hỏng môi trường kia.

**Luật:** `phase2/` LUÔN dùng đường dẫn phẳng `../` — vì đó là hình dạng
của bản deploy mới là thứ được chấm. Muốn test local mà đúng thì phải mô
phỏng cấu trúc phẳng:

```bash
# Dựng bản mô phỏng đúng như workflow rồi serve thư mục đó
python -c "
import os,shutil,fnmatch
b=r'C:/Users/nguye/workspace/nasa-space-apps-2026/team-repo'
s=r'C:/Users/nguye/AppData/Local/hermes/cache/scratch/nasa-flatsim'
shutil.rmtree(s,ignore_errors=True)
def cp(a,d):
    os.makedirs(d,exist_ok=True)
    for n in os.listdir(a):
        p=os.path.join(a,n)
        if os.path.isdir(p): cp(p,os.path.join(d,n))
        elif not any(fnmatch.fnmatch(n,g) for g in ['dev-*.js','__*-*']): shutil.copy2(p,os.path.join(d,n))
cp(b+'/src',s); cp(b+'/phase2',s+'/phase2')
"
cd "$s" && python -m http.server 8353
```

Kiểm bằng một lệnh là biết ngay:

```bash
cd team-repo && grep -rn '\.\./src/' phase2/*.js phase2/*.css \
  | grep -vE ':[0-9]+:[[:space:]]*(\*|/\*|-|//)'
# phải KHÔNG ra dòng code nào (comment thì được)
```

Hai commit đã sửa lỗi này: `d44a47e` (đổi `../src/` → `../`) và `77b7d89`
(hai chỗ còn sót). Ngày 17/11 nó tái phát lần ba với 25 dòng trong 18 file —
sửa lại về `../` và đã kiểm: 11 module Phase 2 nạp được, 8 file CSS
`@import` đều 200 trên bản mô phỏng deploy.

---



## 3. Quy trình deploy (làm đúng thứ tự này)

```bash
cd "C:/Users/nguye/workspace/nasa-space-apps-2026/team-repo"
git add -A && git commit -m "..."
git push origin feat/ui-scaffold
gh pr create --base main --head feat/ui-scaffold --title "..." --body "..."
gh pr merge --merge

cd ~/bersious-web
git fetch -q origin && git reset --hard origin/main -q   # quan trọng: reset để lấy bản mới
gh workflow run sync-game.yml
sleep 90
curl -s -o /dev/null -w "%{http_code}\n" "https://bersious.io.vn/nasa"
```

Lưu ý: `git pull --rebase` hay bị kẹt vì workflow bot commit liên tục.
Dùng `git fetch && git reset --hard origin/main` cho chắc.

---

## 4. Những gì đã xong

### Hạ tầng và luồng
- Màn chờ tải nhúng thẳng HTML đầu `<body>`, hiện trong 353ms, ba lớp tự gỡ độc lập
- Cổng chặn chuyển cảnh (`gate()` trong `preloader.js`), không che video mở đầu
- Menu mới: ảnh nền `menu-mars-hero.webp` (tàu + phi hành gia nằm trong tranh), tiêu đề căn giữa chuẩn 720/1440, ba nút kiểu HUD, tagline The Martian
- Bỏ hẳn sprite tàu SVG và ảnh nhân vật rời

### Giai đoạn 1
- Căn cứ point-and-click, 6 trạm, HUD nổi
- Nhật ký sứ mệnh 2 tab, checklist đọc trạng thái thật từ game
- Chuỗi quest xác tàu: ngày 6 nhớ ra, ngày 7-9 đào, sửa 3 món, rồi mới phát tín hiệu
- Nút Thiết kế tàu khoá cho tới khi phát tín hiệu xong
- 8 ảnh ending thua, màn ending có báo cáo NASA và ba nút

### Giai đoạn 2
- Đủ 4 bước: bắt sóng, lắp ráp, kiểm duyệt, bay và hạ cánh
- 6 đường chỉ dẫn trên thân tàu, modal linh kiện, modal quỹ đạo 3 phương án
- 4 đồng hồ đo, nút PHÓNG khoá theo 80% xanh
- Nút Hạ cánh ngay mở đường thua EDL
- `mountPhase2` tự nạp `phase2.css` (trước đây mở từ bảng dev là vỡ giao diện)

### Kết thúc
- 13 ảnh comic chuyển tiếp (đã bóc sạch logo NASA)
- True Ending 9 khung + bảng tổng kết xếp hạng S/A/B, đối chiếu Curiosity/Perseverance/MAVEN
- 8 ảnh True Ending đủ bộ

### Bảo hiểm
- `guide-escape.js`: gỡ mọi lớp phủ hướng dẫn còn sót, có nút trong bảng dev
- Thẻ hướng dẫn tự đóng sau 40 giây, Esc đóng được
- Bảng dev 40 mục, 6 nhóm

---

## 5. Việc còn lại khi chạy tiếp

### Ưu tiên 1: chạy lại 5 sub kiểm tra (đã bị dừng giữa chừng)

Năm sub đã chạy 48 phút và sửa được vài lỗi, rồi bị dừng để tắt máy.
Cần chia lại để kiểm tra nốt:

1. Màn chờ, menu, nút Bắt đầu phản hồi dưới 100ms
2. Comic 12 khung, story, lớp hướng dẫn
3. Căn cứ: 6 trạm, túi đồ, nông trại, đường thua
4. Phase 2: 4 bước, True Ending, đường thua
5. Rà soát bản live

Prompt mẫu cho sub 5 (rà soát live) ở mục 7 dưới.

### Ưu tiên 2: kiểm bằng mắt toàn bộ luồng

Chưa có lần nào chơi thông từ đầu tới cuối bằng tay trên bản live để
xác nhận không có màn nào trắng hay kẹt. Cần một lượt chơi thật.

### Ưu tiên 3: nộp bài

Theo thể lệ cần: mã công khai GitHub (đã có), tóm tắt 50-200 từ,
live demo (đã có), **video 30-60 giây** (chưa quay).

---

## 6. Lỗi đã biết nhưng chưa sửa

| Lỗi | Mức độ | Ghi chú |
|---|---|---|
| Khung 13 comic còn vài miếng vá trống trên ngực đám đông | Rất nhẹ | Không phải logo, không có ký tự nào |
| Khung 11 comic: giám đốc đập hai tay thay vì một | Rất nhẹ | Hết hạn ngạch sinh lại |
| Footer menu hơi nhỏ, tương phản thấp | Nhẹ | Vision gợi ý tăng lên 11-12px |
| Phase 2 có scrollbar trình duyệt lộ ở mép phải | Nhẹ | Cần custom scrollbar |
| Nút "TIẾP: LẬP TÀU" trong Phase 2 là chữ xám chứ không phải nút | Nhẹ | Ngược phân cấp với nút BƯỚC TRƯỚC |

---

## 7. Prompt mẫu cho sub rà soát live

```
Game web thuần HTML/CSS/JS. Bản live: https://bersious.io.vn/nasa
Repo: C:\Users\nguye\workspace\nasa-space-apps-2026\team-repo

Đây là sub kiểm tra cuối trước khi nộp bài thi. Mục tiêu là tìm mọi thứ
có thể làm giám khảo kết luận game bị hỏng.

Kiểm trên BẢN LIVE (không phải localhost) để chắc file đã deploy:
1. Tải trang lần đầu, không cache. Có khung trắng nào lọt ra không,
   màn chờ có hiện ngay không, console có 404 file nào không.
2. Bấm qua toàn bộ luồng: menu Bắt đầu, video, comic, story, căn cứ,
   sáu trạm, nhật ký, sổ tay, thiết kế tàu, kiểm duyệt, bay, kết thúc.
   Ghi rõ chỗ nào kẹt, chỗ nào trống.
3. Dùng curl kiểm từng file js và css mà index.html và các module import.
4. Kiểm 13 ảnh bg-im, 8 ảnh true-ending, 8 ảnh ending_ đều phải 200.
5. Responsive 1440x900, 1024x768, 390x844, không tràn ngang.
6. Đổi VI sang EN, đi qua vài màn, tìm chuỗi tiếng Việt còn sót.
7. Không có logo NASA trong ảnh, chỉ được HORIZON-IV hoặc MISSION CONTROL.

Nếu sửa lỗi thì deploy lại theo đúng thứ tự: push nhánh feat/ui-scaffold,
tạo PR, merge, rồi cd ~/bersious-web && git fetch && git reset --hard
origin/main && gh workflow run sync-game.yml.

TUYỆT ĐỐI không để file middleware.ts xuất hiện trong ~/bersious-web,
nó làm cả site trả 500.
```

---

## 8. Đường dẫn quan trọng

| Thứ gì | Ở đâu |
|---|---|
| Repo game | `~/workspace/nasa-space-apps-2026/team-repo` |
| Repo deploy | `~/bersious-web` |
| Workflow deploy | `~/bersious-web/.github/workflows/sync-game.yml` |
| Script sinh ảnh | `team-repo/scripts/gen-assets.py` |
| Script xử lý ảnh | `team-repo/scripts/process-assets.py` |
| Che watermark | `team-repo/scripts/wm-clean.py`, `wm-clean-im.py`, `wm-clean-menu.py` |
| Python có cv2 | `C:/Python314/python.exe` (python mặc định KHÔNG có cv2) |
| Server test | `cd team-repo/src && python -m http.server 8321` |
| Server Phase 2 | `cd team-repo && python -m http.server 8331` |
| Kịch bản truyện | `~/Desktop/NASA-Game-Kich-Ban.txt` |


---

## 9. Phát hiện từ đợt 5 sub bị dừng giữa chừng (ghi lại 16/11)

Năm sub chạy được khoảng 50 phút rồi bị dừng để tắt máy. Chúng chưa kịp
báo cáo đầy đủ nhưng trong log còn lại mấy phát hiện đáng giá. Đây là
danh sách để lần sau kiểm lại, KHÔNG phải đã sửa xong.

### Lỗi xác nhận được, cần kiểm và sửa

**1. Menu trên điện thoại có "hộp rỗng" (sub 1 phát hiện, đáng tin)**
`.menu-actions` có cả `top: 47%` lẫn `bottom: 16%`. Vì là flex column
định vị tuyệt đối nên nó bị kéo cao 312px trong khi nội dung chỉ 204px,
tạo một khoảng trống thừa dưới cụm nút trên màn hẹp. Sửa: bỏ một trong
hai thuộc tính (nên bỏ `top`, chỉ neo `bottom`).

**2. Story không có nút bỏ qua (sub 2 phát hiện)**
Yêu cầu là story phải có nút bỏ qua nhưng `story.js` không có. Giám khảo
phải ngồi đọc hết 20 lượt thoại mới vào được game. Cần thêm nút Bỏ qua
góc dưới phải, cùng kiểu với comic.

**3. Bàn liên lạc từng không mở được (sub 3, có vẻ đã sửa)**
Log ghi "The comms console now opens", nghĩa là sub đã sửa trong lúc chạy
nhưng chưa kịp test xong `stage1Done` có được ghi hay không. Cần kiểm lại
chuỗi: mở bàn liên lạc, qua ba bước, phát tín hiệu, xem cờ `smdg.stage1Done`
có thành `'1'` và nút Thiết kế tàu có mở khoá.

**4. Sáu đường chỉ dẫn Phase 2 từng tràn ra ngoài sân khấu (sub 4)**
Log ghi "All 6 callouts are now inside the stage at distinct heights",
tức là sub đã sửa nhưng chưa soi vision xác nhận. Cần chụp màn hình kiểm.

**5. Hai chỗ chữ "Sắp xong" cứng trong bộ đếm tiến trình (sub 5) — ĐÃ SỬA ✅**
Hai fallback `'Sắp xong'` trong `index.html` (settle và __pbProgress) đã
đổi sang hàm `txt(key)` đọc `smdg.lang` trực tiếp, cộng thêm script dịch
ngay sau khung `#pb` để dòng đầu tiên cũng đúng ngôn ngữ. `preloader.js`
đổi `'Almost ready'` thành `'Almost there'` cho khớp bản nhúng. Đã test:
EN thấy "Almost there", VI thấy "Sắp xong" ở cả trạng thái đầu và cuối.

**1. Menu điện thoại hộp rỗng — ĐÃ SỬA ✅**
`bottom: auto` đã có sẵn trong nhánh này. Còn 38px đệm dọc của
`.menu-actions::before` làm hộp cao hơn cụm nút; đã thu xuống 9px mỗi
bên trong media 620px. Đo 390x844: hộp 222px vs cụm nút 204px (chênh
18px, dưới ngưỡng 24px).

**Lỗi mới phát hiện trong đợt kiểm đầu game (16/11):**

**6. `playLaunch()` lần bị vượt qua không bao giờ resolve — ĐÃ SỬA ✅**
Token chống chạy hai lần im luôn các timer của lần cũ, kể cả resolve,
nên Promise cũ treo vĩnh viễn. Đã cho resolve ngay khi bị vượt qua.

**7. Cổng chặn che video mở đầu 200ms — ĐÃ SỬA ✅**
`gate()` resolve trước khi lớp cổng (z240) mờ xong, video mở đầu (z95)
bị tấm màn xám đè suốt 200ms. `gateHide()` giờ trả Promise chờ gỡ xong
và `gate()` await nó.

### Việc chưa sub nào làm xong

- Chưa có lần nào chơi thông từ đầu tới cuối bằng tay trên bản live
- Chưa quay video 30-60 giây theo thể lệ
- Chưa kiểm tương phản WCAG tự động cho toàn bộ chữ trên nền ảnh
