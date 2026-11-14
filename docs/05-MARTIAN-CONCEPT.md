# 05 — Concept Proposal: Crewed Mars Contingency Scenario
### (inspired by *The Martian* — read the IP section before agreeing)

Status: **proposal, not committed design.** Needs @tranminhngoc171-bot's sign-off before any data changes.

---

## TL;DR

*The Martian* is a **great source of theme and tone, and a bad source of names.** Do not title the game after the film, do not use Mark Watney / Hermes / Ares III / Project Elrond. What we *can* take — and what is genuinely valuable — is the **narrative frame** and the **humanist thesis**, plus one mechanic that is unusual enough to earn Creativity points:

> **The objective function changes mid-mission.** The player designs a science mission. Then it becomes a rescue mission. Everything they optimised for is now the wrong thing to optimise for.

That single twist is the whole pitch. It is cheap to build on top of our existing engine, it directly answers "why does this game teach something a textbook doesn't," and it gives us the humanist message Ngọc asked for **without inventing one**.

---

## 1. What we may and may not use (IP — read this first)

| Item | Safe? | Why |
|---|---|---|
| The title "The Martian" | **No** | Trademark/title of a copyrighted novel (Andy Weir, 2011) and film (20th Century Fox / Disney, 2015) |
| Characters: Mark Watney, Melissa Lewis, Rich Purnell, Mindy Park | **No** | Copyrighted characters |
| Names: *Hermes*, *Ares III*, *Project Elrond*, "Rich Purnell Maneuver" | **No** | Fictional proper nouns from the work |
| Dialogue lines ("I'm gonna have to science the shit out of this") | **No** | Copyrighted text |
| **The premise** "an astronaut is stranded and must be rescued" | **Yes** | A generic, uncopyrightable idea — dozens of works share it |
| **The theme** "no one is left behind", "one life is worth the cost" | **Yes** | Values are not copyrightable |
| **The science** Mars facts, solar irradiance, transfer windows, ISRU | **Yes** | Facts, and free to use with a NASA data citation |
| **Acknowledging the inspiration in our docs** | **Yes, and recommended** | "Inspired by the themes of *The Martian*" is normal, legal, and honest |

**Practical rule:** the word "Martian" may appear in our *research notes* and in a *design rationale document* (like this one). It must **not** appear in the game UI, the game title, the project name on the Space Apps submission, or the demo video. A NASA-branded hackathon submission that looks like it is trading on a Disney property is a needless risk, and it is the kind of thing a judge notices.

**Confirm:** the open textual homage. If we want a nod, it should be structural — a botanist crew member, a potato reference in an easter-egg tooltip — not a name lifted from the film.

---

## 2. Why this direction is strategically stronger than what we have now

Our current three scenarios (`climate_watch`, `disaster_response`, `space_weather`) are all **Earth-observation satellites**. They are well-built and the trade-offs are real, but:

- The 2026 hackathon theme is literally **"The Next Frontier"** — "propelling us to the Moon, Mars, and beyond."
- The challenge page's three focus areas are: **returning humans to the Moon**, **preparing for missions deeper into the solar system**, and **expanding understanding of the universe.**
- A satellite in SSO is none of those three. It is a good engineering exercise that reads as "generic space tech" to a judge who has read 40 other submissions about satellites.

A **crewed Mars mission** hits focus area #2 dead centre. It also makes the six resources *mean* something a satellite cannot: mass and power stop being spreadsheet numbers and become "can this crew survive."

| Criterion | Satellite scenarios | Crewed Mars scenario |
|---|---|---|
| **Relevance** | Partial (space, but not the stated focus areas) | Direct (focus area #2, named in the theme) |
| **Impact** | Taught a trade-off | Taught a trade-off *and* an ethical decision |
| **Creativity** | Solid dashboard | Rules that change mid-run — rare in this challenge |
| **Validity** | Good | Good, and grounded in NASA's own Artemis→Mars architecture |
| **Presentation** | One more satellite game | A story with a hook a judge remembers |

Recommendation: **keep the satellite scenarios** (they teach the engine and are already designed), and **add one crewed Mars scenario** as the centrepiece. The satellites become the tutorial; Mars becomes the demo.

---

## 3. The humanist message — and why it must come from the mechanics, not the text

Ngọc asked for a message that means something to a community. The temptation is to write a paragraph of uplifting copy. **That does not work in a game**, because players skip text and remember what the system made them *feel*.

*The Martian*'s actual thesis, stated plainly: **a person is worth more than the mission.** The film dramatises it three ways — NASA burns hundreds of millions to recover one man; the crew mutinies against direct orders to turn back; a rival space agency hands over a classified booster it did not have to reveal.

We can encode exactly that as a rule:

> At the halfway point of the run, a resource that was **not** in the objective function becomes the only thing that matters: **crew survivability**.

Design consequences:

- A player who spent the whole design phase maxing science value and shaving margins now has to discover that **the margin they removed was the thing that would have saved the crew.**
- The debrief no longer says "you failed the science target." It says "the crew survived because you bought the 15 % mass margin at the cost of one instrument — that was the right call, and it cost you 8 points of science."
- The lesson is not "be nice." It is **"design for the contingency you are not being paid to design for."** That is a real engineering ethics lesson and it is *exactly* what The Martian is about.

Three sentences we may actually use in the UI (our own words, no lifted dialogue):

> "The mission was built to return data. It will now be judged on whether it returns people."
> "Every kilogram of margin you removed was a decision you made on behalf of someone else."
> "There is no perfect design. There is only the cost you chose to accept."

---

## 4. Concrete scenario spec

```jsonc
{
  "id": "mars_crew_contingency",
  "name": "Ares Surface Contingency",   // fictional but generic — no franchise nouns
  "difficulty": "advanced",
  "budget_musd": 900.0,
  "duration_months": 30,
  ...
}
```

### Phase structure (extends our existing 4-phase simulation)

| Phase | Player does | Resources in play |
|---|---|---|
| 1. **Design** | Bus, power (solar vs. RTG), ISRU plant, ascent vehicle, comms, crew supplies, instruments | Mass, Power, Budget |
| 2. **Transit** | Choose transfer window; pay for life support over 26 months | Time, Budget |
| 3. **Surface ops** | Run the science programme; consume consumables | Data, Comms, Time |
| 4. **⚠ CONTINGENCY** | A seeded event forces an unscheduled departure. Available mass/power is now the rescue budget. | **All six, and the objective flips** |

### The flip — how it works mechanically

At phase 4 the engine swaps the objective weights:

```js
// before
objectives: [science, revisit, lifetime, data_delivered]   // weights sum 1.0
// after
objectives: [crew_survival, contingency_margin, comm_uptime]
```

`crew_survival` is computed from the **margin the player left**, not from science. This is the entire point: the player's earlier optimisation is re-scored against a criterion they did not know about. Nothing needs to be rebuilt — `computeMission()` already returns `{resources, checks, objectives, score, analysis}`; we only need a second objective set and a phase flag.

### Real numbers to seed the data tables (all NASA-sourced, all citable)

| Quantity | Value | Use |
|---|---|---|
| Mars solar irradiance | 586 W/m² (43 % of Earth's 1361) | Solar array sizing — a Mars array needs **2.3×** the area of an Earth one for the same watts. A great, teachable constraint. |
| Mars surface gravity | 3.71 m/s² (0.379 g) | Ascent vehicle delta-v is lower than Earth's — an advantage to model |
| Mars synodic period | 779.94 days (~26 months) | The launch-window rule; miss it and Time budget explodes |
| Mars year | 686.98 days | Mission lifetime in sols, not Earth years |
| Mars sol | 24 h 39 m 36 s | Slightly longer day; affects power cycle count |

Source: NASA NSSDC Mars Fact Sheet — `nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html`. This is a **citable NASA data source**, which we need anyway for global-award eligibility.

---

## 5. Cost estimate against the 24-hour plan

This is the part that decides whether we do it — measure it honestly.

| Work item | Hours | Owner |
|---|---|---|
| Second objective set + phase flag in engine | 1.5 | Ngọc |
| Crewed-mission data tables (bus/instruments/ISRU/ascent) | 2.0 | Ngọc |
| Five new instruments + 2 events in JSON | 1.5 | either |
| Contingency screen (one layout, one transition animation) | 2.5 | Bersious |
| Debrief copy for the flipped objective | 1.5 | Bersious |
| Balance pass so it is winnable but tight | 2.0 | Ngọc |
| **Total** | **~11 h** | |

**But this only works if the satellite core is done first.** If we start Mars before `climate_watch` plays end-to-end, we will have two half-built things instead of one working game.

**Suggested sequencing:** build `climate_watch` fully → it becomes the template → the Mars scenario reuses the same UI shell with a different theme and one extra phase.

**Cut list for this feature, in order:**
1. ISRU plant (drop it, it is flavour, not mechanism)
2. Ascent vehicle as a separate component (fold into bus)
3. Transit phase animation (a static progress bar is fine)
4. The contingency *twist* itself — **last resort only.** Without the twist this is just another scenario and probably not worth the 11 hours.

---

## 6. Open questions for Ngọc

1. Do we accept the IP constraint (no franchise names anywhere in the shipped product)? I think we must.
2. Is a mid-run objective flip too clever for a judge who plays for 90 seconds? My answer: no, *if* the debrief spells out what happened. But it needs a strong 3-second transition.
3. Do we keep all three satellite scenarios, or cut to two satellites + Mars to save time?
4. Does the humanist framing risk reading as preachy? My rule: the UI states consequences, never morals. The moral is visible only in the numbers.

---

## 7. Decision log entry (to be added to docs/logs/decisions.md if approved)

```
CONCEPT — Crewed Mars contingency scenario proposed.
Rationale: current scenarios are Earth-observation and miss the 2026 theme
("The Next Frontier", focus area: deeper solar system missions). A crewed Mars
scenario with a mid-run objective flip adds Relevance + Creativity at ~11h cost.
IP: franchise names excluded from shipped product. Theme and premise only.
```

---

## Proposed README tagline (our words, no franchise reference)

> *Design a mission to Mars. Then discover the mission was never about the data.*
