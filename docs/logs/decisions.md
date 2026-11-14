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

## 2026-11-15 — Trace every design number to a NASA source
**Context:** Global judging rewards work grounded in agency material; judges also punish invented numbers.
**Decision:** `docs/08-RESEARCH-SOURCES.md` maps each NASA resource to its role in our build, and §8 explicitly lists what we do *not* model (no GMAT propagation, no link budget, no thermal). The submission will cite: the four-segment systems-engineering PDF, Goddard MDL, JPL CML, Webb telescope game, NSSDC Mars Fact Sheet.
**Consequence:** We must keep the stated simplifications honest in the demo — no claiming "high-fidelity" anywhere. If we later run GMAT, only one orbit gets validated and it is labelled as such.

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
