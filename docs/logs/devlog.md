# Devlog

Append newest entry at the top. One entry per work session. Keep it factual: what changed, what broke, what is next.

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
