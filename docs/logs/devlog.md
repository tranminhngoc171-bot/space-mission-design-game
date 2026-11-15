# Devlog

Append newest entry at the top. One entry per work session. Keep it factual: what changed, what broke, what is next.

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
