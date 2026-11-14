# 00 — Challenge Brief: what is actually graded

Source: https://www.spaceappschallenge.org/2026/challenges/space-mission-design-game/

## One-paragraph summary
Build an **interactive game** where players design, manage and simulate a **complete space mission** — objectives, spacecraft, instruments, launch vehicle, orbit, budget, power, mass, comms, lifetime — and experience the **trade-offs**: every gain in one area costs something in another.

## Hard requirements (implied by "a strong solution might include")
1. Functional interactive game/simulation with a clear UI
2. Mission configuration system (objective → requirements → design)
3. Resource management across: **Mass, Power, Budget, Data, Comms, Time**
4. Collaboration / multiplayer for **up to 4** participants (NOT mandatory — see below)
5. Mission simulation + evaluation system with feedback on **why** it succeeded/failed

## Is multiplayer mandatory? — NO
The wording is consistently permissive: *"You **may** consider…"*, *"The game **could** support…"*, *"might include…"*. Single-player is explicitly allowed ("participate individually **or** collaborate"). Our plan: single-player first, then **hot-seat team mode** (4 roles, one screen) + **share-design via URL**. No realtime networking.

## Judging criteria (NASA Space Apps standard five)
| Criterion | What it means for us |
|---|---|
| **Impact** | The game must actually teach mission trade-offs; post-mission analysis is the key deliverable |
| **Creativity** | Mission Control aesthetic, random events, scenario variety, shareable mission links |
| **Validity** | Numbers must be plausible (mass/power/cost in realistic ranges); compatibility checks must be real |
| **Relevance** | Directly answers the brief: complete mission, six resources, trade-offs |
| **Presentation** | 2-min demo video, clean README, live playable link, 5-slide deck |

## Feature priority (what to build, in order)
1. Core loop: choose objective → design → simulate → scored result
2. Six-resource dashboard with live updates + over-limit warnings
3. Compatibility checks (mass ≤ launcher capacity; power draw ≤ generation+battery; data ≤ downlink)
4. **Post-mission analysis** — itemised reasons for failure (highest educational value, mentioned 3× in the brief)
5. Random events (seeded, 3–5 types)
6. Hot-seat team mode (4 roles) + share design via URL
7. Multiple scenarios + sandbox mode
8. Tutorial/tooltips explaining each concept in plain language

## Explicit "do not" list (from our own analysis)
- No 3D/WebGL — 10–16h cost, zero graded value
- No realtime multiplayer — kills the demo if it breaks
- No pixel art — needs an artist, reads "student project"
- No backend/database — static site is enough; localStorage + URL-encoded designs
