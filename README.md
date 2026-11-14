# Space Mission Design Game 🚀

> Interactive game where players design, manage and simulate a complete space mission — and learn why every engineering decision costs something.

**NASA Space Apps Challenge 2026** · Challenge: [Space Mission Design Game](https://www.spaceappschallenge.org/2026/challenges/space-mission-design-game/) · Difficulty: Intermediate

---

## Team

| GitHub | Role |
|---|---|
| [@tranminhngoc171-bot](https://github.com/tranminhngoc171-bot) | Game logic · simulation engine · scoring |
| [@bersious](https://github.com/bersious) | UI · mission control dashboard · visualisation |

Both have **write access** — branch freely, open PRs, review each other.

---

## What we are building

A browser game in the **Mission Control** aesthetic (dark telemetry panels, SVG spacecraft schematic, animated orbit). No 3D, no WebGL — the points are in the *trade-offs*, not the polygons.

```
Mission Objective → Requirements → Design (bus + instruments + orbit + launcher)
        ↓                                              ↓
    Debrief ← Simulation (phases, events, scoring) ← Compatibility checks
```

**The core loop:** allocate six resources → simulate → hit a random event → see exactly *why* it failed → redesign. That loop is the educational product.

### The six resources

| Resource | Meaning | Fails when |
|---|---|---|
| **Mass** | bus + instruments + propellant | > launch vehicle capacity |
| **Power** | generation vs. draw | draw > generation + battery buffer |
| **Budget** | development + launch + operations | > mission budget |
| **Data** | generated per day by instruments | > downlink capacity |
| **Comms** | downlink capacity vs. orbit windows | data backlog grows |
| **Time** | mission lifetime vs. objectives needed | objectives unmet at end |

---

## Repo layout

```
docs/               design + analysis documents (start here)
  logs/             shared devlog & decision records
data/               balance tables as JSON — the source of truth for all numbers
src/                game code
assets/images/      screenshots, diagrams, submission assets
notes/              scratch research, links, NASA data notes
```

## Built on NASA's own mission-design method

We did not invent the workflow — we playtested NASA's. Three agency sources shape the design, and the submission cites them:

| NASA source | What we took from it |
|---|---|
| [Design and Develop Science Missions](https://www.nasa.gov/wp-content/uploads/2025/04/250323-design-and-develop-science-mission.pdf) | The **four mission segments** (launch / space / ground / user) — the check that told us our six resources were the right six |
| [Mission Design Lab](https://etd.gsfc.nasa.gov/capabilities/integrated-design-center/mission-design-lab/) (Goddard) | Our screen order: Office Hours → Concept Development → Trade Studies → Point Design |
| [Concept Maturity Levels](https://dataverse.jpl.nasa.gov/dataset.xhtml?persistentId=hdl:2014/44299) (JPL) | Why our three scenarios differ: difficulty is *less freedom*, not bigger numbers |

Benchmarked against NASA's own [Webb telescope design game](https://science.nasa.gov/mission/webb/game-build-it-yourself/) — we take its ending (name what the player really designed) and skip its cutscene.

Full analysis, including what we deliberately do **not** model: `docs/08-RESEARCH-SOURCES.md`.


## Start here

1. `docs/00-CHALLENGE-BRIEF.md` — what is actually graded
2. `docs/04-PLAN-24H.md` — who builds what, hour by hour
3. `data/*.json` — the numbers (instruments, orbits, launchers, events, scenarios)
4. `docs/03-SCORING.md` — how a mission is scored
5. `docs/08-RESEARCH-SOURCES.md` — which NASA sources we used and what we deliberately left out

## How we work

- `main` is protected by convention: nobody pushes straight to it, use `feat/...` or `fix/...` branches + PR.
- Commit style: `feat:`, `fix:`, `docs:`, `data:`, `chore:`.
- Every design number change goes in `data/*.json` **and** gets a line in `docs/logs/decisions.md`.
- Work log goes in `docs/logs/devlog.md` (append, newest on top).
- Screenshots/diagrams: `assets/images/<topic>-<date>.png`.

See `CONTRIBUTING.md`.

## License

MIT (see `LICENSE`).
