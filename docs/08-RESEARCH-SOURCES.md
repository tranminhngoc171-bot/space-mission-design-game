# 08 — Research Sources: What NASA Handed Us, and What We Did With It

**Owner:** Ngọc
**Status:** reference — no code depends on this file, but the submission does

This document exists for two reasons:

1. **Traceability.** Every design assumption in `docs/02-BALANCE-DATA.md` should be traceable to something NASA published, not to our taste.
2. **Global-judging eligibility.** Judges reward projects built on the agency's own material. If we use it, we must be able to say exactly where.

All links below are from the Resources tab of the challenge page.

---

## 1. The sources, and their actual role in our build

| Source | What it is | Role in our project | Status |
|---|---|---|---|
| [Design and Develop Science Missions](https://www.nasa.gov/wp-content/uploads/2025/04/250323-design-and-develop-science-mission.pdf) (PDF) | NASA's systems-engineering walkthrough of a science mission, from need → requirements → design → verification | Defines the **four mission segments** our six resources must cover | **used** — §2 |
| [Mission Design Lab (MDL)](https://etd.gsfc.nasa.gov/capabilities/integrated-design-center/mission-design-lab/) | Goddard's rapid concept-development environment (Office Hours → Concept Development → Trade Studies → Point Design) | Our **design screen order** and the name of our flow | **used** — §3 |
| [Concept Maturity Levels](https://dataverse.jpl.nasa.gov/dataset.xhtml?persistentId=hdl:2014/44299) (JPL) | CML 1–9 framework for how mature a mission concept is | Labels our **three scenarios** by maturity, so difficulty is meaningful rather than arbitrary | **used** — §4 |
| [A Learning Game About Telescopes](https://science.nasa.gov/mission/webb/game-build-it-yourself/) (Webb) | NASA's own design-a-telescope game, 3 levels, gated choices, real-mission comparison at the end | The **benchmark** we are measured against by any judge who knows it. Our debrief borrows its "here is the real mission you just designed" ending | **benchmarked** — §5 |
| [GMAT](https://software.nasa.gov/software/GSC-19468-1) | Open-source mission analysis / trajectory tool | Not run live. Optional offline validation of our revisit and eclipse numbers | **deferred** — §6 |
| [NASA Mission Viz](https://nasa.github.io/mission-viz/) | WebGL 3D mission/trajectory visualiser | We are not shipping 3D. Cited as the tool a player graduates to | **not used, cited** |
| [CubeSat 101](https://www3.nasa.gov/sites/default/files/atoms/files/nasa_csli_cubesat_101_508.pdf) | Practical CubeSat mission handbook (ConOps → launch → ops) | Source for realistic failure modes in `data/events.json` | **partially used** |
| [2023 VR mission visualisation challenge](https://www.spaceappschallenge.org/2023/challenges/visualize-a-space-mission-using-virtual-reality/) | Past challenge, same subject, VR | Precedent check only — confirms the "visualise a mission" space is crowded, so we differentiate on *decisions*, not graphics | **not used** |
| [CSA Digital Games](https://www.asc-csa.gc.ca/eng/youth-educators/digital-games-and-activities.asp) | Canadian Space Agency game collection | Style comparison for accessibility and tone | **not used** |

---

## 2. The four mission segments — our completeness check

NASA's document splits a mission into four segments. This is the test of whether our six resources are the *right* six: if a segment has no resource attached to it, the model has a hole.

| Segment | What it is | Where the player touches it | Resource it consumes |
|---|---|---|---|
| **Launch** | Launch vehicle and services to get to space | `data/launch_vehicles.json` — 5 launchers, capacity per orbit | Budget, Mass |
| **Space** | Spacecraft, instruments, orbit | `data/instruments.json` + `bus_options` + `data/orbits.json` | Mass, Power |
| **Ground** | Ground stations, mission control, data reception | Comms payload + orbit comm window → downlink calculation | Comms, Data |
| **User** | Scientists who analyse and apply the data | Debrief: what the scientist actually receives | Data, Time |

**Result: all four segments are covered, and every one of the six resources maps to at least one segment.** That is not an accident of our design — it is the check that told us the six were correct.

The one segment we model thin is **Ground**: we collapse an entire ground network into a single "comm window %" per orbit. That is a documented simplification, and the honest way to say it in the submission is:

> "Our ground segment is a single aggregate parameter (comm window, downlink rate) rather than a station network. This keeps the game playable in eight minutes at the cost of ground-station scheduling realism."

Judges accept stated simplifications. They do not accept unstated ones.

---

## 3. MDL — why our screens are in the order they are

Goddard's Mission Design Lab escalates a concept through four study levels. Our design flow mirrors it, and this is worth stating out loud because it makes our screen order defensible:

| MDL level | What happens there | Our equivalent |
|---|---|---|
| **Office Hours** | Fast brainstorming, identify the hard problems | Scenario briefing screen: objective + budget + the one dominant constraint |
| **Concept Development** | Feasibility and risk assessment | Bus + power + battery selection; the first red resource bar |
| **Trade Studies** | Compare architectures and options | Instrument selection, and the orbit/launcher compatibility gate |
| **Point Design** | Detailed design, equipment lists, cost estimates | Review screen: full cost rollup, mass margin, itemised checks |

The debrief mirrors MDL's multi-disciplinary trade-off analysis: it does not say "you lost," it names the discipline that lost (power, mass, comms, budget) and the kilogram, watt, or dollar that decided it.

---

## 4. CML — why the three scenarios have different difficulty

JPL's Concept Maturity Levels describe how developed a concept is. We use them as the *reason* our three scenarios feel different, rather than as flavour text:

| Scenario | CML | Why |
|---|---|---|
| `climate_watch` | **CML 2 — feasibility** | Broad objective, generous budget, forgiving margins. Teaches the loop. |
| `disaster_response` | **CML 3 — trade studies** | Tight revisit requirement forces a real architecture trade (SAR vs. cheaper optics + orbit change). |
| `space_weather` | **CML 4 — point design** | Mature, specific orbit and instrument requirement; almost no freedom left, so the player must optimise rather than explore. |

Player-facing rule: **difficulty is not "more numbers," it is "less freedom."** That is the same progression JPL describes, and it is why we did not build a "hard mode" that just multiplies costs.

---

## 5. The Webb telescope game — our honest benchmark

NASA already published a design game for the Webb telescope. Any judge who has played it will compare us to it. What it does and what that means for us:

| Webb game | Ours | Verdict |
|---|---|---|
| 3 levels, 1 objective → many objectives | 3 scenarios, each with 4 weighted objectives | **comparable** |
| Choices become unavailable when incompatible with the objective | Compatibility gate: launcher × orbit × mass | **comparable** — ours is arithmetically stricter |
| Animated launch sequence | No launch animation; the *checks* are the drama | **we are weaker, by choice** |
| Ends by naming real NASA missions with similar characteristics | Debrief names the real dataset the design would have produced | **we are stronger** — ours points at open data, not just a mission name |
| Single player | Single player + hot-seat 4 roles + shareable design URL | **we are stronger** |

**Lesson taken:** the Webb game's ending — "here is the real mission you just designed" — is the single cheapest credibility move available in this genre. Ours is the data-product version: *"this design would have produced a Sentinel-1 class SAR acquisition over the Mekong Delta at 06:00 UTC."*

**Lesson refused:** an animated launch. It is 2–3 hours for a cutscene that teaches nothing, and it is the first thing to cut when the schedule slips.

---

## 6. GMAT — deliberately deferred, and why that is defensible

GMAT could give us high-fidelity revisit times and eclipse durations for our four orbits. We chose not to run it during the hackathon:

- Our revisit numbers are already physically plausible (SSO ~12 h, MEO ~12 h, GEO 24 h) and are stated as *approximations*.
- Running GMAT properly (building the mission, propagating, extracting ground-track repeat intervals) is 2–4 hours of work that produces numbers a player cannot distinguish from ours.
- The risk is not that judges check our revisit maths. The risk is that we have no working game to check.

**If there is time after the vertical slice:** run GMAT for `leo_sso_400` only, export the eclipse fraction and revisit interval to CSV, and add `"validated_by": "GMAT 2023a"` to that orbit's entry. One validated orbit is worth more than four approximate ones, because it demonstrates the method.

---

## 7. Citation block for the submission

Copy this into the project submission form and the demo video credits:

```
Mission-design methodology:
  NASA, "Design and Develop Science Missions" (2025)
  NASA Goddard Mission Design Lab, https://etd.gsfc.nasa.gov/capabilities/integrated-design-center/mission-design-lab/
  NASA/JPL Concept Maturity Levels (hdl:2014/44299)

Benchmarked against:
  NASA Webb "Build It Yourself" telescope design game, https://science.nasa.gov/mission/webb/game-build-it-yourself/

Physical constants (Mars scenario):
  NASA NSSDC Mars Fact Sheet, https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html

Open data the mission would have produced:
  Copernicus Sentinel-1 (SAR), Sentinel-2 (multispectral) — open access
  NASA SMAP, MODIS/VIIRS, GPM IMERG — open access
```

---

## 8. What this document does *not* claim

To keep us honest in front of judges who will know better:

- We did **not** run GMAT. Our orbit numbers are textbook approximations, not propagated solutions.
- We model the ground segment as one aggregate parameter, not a station network.
- We model power as a static generation-vs-draw balance plus an eclipse battery check. There is no thermal model, no seasonal beta-angle variation, no degradation curve beyond a single radiation multiplier.
- We do not simulate attitude control, propulsion sizing, or communications link budget (dB, antenna gain, Eb/N0). We simulate the *decision*, not the physics.

Every one of those is a place where a real mission designer would go deeper. Saying so first is what separates a credible simplification from a hole in the work.
