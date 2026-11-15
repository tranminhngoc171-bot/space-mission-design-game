# 08 — Framework & File Structure Decision

**Status:** decided by @bersious, open to objection from @tranminhngoc171-bot. Say so in this PR if you disagree and we revert before any code depends on it.

---

## 1. The decision

> **Plain HTML + CSS + JavaScript ES modules. No framework. No build step. SVG for anything drawn.**

Deployment target: **GitHub Pages**, direct from the repo. No bundler, no `node_modules`, no transpile.

---

## 2. Why, in one paragraph each

**No build step.** In a 24-hour event with two people and two agents, every minute spent waiting for an install or a compile is a minute not spent on the demo. Editing a file and reloading the page is the shortest possible loop. It also means a broken `package.json` cannot take the project down at 2 a.m.

**Deployment is a switch, not a pipeline.** GitHub Pages serves this repo directly. No environment variables, no base-path configuration, no platform account. Judges get a URL, it works on a phone.

**The game is a control panel, not an action game.** Five choice screens, six resource bars, one debrief. There is no sprite loop, no physics, no per-frame rendering. Frameworks earn their keep on state-heavy component trees; this project has one state object and a handful of views. Plain JS handles that in a few hundred lines.

**Agents work better in plain files.** Both of us delegate to an AI agent. An agent reading and editing `ui.js` is reliable; an agent editing JSX inside a build pipeline with its own conventions is where silent breakage lives.

---

## 3. What we are deliberately refusing

| Rejected | Why |
|---|---|
| **React / Next.js** | Build step, deploy configuration, `package.json` merge conflicts between two devs. The component reuse it offers is not needed at this size. |
| **Vue / Svelte** | Same reasons, slightly lighter. Still a build. |
| **Phaser** | Built for sprite-based action games. We would spend hours fighting it to make a dashboard. Wrong tool. |
| **Godot / Unity → HTML5** | Export bundle is 20 MB+. A judge on mobile waits, or gives up. |
| **WebGL / Three.js** | Already ruled out in `decisions.md` — zero graded value, 10–16 h cost. |
| **Tailwind via CDN** | One more dependency to break, and it fights the hand-written Mission Control CSS. Hand-written CSS is ~400 lines and we control all of it. |

**Optional escape hatch:** if DOM manipulation becomes painful, add **Alpine.js via a single `<script>` tag**. That is still no-build and reversible in ten minutes. Do not add it preemptively.

---

## 4. The file structure

```
src/
├── index.html          page shell: topbar, step nav, stage, resource rail, footer
├── css/
│   └── mission.css     the entire visual system (dark Mission Control)
├── data.js             the ONLY file that fetches ../data/*.json
├── engine.js           ⚠ owned by Ngọc — pure computeMission(), no DOM
├── scoring.js          ⚠ owned by Ngọc — score + analysis generation
├── ui.js               renders engine output into the DOM, owns no math
└── orbit.js            SVG orbit + spacecraft schematic
```

**Rules that keep this structure honest:**

1. `data.js` contains **no numbers**. It loads and indexes. If you want to add a mass value there, it belongs in a JSON file instead.
2. `engine.js` and `scoring.js` **never touch the DOM**. They take a design object and return a result object.
3. `ui.js` **never computes a resource or a score**. It reads `result.resources[x].pct` and paints it.
4. Any JS file with a hard-coded kg, W, M$, GB or hour in it is a bug.

That division is what lets two people work in one day without blocking each other.

---

## 5. Gap in the data files (action needed from Ngọc)

`data/` currently has instruments, orbits, launch vehicles, events, scenarios. It does **not** have:

- `data/buses.json` — the design doc and `01-GAME-DESIGN.md` reference three buses (small / medium / large) with dry mass, cost, max instrument slots, overhead watts, battery capacity. These currently exist only in prose.
- `data/power.json` — solar array options vs. RTG, with mass, cost and generated watts.

**The UI cannot render the bus and power screens without these.** I have deliberately *not* invented them — inventing balance numbers is Ngọc's lane, and doing it silently would be exactly the failure mode §4 exists to prevent.

Suggested shape, for Ngọc to accept or amend:

```jsonc
// data/buses.json
{ "buses": [
  { "id": "small_bus", "name": "...", "dry_mass_kg": 0, "cost_musd": 0,
    "max_instruments": 0, "overhead_w": 0, "battery_wh": 0,
    "blurb": "...", "tradeoff": "..." }
]}

// data/power.json
{ "sources": [
  { "id": "solar_small", "name": "...", "mass_kg": 0, "cost_musd": 0,
    "gen_w": 0, "blurb": "...", "tradeoff": "..." }
]}
```

Until those land, `index.html` renders the instrument / orbit / launcher screens and shows a "data pending" placeholder on bus and power.

---

## 6. The dev-server trap everyone hits

`fetch('../data/instruments.json')` **fails when the page is opened as a `file://` URL.** The browser blocks it as a cross-origin request. The page will be blank and the console will say something about CORS or "Why does it say 0?".

Three ways to run it, pick one:

```bash
# 1. Python, one line, works anywhere
cd src && python -m http.server 8000
# → http://localhost:8000

# 2. npx, if Node is installed
npx serve src

# 3. VS Code live-server extension, right-click index.html → Open with Live Server
```

GitHub Pages is `http://`-served, so the deployed version never has this problem. Only local double-click does. **Do not "fix" it by inlining the JSON** — that would create a second copy of every number and violate rule 1.

---

## 7. If we are wrong

Reversing this decision costs about **2 hours**: the engine and data layers are framework-independent, so only `ui.js` would be rewritten as components. That is an acceptable risk to carry, and it is why the decision is recorded here rather than left implicit.

What is *not* acceptable is starting on React "just in case" and ending up with neither. Pick one, finish the demo.
