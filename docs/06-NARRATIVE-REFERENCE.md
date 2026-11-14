# 06 — Narrative Reference: Plot Structure of *The Martian*
### Research notes for the crewed Mars scenario. **Not a spec — a source of mechanics.**

> IP reminder: nothing in this document may be lifted into the shipped product. See `05-MARTIAN-CONCEPT.md` §1.
> What we take is **structure**, not text.

---

## 1. The plot, reduced to its load-bearing beats

The film runs on a single engine: **every solution creates the next crisis.** Watney solves food, and the solution is what nearly kills him twice. NASA solves comms, and the rescue attempt built on it collapses on the launch pad. Track it as a chain:

| # | Beat | What solves it | What it *breaks* next |
|---|---|---|---|
| 0 | Dust storm forces abort on sol 18; Watney struck by debris, presumed dead | Crew evacuates — the only survivable choice | He is alone, with no comms and 4 years until the next mission |
| 1 | He wakes. Food for ~300 sols, needs ~900 | Grows potatoes: bio-waste + Martian soil, water cracked from hydrazine | Hydrazine reaction nearly kills him (hydrogen explosion). Crop becomes a single point of failure |
| 2 | No way to talk to Earth | Treks to recover the *Pathfinder* probe, links it to the rover | Earth now knows he lives — which forces NASA into decisions it cannot win |
| 3 | Airlock breaches, decompression destroys the potato crop | Repairs the airlock | **The food clock restarts with no solution.** This is the true midpoint |
| 4 | Starvation in ~200 sols | NASA builds a resupply probe in a hurry, skipping inspections | **The probe disintegrates on launch.** The hurry *is* the failure |
| 5 | No booster left | CNSA offers its *Taiyang Shen* launcher | Two mutually exclusive plans now compete for it |
| 6 | Which plan? | Plan A (Iris 2): resupply Watney directly — risks 1 life. Plan B (Purnell): slingshot the crew's ship back — risks 6 lives | NASA's director picks the lower-risk plan. Flight director leaks Plan B to the crew |
| 7 | The crew decides | Unanimous vote to defy orders and turn back | NASA is now publicly committed to a mission it opposed |
| 8 | Watney must reach the orbiting ship | Trek to the pre-positioned ascent vehicle; strip it to shed mass | Launch leaves him short and too fast |
| 9 | Closing the gap | Commander blows the airlock for thrust | Still short. Watney punctures his suit to fly on escaping air |
| 10 | Rescue | — | Epilogue: he becomes a survival instructor |

**The structural insight:** the film is not "one problem, solved heroically." It is **eleven problems in series, where the fix for problem *n* is the cause of problem *n+1*.** That is a level-design template, not a plot.

---

## 2. Four mechanics we can actually steal

### 2.1 Chained crises (the backbone)

Each game phase should **close on the consequence of the player's own success**, not on a random penalty. Stealing the pattern:

> `crisis → what you have left → improvised fix → that fix consumes a resource → new crisis`

Our engine already models six resources. What it lacks is **causality between phases**. Instead of "a dust storm happened," the event should fire *because* of a design decision. Example: skip the mass margin to carry one extra instrument → the ascent vehicle is now too heavy → you must strip something in a hurry → stripping the cockpit removes the backup comms → the final rendezvous has no telemetry.

That last link is a real teaching moment, and it is cheap to implement: our `analysis[]` array can carry a `caused_by` field pointing at the earlier decision.

### 2.2 The asymmetric-risk decision (beat 6)

This is the best single decision in the film and the strongest candidate for a dedicated screen.

| Plan | Saves | Puts at risk | Cost |
|---|---|---|---|
| Iris 2 — resupply the stranded astronaut | 1 | 1 | Reliable, slow |
| Purnell — divert the crewed ship back | 1 | 6 | Elegant, fragile |

**Neither is wrong.** The film makes the "safe" choice the *arguably wrong* one, then has a subordinate leak the "reckless" plan because he believes it is right. That is a decision with no correct answer and no numerical optimum — exactly what makes a game interesting, and exactly the kind of thing that earns **Creativity** and **Impact**.

Mechanically this is trivial to build: two buttons, two different risk vectors, two different debriefs. The scoring engine does not need to know which is "right."

### 2.3 The margin that was cut

The film's engineering lesson, stated in our words: **the reserve you deleted to hit a target is the reserve that saves you.**

This is already the spine of `05-MARTIAN-CONCEPT.md` §3. Worth restating here because the film demonstrates it three separate times: the mass left off the ascent vehicle, the inspection skipped to launch on time, the backup comms removed to make room.

### 2.4 The mutiny (beat 7) — optional, but it is the humanist payload

A crew that disobeys a direct order because they judge the order wrong. This maps *directly* onto our **hot-seat 4-role mode**: four roles, one shared resource pool, and a moment where the Mission Director's decision can be overruled by the other three. The coordination penalty becomes a coordination *choice*.

---

## 3. What the film gets right scientifically (and what we should copy exactly)

From the film's science, these are usable and citable:

| Fact | Value | Where it bites in our game |
|---|---|---|
| Mars solar irradiance | 586 W/m² (43 % of Earth) | A solar array on Mars needs **2.3×** the area for the same watts — brutal, teachable mass cost |
| Mars surface gravity | 3.71 m/s² (0.379 g) | Ascent is *cheaper* than from Earth. A genuine advantage to model, not a penalty |
| Earth–Mars synodic period | 779.94 days (~26 months) | The launch window. Miss it and the Time resource explodes |
| Mars sol | 24 h 39 m 36 s | Slightly longer day; power cycles run on a 24.66 h clock |
| Mars year | 686.98 days | Mission lifetime is stated in sols, not Earth years |
| Comms light-time delay | ~4–24 min one way | Ground cannot help in real time. Justifies why the crew decides alone |

Source: NASA NSSDC Mars Fact Sheet.

**One deliberate inaccuracy worth knowing:** the film's opening dust storm is scientifically overstated — real Martian atmospheric density is ~0.6 % of Earth's, so even a violent storm cannot generate the forces the film shows. Andy Weir has acknowledged he took the liberty for narrative reasons. We should **not** model that storm as a physics event; use it as a *narrative* trigger only, or pick a physically honest crisis (a seal failure, a resupply loss, a window slip).

---

## 4. Proposed mission arc for `mars_crew_contingency`

Ten beats, each one screen or one event, each closing on the next problem:

```
1. BRIEF       You are designing a 30-month crewed Mars surface mission.
               Objective: maximise science return within budget.

2. DESIGN      Bus / power (solar 2.3× area vs RTG) / ISRU / ascent vehicle /
               comms / supplies / instruments.  Six resource bars live.

3. TRANSIT     26-month window. Life support burns budget and consumables.

4. SURFACE     Science programme runs. Data accumulates. Downlink is the bottleneck.
               Player is winning. Score is climbing.

5. ⚠ EVENT      A contingency forces an early, unplanned departure.
               Objective function is replaced. Science no longer matters.

6. THE CHOICE  Two mutually exclusive recovery plans, asymmetric risk.
               (This is beat 6 of the film, abstracted.)

7. THE CUT     You are now short on mass/power/time. Strip the design
               to make it fly — and lose whatever you strip.

8. THE RUN     Final manoeuvre. Seeded events test what you kept.

9. DEBRIEF     Scored on crew survival AND re-scored on the design
               decisions you made before you knew they mattered.

10. THE LESSON One line. Numbers only, no sermon.
```

The whole arc is ~11 h of work on top of the existing engine, per the estimate in doc 05.

---

## 5. The humanist message, in one table

Ngọc asked for a message worth giving a community. The film gives us one that is not sentimental, and is therefore usable:

| The film says | The game makes the player feel |
|---|---|
| A person is worth more than the mission | The margin you cut was somebody's oxygen |
| Nobody survives alone — a botanist survives because a satellite planner noticed a dot moving | Every role in your 4-person team matters, even the one that looks like admin |
| Institutions can be wrong, and individuals inside them can be right | The "safe" option is sometimes the wrong one, and you must defend your choice |
| Ingenuity is a moral act, not just a technical one | Fixing the problem *is* the care |

We state these as **consequences in the debrief**, never as text on a splash screen. A player who is told they were brave learns nothing. A player who is shown the exact kilogram that would have saved the crew learns it permanently.

---

## 6. One line we could use as the game's epigraph

Our own words, no franchise reference:

> *Every kilogram you left out was a decision made on behalf of someone else.*

---

## 7. Sources

- Plot and production: `en.wikipedia.org/wiki/The_Martian_(film)` — Wikipedia, Good Article
- Character-level divergences between novel and film: LitCharts summary, `litcharts.com/lit/the-martian/summary`
- Trajectory analysis of the rescue manoeuvre by NASA's own Mission Architecture branch: `ntrs.nasa.gov/api/citations/20150019662` — a real NASA technical paper on the film's orbital mechanics, worth citing in our submission
- Mars physical constants: NASA NSSDC Mars Fact Sheet, `nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html`
- NASA's involvement in the film (for context on why this premise reads as credible to a NASA judge): Wikipedia §"NASA involvement"
