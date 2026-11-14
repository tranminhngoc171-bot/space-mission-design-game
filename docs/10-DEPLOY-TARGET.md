# 10 — Deployment Target: `bersious.io.vn/nasa`

**Status:** decided. This overrides nothing in doc 08 (the framework decision stands) — it only answers *where the built game is served from*.

---

## 1. The decision

> **The playable game is served at `https://bersious.io.vn/nasa`.**
> `~/bersious-web` (repo `bersious/bersious-web`, Vercel project `bersious-web`) is the **deployment host**.
> `space-mission-design-game` remains the **source of truth** for code and numbers.

The team repo is where we work. `bersious-web` is where it ships.

---

## 2. Why not GitHub Pages on the team repo

GitHub Pages on `tranminhngoc171-bot/space-mission-design-game` would give
`tranminhngoc171-bot.github.io/space-mission-design-game` — a URL with someone else's handle in it and a repository name that has nothing to do with the project. Judges see that link.

`bersious.io.vn/nasa` is short, has our own domain, deploys in 5–10 s on every push, and sits next to the other hackathon projects on the homepage. Doc 08 already said "deploy to GitHub Pages"; this document replaces that specific detail with the better host. **The no-build-step rule is unchanged.**

---

## 3. File layout — what lands where

`~/bersious-web/nasa/` mirrors `src/` plus a copy of `data/`:

| Team repo | Deployed at |
|---|---|
| `src/index.html` | `nasa/index.html` |
| `src/css/mission.css` | `nasa/css/mission.css` |
| `src/data.js`, `engine.js`, `scoring.js`, `ui.js`, `orbit.js` | `nasa/*.js` (flat, same level as `index.html`) |
| `data/*.json` | `nasa/data/*.json` |

**Why `data/` moves:** `src/data.js` currently fetches `../data/*.json`, which is correct inside the team repo (`src/` is one level below `data/`). Deployed, `nasa/index.html` is the root — `../data/` would point at `/data/`, which does not exist.

**Fix (already applied in the team repo):** `data.js` tries both bases and uses whichever answers. Two lines, no configuration, works in both places:

```js
const BASES = ['../data/', 'data/'];   // team repo first, deployed copy second
```

Do not "simplify" this to a single path — that breaks one of the two environments.

---

## 4. The sync step — the only manually-run command

```bash
bash scripts/sync-to-web.sh
```

That script (in `scripts/sync-to-web.sh`) does exactly this and nothing else:

```
team-repo/src/*      →  ~/bersious-web/nasa/       (index.html, css/, *.js)
team-repo/data/*     →  ~/bersious-web/nasa/data/
```

It uses `rsync --delete` on the *copied* files so a deleted source file disappears from the deployment too — drift in that direction is impossible. It then prints what changed so you can eyeball it before committing.

**Why a copy and not a submodule or a symlink:** a git submodule would make Vercel's build fragile (submodule cloning is not guaranteed for every project configuration), and a symlink does not survive a Windows checkout. A visible `rsync` is boring, and boring is correct here.

---

## 5. The one risk this creates, and how we contain it

**Numbers now exist in two places.** `data/*.json` lives in the team repo (source of truth) and is copied into `bersious-web/nasa/data/` (the served copy). If someone edits the served copy directly, the two drift and nobody notices until the demo shows a number that no longer matches the balance table.

Three rules, all cheap:

1. **Never edit anything inside `~/bersious-web/nasa/` by hand.** It is generated. Edit the team repo, then run the sync.
2. `~/bersious-web/nasa/GENERATED.md` is written by the sync script and names the commit it came from. If that commit does not match `git -C team-repo rev-parse --short HEAD`, the deployment is stale.
3. `scripts/sync-to-web.sh --check` compares hashes and exits non-zero if the deployment is out of date. Run it before any submission push.

---

## 6. Vercel configuration — do not repeat a known outage

`~/bersious-web/vercel.json` must stay minimal:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "cleanUrls": true,
  "trailingSlash": false
}
```

Plus only the `headers` blocks that already exist. **Do not add a `rewrites` entry for `/nasa`.**

This exact mistake broke the site on 2026-10-19: a leftover `rewrite` for `/tmn → /project.html` survived a migration to a subdirectory and caused `DEPLOYMENT_NOT_FOUND` across the whole site at midnight. A directory `nasa/index.html` is served automatically by `cleanUrls` — a rewrite pointing at a file that does not exist is not "extra safety", it is an outage waiting for a pushed commit.

---

## 7. Verification — after every deploy

```bash
for u in / /nasa /tmn /rmit /aeterna; do
  printf "%-10s " "$u"; curl -s -o /dev/null -w "%{http_code}\n" -m 15 "https://bersious.io.vn$u"
done
```

All five must return `200`. A `404` or `5xx` anywhere means `vercel.json` needs looking at, not the code.

Also verify the new page did not inherit a stale theme colour: the mobile browser bar must be `#06090f` on `/nasa` and stay dark, not fall back to the pink theme used by the gift page.

---

## 8. Current state of `/nasa` (honest)

Right now `bersious.io.vn/nasa` serves a **project brief page** — what the game is, the six resources, how a run works, team credits, and a "building" banner. It is a placeholder that a judge can read and understand.

When the game is playable, `nasa/index.html` is replaced by `src/index.html` from the sync. The brief content should not be thrown away — it becomes the intro screen inside the game, or moves to `nasa/about.html`. Decide when we get there.

---

## 9. Who does what

| Step | Owner |
|---|---|
| Write game code in `src/` | both (lanes per doc 09) |
| Run `scripts/sync-to-web.sh` | whoever is deploying — usually @bersious |
| Commit + push `bersious-web` | @bersious (it is his repo and his domain) |
| Verify the five URLs return 200 | whoever pushed |
| Report the live link in the devlog | whoever pushed |

**@tranminhngoc171-bot does not need access to `bersious-web`.** The push is the deployment; code review happens in the team repo before it ever reaches the web.

---

## 10. Submission detail that follows from this

The Space Apps project page requires a **public demo link**. That link is:

```
https://bersious.io.vn/nasa
```

It must open on a phone without login, without a download, and without a blank screen. That is the acceptance test, and it is why the deployed-copy sync is a pre-submission step (`--check`) rather than an afterthought.
