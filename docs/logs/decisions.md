# Decision Records

Short, dated, one per design decision that someone might later question.

Format:
```
## YYYY-MM-DD — <decision>
**Context:** why it came up
**Decision:** what we chose
**Consequence:** what it costs us / what it rules out
```

---

## 2026-11-15 — No 3D, no realtime multiplayer
**Context:** 24 hours left, nothing built. 3D needs 10–16 h before any graded feature exists; realtime multiplayer dies publicly if a socket misbehaves during a 5-minute demo.
**Decision:** 2D "Mission Control" UI. Multiplayer = hot-seat 4 roles + shareable design URL.
**Consequence:** We trade wow-factor for a game that cannot break on stage. Both are optional per the brief ("may / could / might").

## 2026-11-15 — Data in JSON, engine in pure functions
**Context:** Two people editing the same codebase in one day.
**Decision:** All numbers live in `data/*.json`. The engine is pure functions with no DOM access; the UI only renders engine output.
**Consequence:** The two workstreams cannot block each other, and balance can be tuned without touching UI code.

## 2026-11-15 — Single satellite only
**Context:** `disaster_response` wanted a 6-hour revisit; no single orbit we model achieves it.
**Decision:** Lower the target to 9 h and state that constellations are out of scope.
**Consequence:** Simpler model, honest limitation. If a judge asks, the answer is "constellations are the sequel".

## 2026-11-15 — 15% mass margin as a hard gate
**Context:** Makes the launcher choice feel real instead of nominal.
**Decision:** The engine multiplies total mass by 1.15 before comparing to launcher capacity.
**Consequence:** Some designs that "just fit" will be rejected — that is the lesson, and the debrief must show the arithmetic.

## 2026-11-15 — Plain HTML + CSS + JS modules (no framework, no build)
**Context:** Two devs, two agents, 24 hours. Needed a stack where two people can edit in parallel without install or build conflicts, and where a judge opens a URL and it just runs.
**Decision:** Plain HTML/CSS/ES-modules in `src/`, SVG for graphics, deployed straight to GitHub Pages. React/Next/Vue/Phaser/Godot all explicitly rejected with reasons in `docs/08`.
**Consequence:** No component framework, so `ui.js` must be written as explicit DOM updates. Cost to reverse ≈ 2 h (engine and data are framework-independent), which is why the risk is acceptable.
