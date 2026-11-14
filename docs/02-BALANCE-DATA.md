# 02 — Balance Data & Engine Formulas

`data/*.json` is the single source of truth. This document explains how the engine turns those numbers into the six resource bars and the scenario metrics.

## Derived values (compute in this order)

```js
// 1. MASS
total_mass_kg = bus.dry_mass_kg
              + power.mass_kg
              + battery.mass_kg
              + Σ instruments[i].mass_kg
mass_with_margin = total_mass_kg * 1.15          // 15% engineering margin

// 2. POWER
power_gen_w  = power.power_gen_w * (rtg ? (1 - 0.008*years) : 1)
power_draw_w = bus.power_overhead_w + Σ instruments[i].power_w
battery_need_wh = power_draw_w * (35/60)          // 35 min eclipse worst case
eclipse_margin = battery.capacity_wh / battery_need_wh

// 3. BUDGET
bus_cost      = bus.cost_musd * orbit.cost_multiplier
payload_cost  = Σ instruments[i].cost_musd
launch_cost   = launcher.cost_musd
ops_cost      = 6.5 * (duration_months / 12)
total_cost    = bus_cost + power.cost_musd + battery.cost_musd + payload_cost + launch_cost + ops_cost

// 4. DOWNLINK / DATA
downlink_gb_day = orbit.comm_window_pct/100 * orbit.downlink_mbps * 86400 / 8 / 1000
                + Σ instruments[i].downlink_gb_day
data_gb_day     = Σ instruments[i].data_gb_day
data_delivered_pct = min(100, 100 * downlink_gb_day / max(data_gb_day, 0.001))

// 5. LIFETIME / REVISIT
lifetime_years = orbit.base_lifetime_years * (1 - 0.1*radiation_index)   // simplified
revisit_hours  = orbit.revisit_hours

// 6. RESOLUTION (imaging quality vs orbit)
effective_resolution_m = instrument.resolution_m * (orbit.altitude_km / 400) ** 0.5
```

### Sanity numbers

| Orbit | downlink_gb_day (before terminal) |
|---|---|
| LEO SSO 400 | 12 Mbps × 24% × 86400 s ≈ **31 GB/day** |
| LEO 550 | 12 × 33% ≈ **43 GB/day** |
| MEO 20,200 | 20 × 62% ≈ **134 GB/day** |
| GEO 35,786 | 60 × 96% ≈ **622 GB/day** |

A mid-tier payload generates 32–55 GB/day. **That is the whole point**: in LEO you must buy a Ka-band terminal (+45 GB/day) or waste data. In GEO it is free — but you pay 2.6× bus cost and lose resolution.

## Verified feasible solutions (use these as regression tests)

Run `python scripts/validate_data.py` — it checks referential integrity and replays all three designs below against the formulas. If a change breaks one of them, the balance is broken.

### climate_watch — 154.5M / 180M, mass 626 kg, power 320/520 W
```
bus_medium + solar_large + bat_medium
cam_hires + cam_stereo + spec_tir + transponder_ka
orbit: leo_sso_400   launcher: falcon9_rideshare
→ imaging 145 ≥ 130 | thermal 80 ≥ 60 | revisit 12 ≤ 14 | lifetime 2.96 < 3 → o4 FAILS (see note)
```
> Note: `lifetime_years = 3 * (1 - 0.1*0.15) = 2.955` → **fails the 3-year objective.** Either use `leo_550` (4 y → 3.93) or accept the failure. This is a deliberate lesson: SSO 400 cannot deliver a 3-year record without a propellant decision. Keep it — the debrief should say exactly this.

### disaster_response — 104M / 120M, mass 390 kg, power 240/260 W
```
bus_small + solar_large + bat_medium + radar_sar + transponder_ka
orbit: leo_550   launcher: falcon9_rideshare
→ radar science 85 ≥ 80 | revisit 9 ≤ 9 | lifetime 3.93 ≥ 2 | delivered 100% ≥ 85%
```
Tight power (240/260) and no room for a second instrument — exactly the intended squeeze.

### space_weather — 148.7M / 220M, mass 193 kg, power 61/90 W
```
bus_small + solar_small + bat_medium + plasma + magnetometer
orbit: meo_20200   launcher: falcon9_dedicated
→ plasma 75 ≥ 70 | magneto 45 ≥ 40 | lifetime 8*0.945 ≈ 7.6 ≥ 5 | comm window 62% ≥ 60%
```

## Balance principles
1. **No dominant strategy.** Every instrument is beaten on at least one axis by another.
2. **The enabling hardware is never free.** Ka-band terminal is pure cost, and it is mandatory in LEO for big payloads.
3. **Orbit choice must be forced by the objective**, not by preference: imaging → LEO, comms/continuous → MEO/GEO.
4. **Budget must bite in at least one scenario.** disaster_response leaves ~16M slack.
5. **Failure must be explainable in one sentence.** If a designer cannot say why a design failed, the model is too complex.
