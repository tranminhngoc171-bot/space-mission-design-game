# 01 — Game Design

## Aesthetic
**Mission Control.** Dark background, monospace numerals, thin-bordered telemetry panels, live-updating numbers. SVG schematic of the spacecraft, SVG orbit animation. No 3D, no WebGL, no pixel art.

## Player flow (single-player)

```
1. BRIEFING      pick a scenario → read objective cards + budget + duration
2. DESIGN        five sub-screens, each with live resource bars:
     a. Bus        (small/medium/large + power source + battery)
     b. Payload    (pick 0..max_instruments, each shows its 5 stats)
     c. Orbit      (4 options with plain-language trade-offs)
     d. Launcher   (filtered by orbit class, capacity bar vs. total mass)
     e. Review     (compatibility checklist, budget breakdown)
3. SIMULATE      phases: launch → commissioning → operations → deorbit
                 seeded random events fire; resources evolve per phase
4. DEBRIEF       score breakdown + itemised failure analysis + "why" tooltips
5. REDESIGN      back to any design screen with state preserved
```

## The six resources (dashboard, always visible)

| Bar | Source of truth | Turns red when |
|---|---|---|
| Mass | bus dry + power + battery + instruments + margin | total > launcher capacity − 15% margin |
| Power | array/RTG generation vs. bus overhead + instruments | draw > generation (or battery can't cover eclipse) |
| Budget | scenario budget vs. bus+instruments+launcher+ops | spent > budget |
| Data | instrument GB/day vs. downlink capacity | generation > capacity (backlog grows) |
| Comms | orbit comm window × downlink rate (+ terminal) | data_delivered_pct < objective |
| Time | mission duration vs. lifetime & schedule | lifetime < duration, or slip eats the window |

## Compatibility checks (hard gates before simulate)
1. `total_mass × 1.15 ≤ launcher.capacity[orbit]` → else: "cannot launch"
2. `power_draw ≤ power_gen` (else battery must cover eclipse: `draw × 35min ≤ battery_wh`)
3. `data_gb_day ≤ downlink_gb_day` (else backlog penalty in scoring)
4. `instrument_count ≤ bus.max_instruments`
5. `orbit ∈ launcher_classes` of chosen launcher

## Team mode (hot-seat, 4 roles)
One screen, four role cards. Each role **owns** certain screens and can only *propose* changes to others; the owner must approve. Roles:

| Role | Owns | Job |
|---|---|---|
| Mission Director | scenario, budget, schedule | keeps the mission affordable and on time |
| Spacecraft Engineer | bus, power, battery, launcher | makes it flyable |
| Science Lead | instruments, orbit | maximises science value |
| Comms & Data | downlink, data, events response | makes the data actually arrive |

Negotiation moments are the point: Science Lead wants the telescope; Director sees the budget; Engineer sees the 300 W; Comms sees 35 GB/day. The final score includes a **coordination bonus** based on how few forced rollbacks happened.

## Random events
Seeded per run (`?seed=1234` in URL) so runs are reproducible and shareable. Events fire in operations phase with the probabilities in `data/events.json`. Each event shows its mitigation hint in the debrief.

## Share a design
The full design state is serialised to a URL parameter (`#design=base64(json)`). Opening the link restores the exact design — used for comparing designs and for judges to replay a run.

## Scoring
See `03-SCORING.md`.

## Tutorial / educational layer
- Every stat has a tooltip written in plain language (the `blurb` + `tradeoff` fields in the JSON are the copy).
- First-run guided tour: 5 steps, skippable.
- Beginner mode hides advanced numbers, shows only red/green indicators.
