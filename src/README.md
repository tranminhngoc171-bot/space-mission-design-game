# src — game code

```
src/
├── data.generated.js  AUTO-GENERATED from data/*.json (python scripts/build_data.py)
├── engine.js          pure functions: computeMission(design, scenarioId, opts) -> result
├── ui.js              renders engine result into [data-ui] hooks, owns no math
├── index.html         semantic skeleton, every dynamic node has a data-ui hook
├── css/mission.css    all visual values in :root tokens
└── (orbit.js)         SVG orbit animation — not started
```

**Rule:** no numbers in the code. Every constant comes from `data/`
(`engineering_rules` in `instruments.json` holds the margins, eclipse minutes,
ops cost). If a balance number is in `engine.js`, it is a bug.

## Engine contract

```js
computeMission(design, scenarioId, opts) -> {
  design, scenario,
  resources:  { mass, power, battery, budget, data, comms, time },  // each {label, value, limit, unit, pct, status, detail}
  checks:     [{ id, label, pass, detail, fix }],
  objectives: [{ id, label, metric, operator, target, actual, pass, weight, gap, explain }],
  events:     [{ id, name, phase, narrative, mitigation_hint, severity }],
  score:      { total, mission_success, science_value, resource_efficiency, robustness, band, gates_pass },
  analysis:   [{ level, area, message, fix }],
  derived:    { dryMass, massWithMargin, draw, generation, eclipseWh, cost, generatedGbDay, downlinkGbDay, deliveredPct, lifetime }
}
```

`opts`: `{ seed }` (deterministic replay), `{ noEvents: true }` (clean-run
balance check used by `scripts/smoke_engine.mjs`), `{ data }` (inject tables).

## The re-skin contract — how the UI stays adjustable after the fact

The whole point of this layout: **the first HTML/CSS is a placeholder, not a
commitment.** Three rules make "fix the look later" a data change, not a rewrite:

1. **All visuals are tokens.** `css/mission.css` has exactly one `:root` block.
   Colours, fonts, sizes, spacing, radius, transition speed — everything else
   references `var(--token)`. Re-theming the entire game = editing ~20 lines in
   one block. Change tokens first; touch an individual rule only if a token
   genuinely cannot express it, and record why in the devlog.

2. **JS never writes style.** `ui.js` only sets `textContent`, structural
   `innerHTML`, `data-*` attributes, and one `width:%` on `.res-fill` (a value,
   not a look). Zero colours, zero font sizes, zero ad-hoc class names. So
   restyling cannot break the logic, and logic changes cannot break the styling.

3. **Structure is hooked, not hard-coded.** Every dynamic element in
   `index.html` carries `data-ui="key"`. `ui.js` finds nodes only through those
   hooks. The DOM may be restructured freely (move a panel, wrap it, add a
   decorative layer) as long as each `data-ui` key still exists — the JS does not
   care where the node sits.

Workflow: open the game, edit `css/mission.css` in DevTools → Sources →
**Ctrl+S** (writes straight to disk), Live Server reloads. No copy-paste loop.

**Forbidden in shipped CSS/HTML** (the "looks AI-generated" tells): gradients,
`backdrop-filter`, large border radii, emoji in UI copy, default blue/purple
accents, three identical cards in a row with round icons. All numbers in the UI
use `.num` (monospace, tabular). One accent colour, 1px rules, dense tables.

## Running it

```bash
npm run build:data   # regenerate src/data.generated.js after editing data/*.json
npm test             # engine smoke test (reference designs + determinism)
npm run serve        # http://localhost:5173 — or just open src/index.html
```

`data.generated.js` exists so the game runs from `file://` and from any static
host with no fetch/CORS dependency. `data/*.json` stays the single source of
truth; never edit the generated file.
