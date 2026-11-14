# Contributing — 2-dev protocol

## Branches
- `main` — always runnable. No direct pushes.
- `feat/<name>` — new feature (e.g. `feat/sim-engine`, `feat/dashboard`)
- `fix/<name>` — bug fix
- `docs/<name>` — docs only
- `data/<name>` — balance table changes

## PR rules (both of us)
1. PRs are small — one feature or one doc each.
2. The other person reviews before merge. If urgent (< 1h to deadline), self-merge but note it in devlog.
3. Merge with **squash** to keep history readable.
4. Never rebase someone else's branch without asking.

## Commit style
`type: short summary` — types: `feat`, `fix`, `docs`, `data`, `chore`, `art`.
Example: `data: nerf SAR power draw 180W -> 150W (budget pressure test)`

## Where things go
| Thing | Location |
|---|---|
| Design numbers (single source of truth) | `data/*.json` |
| Rationale for a number change | `docs/logs/decisions.md` |
| "What I did today" | `docs/logs/devlog.md` (append on top) |
| Scratch research / links | `notes/` |
| Screenshots, diagrams, submission assets | `assets/images/` |

## Sync rule
Before starting work: `git pull origin main`. Before ending a session: push your branch even if unfinished (prefix WIP in PR title) — the other person must see progress.
