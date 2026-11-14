# Devlog

Append newest entry at the top. One entry per work session. Keep it factual: what changed, what broke, what is next.

---

## 2026-11-15 — NASA source traceability (docs/08)

**Ngọc**
- Added `docs/08-RESEARCH-SOURCES.md`: every NASA resource from the challenge's Resources tab mapped to what we actually took from it (four-segment completeness check, MDL screen order, CML scenario difficulty, Webb game benchmark, GMAT deferred with rationale).
- README now has a "Built on NASA's own mission-design method" section + citation-ready source list for the submission form.
- Read @bersious's branches `docs/martian-concept` (05/06/07) and `docs/sync-protocol` (09) — no merge yet, decision pending (see below).
- Note: numbered my doc **08** to avoid colliding with bersious's 06/07/09.

**Next**
- Decide on the Mars two-act proposal (docs/05 + 07) — my read: Act I first, Mars contingency as the flagship scenario *if* the satellite core runs end-to-end today.
- Build the engine.

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
