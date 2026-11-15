# Devlog

Append newest entry at the top. One entry per work session. Keep it factual: what changed, what broke, what is next.

---

## 2026-11-15 — Giai đoạn 2: Earth Mission Control (MDL / CML 1-4)

**Ngọc (agent)**
- Thêm thư mục `phase2/` hoàn toàn độc lập với `src/`: 9 file (engine cho sẵn + i18n + bridge + 4 feature + app + css + README). Không sửa một dòng nào của Giai đoạn 1.
- Giao tiếp hai chiều chỉ qua CustomEvent: `mars:sos-received`, `earth:dsn-command-sent`, `mars:beacon-deployed`, `phase2:goto-mars`, kèm `window.MARS_RESCUE_SHARED_STATE`.
- Bốn hồi theo CML: telemetry + chọn KPP, trade space bốn phân khu với bốn đồng hồ biên độ, checklist RYG JPL có khoá LAUNCH, canvas quỹ đạo Trái Đất tới Sao Hỏa + sóng DSN + EDL + tổng kết NASA analogue.
- Hai test chạy bằng node, không cần trình duyệt: `scripts/test_phase2_lifecycle.mjs` (luồng engine tới COMPLETED) và `scripts/test_phase2_dom.mjs` (shim DOM, mount đủ 8 file, kiểm tra render + khoá nút + shared state).
- Lỗi thật tìm được khi test: đèn hiệu cắm trước mốc `PROXIMITY_WAIT` làm engine bỏ qua và sứ mệnh treo ở LAUNCHED. Sửa trong bridge: ghi nhớ và hoàn tất khi tới mốc.
- Cân bằng đo được: ở 250 Sol chỉ 2/64 tổ hợp qua CML 4, ở 300 Sol là 6/64. Ghi vào `phase2/README.md`, không tự sửa engine cho dễ.

**Next**
- Chờ Thiện Nhân phát `mars:sos-received` từ cuối Phase 1 và nhận `earth:dsn-command-sent` cho nhiệm vụ cắm đèn hiệu.
- Còn thiếu theo docs/12 §4: chỉ số đồng thuận ba vai trò (data + engine), dữ liệu Mission Viz cho tab Sao Hỏa.

---

## 2026-11-15 — Đồng bộ theo luật agent, tách PR #6

**Ngọc (agent)**
- Pull `main` tới `fc3b7f0`, đọc `docs/14-AGENT-RULES.md`, `NIGHT_SHIFT_REPORT.md`, `docs/12-ENGINE-NOTES.md`.
- Tách PR #6 theo mục 7 của luật: PR mới `feat/engine-extras` chỉ mang `scripts/smoke_engine.mjs` và mục log này. `src/engine.js`, `src/data.generated.js`, `scripts/build_data.py`, `docs/08-RESEARCH-SOURCES.md` đã nằm trên `main` nên không gửi lại.
- Không đưa `src/index.html` và `src/ui.js` vào (vùng của Thiện Nhân).
- Không ghi đè `src/css/mission.css`: bản trên `main` dài 424 dòng, header ghi `Owner: @bersious`, trong khi mục 1 của luật xếp file này vào vùng Ngọc. Giữ nguyên bản của `main` và chờ chốt chủ sở hữu.
- Kiểm tra trên engine hiện tại của `main`: ba thiết kế tham chiếu qua hết cổng tương thích, clean-run khớp `docs/02-BALANCE-DATA.md`, seed 42 lặp lại đúng điểm.

**Next**
- Soát lại engine sau bản sửa NaN của Thiện Nhân, thêm test cho trường hợp design thiếu `duration_months`.
- Phần engine còn thiếu theo `docs/12` §4: scenario cứu hộ, chỉ số đồng thuận ba vai trò, dữ liệu cho Mission Viz 2D.

---

## 2026-11-15 — repo bootstrap

**Ngọc**
- Created repo, invited @bersious with write access.
- Wrote challenge brief, game design, balance data (12 instruments, 3 buses, 4 orbits, 5 launchers, 7 events, 3 scenarios), scoring model.
- Hand-verified three feasible designs as regression tests (see `02-BALANCE-DATA.md`).
- Found + fixed: `disaster_response` revisit target was 6 h, unreachable by any single-satellite orbit → set to 9 h.

**Bersious**
- (waiting on invite acceptance)

**Next**
- Agree `engine.js` ↔ `ui.js` contract.
- Build the mass/power/budget gates first — they are the demo.

## Open questions
- Framework: plain HTML+JS modules vs. React? (plain = fewer moving parts, 1-day friendly)
- Do we need the tutorial on first run, or only tooltips?
