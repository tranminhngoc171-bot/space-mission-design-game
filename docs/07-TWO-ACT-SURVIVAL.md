# 07 — Two-Act Structure: Design, then Survive
### Reframing proposal — supersedes the single-scenario sketch in doc 05 ⚠ needs Ngọc's decision

> Read this before doc 05's §4. This document changes the shape of the game, not just its content.

---

## 1. The tension we have to name first

What Bersious is describing — **one person alone on Mars, farming crops, rebuilding contact with Earth, watching the crew recede toward home, scavenging wreckage** — is a **survival game**. Our current design is a **mission-configuration simulator**. These are different genres, and the NASA brief describes the second one:

> "design a spacecraft, select scientific instruments, choose a launch vehicle and orbit, and manage key constraints such as budget, mass, power, communications, data, and mission lifetime"

If we ship a pure survival game, we lose **Relevance** (we no longer answer "design a mission") and probably **Validity** (nothing to validate scientifically). That is 2 of 5 criteria — 40 % of the score.

**But there is a structure that gives us both, and it is better than either alone.**

---

## 2. The two-act structure

```
ACT I — DESIGN (2–4 min)          ACT II — SURVIVE (5–8 min)
─────────────────────────         ────────────────────────────
You are the mission architect.    You are the person left behind.
Pick bus, power, instruments,     Every sol: allocate limited energy,
orbit, launcher. Six resources    mass and time across competing needs.
go red or green. Compatibility    Farm, repair, scavenge, transmit.
checks gate the launch.           The crew is 200 days out and not turning back.
Score: does it fly?               Score: do you live, and do you get home?

Earns: Relevance, Validity        Earns: Impact, Creativity, Presentation
                                  Delivers Ngọc's humanist message
```

The two acts are **the same six resources, viewed from two ends of the same mission.** That is what makes it one game and not two.

**Why this works for the brief:** Act I is literally the challenge statement, executed properly. A judge reading "design a spacecraft, select instruments, choose orbit, manage six constraints" sees compliance in the first four minutes. Then Act II is the part they remember.

**Why it works for us as builders:** Act I is the engine Ngọc is already building. Act II reuses the same six resource bars and the same `computeMission()` skeleton — it changes the objective set and the loop cadence.

---

## 3. Mapping the six resources onto survival

This is the crux. If the mapping is weak, the two acts feel bolted together. Here it is:

| Brief's resource | Act I meaning | Act II meaning | How it fails |
|---|---|---|---|
| **Mass** | Spacecraft dry mass vs. launcher capacity | **Everything you own.** Consumables, seed stock, spare parts, rover payload. Every trip you take costs mass you cannot replace | You carried too little, or you burned it on the wrong thing |
| **Power** | Array/RTG generation vs. draw | **The sol's real currency.** Drilling, heating, charging the rover, transmitting — all draw from the same pool. Winter and dust storms cut generation | You cannot run the heater and the radio on the same night |
| **Budget** | Dollars | **Calories.** Reframed as the consumable budget: total food energy vs. daily need. The number that actually kills you | You run out before rescue is possible |
| **Data** | Instrument GB/day vs. downlink | **Evidence of value.** Science you can still do alone. It is also your argument for why anyone should spend money coming back for you | You survive but produce nothing worth retrieving |
| **Comms** | Downlink capacity vs. orbit windows | **The goal itself.** You have no dish, no network. You are rebuilding a channel out of salvaged hardware | Silence. Nobody knows you are alive |
| **Time** | Mission lifetime vs. duration | **Sols until starvation, and sols until the next launch window.** Two clocks, and they are not the same clock | The window opens after you die |

**The design insight:** `Budget` is the only resource that changes meaning substantially. Everything else maps almost one-to-one. That means the engine's resource model survives the reframe nearly intact — we add a calorie pool and a second clock, and we are done.

---

## 4. Act II — the actual loop

Each **sol** is one turn. The player has a fixed energy pool and must allocate it:

| Action | Costs | Produces | Risk |
|---|---|---|---|
| **Tend the crop** | Water, ~2 h, some power for lighting | Calories (delayed by growth cycle) | Crop failure is unrecoverable |
| **Make water** | Fuel stock, power, ~4 h | Water for crop + drinking | Chemical hazard — mishandled, it explodes |
| **Charge the rover** | Power (competes with heating) | Range for one trip | Drained battery strands you away from base |
| **Scavenge wreckage** | Rover range, time, mass capacity | Components: antenna parts, batteries, solar cells, a radio | The wreck is far; the trip is one-way if you misjudge power |
| **Attempt transmission** | Power, time, alignment | Progress on the comms channel | Each attempt may be silent; you learn slowly |
| **Repair / seal breach** | Mass (parts), time | Prevents catastrophic loss | Ignoring it costs everything |
| **Do science** | Power, time | Data — the value argument | Every hour here is an hour not spent surviving |

**The loop's cruelty, borrowed from the film's structure:** each success creates the next problem. Fix the water supply and you have consumed fuel you needed for the return. Extend the crop and you have burned power the heater needed. Get the radio working and you learn the crew cannot turn back.

---

## 5. What the film actually gives us, beat by beat — with real numbers

These are specific, citable, and directly convertible to balance tables.

| Beat | The real detail | Game rule |
|---|---|---|
| **Farming** | ~2,000 potatoes grown; needs ~1,100 kcal/day (rising to 1,500); ~150 kcal per potato → **7.3 potatoes/day → only ~285 days of food**, not the 1.5 years the book claims | Food pool must be generously *insufficient*. The 285-day figure is the designed tension: rescue is further away than the crop lasts |
| **Why potatoes fail as a strategy** | A potato tuber cannot be regrown once flash-frozen — the soil bacteria die with it. Seeded crops (orthodox seeds) survive freezing; tubers do not | Model crop as **non-renewable after a loss event**. One breach and the food clock restarts with no fix available. That is the true midpoint of the film |
| **Soil** | Martian soil contains **perchlorates**, toxic to plants — Weir did not know this when he wrote it. NASA's own fact-check flags it | Add a "soil treatment" cost. It is a real constraint, and it is a chance to be *more* accurate than the source |
| **Water** | Hydrazine (N₂H₄) decomposes to nitrogen and hydrogen over a catalyst; burn the hydrogen with oxygen to get water. Watney's first attempt **exploded** | Water production is a high-yield action with a real failure probability and a repair cost when it fails |
| **Communication** | He recovers a **1997 lander probe**, links it to the rover, and rebuilds a text channel — light-time is ~4–24 min one way, so every exchange is a letter, not a conversation | Comms progress is measured in **rounds**, not seconds. Each message is an action that costs a sol. This is what makes silence feel expensive |
| **Rover trips** | The rover was designed for roughly **35 km per charge**; he extends it with extra batteries and by not running the heater. Pathfinder's battery allowed only about **40 charge-discharge cycles** | A hard range limit with a modification path. The "no heater" trade-off is a perfect mechanic: you save power and risk the cold |
| **Crew status** | The crew genuinely believe he is dead and are months into the return journey. They are not a rescue party — they are a fact he has to live with | Act II shows a **crew distance counter that only increases** for the first half. Hope must be earned, not assumed |

---

## 6. Scavenging debris — Bersious's own addition, and it is the best mechanic here

Note carefully: **collecting satellite wreckage is not in the film.** In the source there is a buried intact probe and a crashed resupply ship, but no scavenging loop. This idea is original to our team, which means:

- **No IP risk whatsoever** — it is not lifted from anything
- It is a genuinely strong mechanic: it turns the map into a resource, it rewards exploration, and it converts the abstract "Mass" bar into a visible, physical inventory
- It gives Act II its **spatial dimension**, which the film has but a dashboard does not

Design it as follows:

| Wreck class | Contains | Why it matters |
|---|---|---|
| Old lander | Antenna, computer, radio | The comms path — the first major objective |
| Failed resupply ship | Intact cargo, damaged structure | Food and parts, but reaching it is a long trip |
| Dead orbiter debris | Solar cells, batteries, fuel | Power and range — the enabler for everything else |
| Unknown / unmarked | Random | Risk and discovery |

Each wreck should require a **mass-vs-range decision**: you can carry little and return safely, or carry much and risk stranding. That is the same trade-off as Act I, expressed physically.

---

## 7. The humanist message, now earned rather than stated

With Act II in place, Ngọc's requirement stops being a copywriting problem and becomes a systems problem. The player *feels* the message because the mechanics impose it:

| The message | The mechanic that produces it |
|---|---|
| **A person is worth more than the mission** | The crew's return is not free. Someone, somewhere, has to decide to spend for one life. The player only learns this because they are the life |
| **Nobody survives alone** | The comms channel is built from salvage. Every part came from somebody else's dead machine — literal inheritance |
| **Institutions can be wrong; individuals can be right** | The crew that was ordered home and turned back anyway |
| **Ingenuity is care** | Fixing the seal *is* staying alive for the people who are looking for you |

The debrief states numbers, never morals. One line at the end, after the score:

> *Every kilogram you left out was a decision made on behalf of someone else.*

---

## 8. Honest cost

| Work | Hours |
|---|---|
| Calorie pool + second clock in engine | 2.0 |
| Sol loop (action allocation, turn resolution) | 3.0 |
| Wreck map + scavenging (4 sites, mass-vs-range) | 3.0 |
| Crop lifecycle + irreversible loss state | 2.0 |
| Comms rebuild as multi-step progress | 2.0 |
| Act II UI screens (sol panel, map, log) | 4.0 |
| Act transition + framing copy | 1.5 |
| Balance pass (it must be winnable and tight) | 2.5 |
| **Total for Act II** | **~20 h** |

**This is a bigger commitment than doc 05's 11 hours, and it is bigger than the 24-hour plan can absorb alongside a full Act I.**

### Therefore, the recommendation

**Do not attempt both acts at full depth in this hackathon.** Build:

1. **Act I complete** — the mission configurator, six resources, compatibility gates, debrief. This is what the brief grades, and it is already designed.
2. **Act II as a vertical slice** — one sol loop, three actions (farm / scavenge / transmit), one wreck site, one failure mode, the crew-distance counter. Ten minutes of play, ending on a real decision.

A **vertical slice is not a lesser product** — it is a complete argument. A judge who plays four minutes of Act I and four minutes of Act II understands the whole game. A judge who plays eight minutes of a half-built Act II understands nothing.

If time remains after the slice works: add the second wreck, then the crop-loss event, then the second clock.

### Cut list for Act II, in order
1. Third and fourth wreck sites
2. Water-production minigame (make it a button)
3. Crop growth animation
4. Multi-step comms (single progress bar instead)
5. Science-as-value scoring in Act II
6. **Act II itself** — but if we cut it, we ship a competent simulator with no soul, and we should know that going in

---

## 9. Questions for Ngọc

1. **Do we accept a two-act game, or stay a pure simulator?** This is the fork. Everything downstream depends on it.
2. If two acts: is ~20 h of Act II acceptable, or do we scope it to the 10-minute vertical slice (~8 h)?
3. `Budget` becomes calories in Act II. Comfortable reusing the field name, or rename to `consumables` and keep the label "Budget" in Act I only?
4. The crew-distance counter only increases for the first half of Act II. Do we want that hopelessness in a four-minute demo, or should the demo start after hope has been established?
5. Does scavenging wreckage risk reading as "not a space mission design game" to a judge? My view: no, if Act I comes first and is visibly complete.

---

## 10. Sources

- Calorie and potato arithmetic, perchlorate caveat: `theprepared.com/blog/matt-damon-grew-potatoes-on-mars-using-poop-is-that-realistic`
- Tubers vs. orthodox seeds, soil bacteria loss: `twistbioscience.com/blog/perspectives/what-if-synthetic-biology-was-available-to-martians-botanist-mark-watney`
- Hydrazine chemistry, first-attempt explosion: `sciencebuffs.org/2018/02/26/stranded-on-mars-the-science-behind-the-martian`
- Rover range (~35 km/charge) and Pathfinder battery cycle limit (~40): `planetary.org`, NASA MER reporting
- Weir on using only his own waste to limit pathogens: `modernfarmer.com/2015/10/can-you-grow-plants-on-mars`
- Mars physical constants: NASA NSSDC Mars Fact Sheet
