# 04 — 24-Hour Plan

Deadline reality: **one day, nothing built yet.** This plan is for two people working in parallel on the same repo.

## Split

| @bersious — UI & presentation | @tranminhngoc171-bot — logic & data |
|---|---|
| Mission Control layout, dark theme, panels | Simulation engine (phases, events, resource math) |
| SVG spacecraft schematic + orbit animation | Compatibility gates & resource computations |
| Resource bars, red/green states, tooltips | Scenario objective evaluation |
| Debrief screen visuals | Scoring + itemised failure analysis copy |
| Screenshots for submission | README, demo script, data balance |

**Interface contract (agree in the first 20 minutes, then do not change it):**

```js
// engine.js  (Ngọc)
computeMission(design, scenario, seed) -> {
  resources: { mass, power, budget, data, comms, time },   // each: {value, limit, pct, status}
  checks:    [{ id, label, pass, detail }],
  objectives:[{ id, label, metric, target, actual, pass, weight, explain }],
  events:    [{ id, name, phase, narrative, effect }],
  score:     { total, mission_success, science_value, resource_efficiency, robustness, band },
  analysis:  [{ level:'FAIL'|'WARN', area, message, fix }]
}
// ui.js     (Bersious) — renders the above, owns no math
```

## Hour-by-hour

| Time | Bersious | Ngọc |
|---|---|---|
| 0:00–0:30 | repo pull, agree contract, pick framework | same + validate data JSON |
| 0:30–2:30 | static layout: 5 design screens, resource bar component | engine skeleton: mass/power/budget checks |
| 2:30–4:00 | instrument picker + bus/orbit/launcher selectors wired to real data | data/downlink/lifetime math + seed RNG |
| 4:00–5:00 | **integration checkpoint #1**: full design → simulate → numeric result on screen | same, fix gaps |
| 5:00–7:00 | orbit SVG animation + spacecraft schematic | events engine + objective evaluation |
| 7:00–8:30 | **checkpoint #2**: debrief screen renders analysis list | scoring + analysis generator (5 items, with fixes) |
| 8:30–10:00 | tooltips, tutorial 3 steps, polish, red states | 3 scenarios tuned, balance regression run |
| 10:00–11:30 | hot-seat team mode (4 role cards, gating) | share-design URL encode/decode |
| 11:30–13:00 | screenshots, demo recording | README polish, submission write-up |
| 13:00–14:00 | **buffer** (there will be a bug) | same |

## Cut list (in this order, if behind)
1. Team mode → keep only the 4-role card UI as a "concept" screenshot
2. Share URL → drop, keep localStorage save
3. Sandbox mode
4. Orbit animation → static SVG
5. Third scenario

## Never cut
- The red/green resource bars
- The debrief with itemised "why it failed + how to fix"
- At least one scenario that is winnable and one that is tight
- Demo video

## Definition of done (submission)
- [ ] Game runs from a URL a judge can open on their phone
- [ ] All 6 resources visible and reacting to choices
- [ ] Every scenario playable end-to-end in under 4 minutes
- [ ] Debrief explains failures in specific numbers
- [ ] 2-minute demo video, 5-slide deck, README with screenshots
- [ ] Submitted on the Space Apps platform **before** the deadline, not at it
