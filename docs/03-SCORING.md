# 03 — Scoring

## Final score (0–100)

```
Score = 0.40 × MissionSuccess
      + 0.25 × ScienceValue
      + 0.20 × ResourceEfficiency
      + 0.15 × Robustness
```

### MissionSuccess (0–100)
Weighted sum of the scenario's objective checks:

```
MissionSuccess = 100 × Σ ( objective.weight × satisfied(objective) )
```
An objective is satisfied when the computed metric meets the operator/target. Partial credit for near-misses is **not** given on hard objectives, but the debrief shows the gap in units.

### ScienceValue (0–100)
```
science_total   = Σ instruments[i].science_value   (after random-event damage)
ScienceValue    = min(100, 100 × science_total / scenario.science_reference)
```
`science_reference` is set per scenario to roughly 1.4× the "reasonable" total, so a strong design scores ~70–80 and only an extravagant one hits 100.

### ResourceEfficiency (0–100)
Two halves, because there are two ways to waste:

```
budget_eff  = 100 × (1 − max(0, spare_budget_pct − 25) / 75)   // using <75% of budget is waste
power_eff   = 100 − 40 × max(0, 0.10 − power_margin_pct)       // margin below 10% is risk
              −  20 × max(0, power_margin_pct − 60)/40          // margin above 60% is over-engineering
ResourceEfficiency = 0.6 × budget_eff + 0.4 × power_eff
```

### Robustness (0–100)
How the mission held up against events:
```
Robustness = 100 × (1 − severe_failure_count / events_fired)
```
Plus **+10 coordination bonus** in team mode if no forced rollbacks occurred (capped at 100).

## Score bands (used in the debrief copy)

| Score | Verdict | Debrief headline |
|---|---|---|
| 85–100 | Nominal | "This mission would fly. Hand it to a program office." |
| 70–84 | Marginal | "It works, but a reviewer would ask for margin." |
| 50–69 | Degraded | "Objectives partially met — here is exactly what pulled you off." |
| 25–49 | Compromised | "You launched, but the science case does not survive." |
| 0–24 | Failure | "Countdown aborted. Here is the first thing that breaks." |

## Post-mission analysis (the graded part)

The debrief must list **itemised, causal, numeric** reasons. Format per item:

```
[FAIL] Mass: 626 kg × 1.15 margin = 720 kg > Electron capacity 200 kg
       Fix: switch launcher (Falcon 9 Rideshare, +0M, 900 kg) or drop spec_tir (−55 kg)
[WARN] Power: 320 W draw vs 520 W generation = 38% margin (healthy)
[FAIL] Data: 67 GB/day generated vs 31 GB/day downlink → 54% of science lost
       Fix: add transponder_ka (+45 GB/day, −22 kg, −6M) or move to leo_550
```

Rules for the copy:
1. Always show **both** numbers in the comparison.
2. Always give **at least one concrete fix** with its cost.
3. Never say "wrong" without saying *why it is physically wrong*.
4. Cap at 5 items, ordered by score impact.

## Worked example (climate_watch, the design in 02-BALANCE-DATA)

| Term | Value | Weighted |
|---|---|---|
| MissionSuccess | 0.30+0.20+0.15+0.15 = 0.80 → **80** (fails lifetime) | 32.0 |
| ScienceValue | science_total 145+80 = 225 / 300 → **75** | 18.75 |
| ResourceEfficiency | budget used 86% → 100; power margin 38% → 100 → **100** | 20.0 |
| Robustness | 2 events, 0 severe → **100** | 15.0 |
| **Total** | | **85.75 — Nominal** |

Change one thing — take `leo_550` instead — lifetime passes → 100 success → total ≈ 93. That is the learning moment, and the debrief should point at it.
