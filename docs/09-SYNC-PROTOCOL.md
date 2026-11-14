# 09 — Sync Protocol (for humans *and* their agents)

**Why this file exists:** both of us work with an AI agent alongside us. An agent that holds work locally is invisible to the other person, and invisible work is how two parallel branches become one lost afternoon. This file is the rule both agents follow.

---

## 1. The one rule

> **Every change that exists gets pushed to GitHub before the work session ends.**
> Not "when it's working." Not "when it's pretty." **Before the session ends.**

If it is broken, push it anyway and say so in the devlog. A broken branch we can see is worth more than a perfect one we cannot.

---

## 2. Agent instructions — copy this to your agent

**For the agent working with @tranminhngoc171-bot** and **for the agent working with @bersious**, identically:

```
You are working in a shared repository with another person and another agent.

HARD RULES
1. Never hold commits locally. After every meaningful change (a file created,
   a file edited, a decision made), commit and push to your branch.
2. Never push to main. Use feat/, fix/, docs/, data/ branches and open a PR.
3. Before starting work: git pull origin main, then merge main into your branch.
4. Never force-push. Never rebase a branch you do not own.
5. Never edit a file outside your owner's lane without asking first (see §4).
6. When you make a decision that someone might later question, write it in
   docs/logs/decisions.md in the same commit.
7. When you finish a work block, append an entry to docs/logs/devlog.md.
8. If you are blocked, push what you have and write the blocker in the devlog.
   Do not sit on a half-finished change waiting to solve it.
```

---

## 3. Branch and PR discipline (condensed from CONTRIBUTING.md)

| Step | Command |
|---|---|
| Start | `git checkout main && git pull && git checkout -b feat/<thing>` |
| Work | commit often, push often — a WIP push is correct behaviour |
| Publish | `git push -u origin feat/<thing>` then open a PR |
| Review | the other person reads it. Review is a courtesy, not a gate |
| Merge | squash merge, delete the branch |
| If behind | `git checkout main && git pull`, then merge `main` into your branch. Never rebase a shared branch |

**PR titles:** prefix with `WIP:` if it is not ready. A WIP PR is better than silence.

---

## 4. Ownership lanes — do not cross without asking

This is the boundary that keeps the two of us from overwriting each other.

| Path | Owner | The other person may |
|---|---|---|
| `data/*.json` | **@tranminhngoc171-bot** | read freely; propose a change in an issue or PR comment, do not commit numbers |
| `src/engine.js`, `src/scoring.js` | **@tranminhngoc171-bot** | read; file a bug in the PR if the output shape is wrong |
| `src/index.html`, `src/ui.js`, `src/orbit.js`, `src/css/*` | **@bersious** | read; file a visual bug in the PR |
| `src/data.js` | **shared** | both may edit — it is the loader, not the numbers |
| `docs/*` | **shared** | both may write; add your name to the section |
| `docs/logs/*` | **shared** | append only, newest on top |
| `README.md` | **shared** | small edits fine; tell the other person if you rewrite a section |

**The reason for the lane on `data/`:** if both of us tune a number in the same hour, one of us silently loses the change. Numbers change by PR, with a line in `decisions.md` saying why.

---

## 5. Agent handoff — telling the other person what you are doing

Before a work block, one line in the PR description or a comment:

```
@other-person — taking src/ui.js for the next 2h (design screens + resource bars).
Not touching engine.js. Ping me if the contract needs to change.
```

After the block, one line in `docs/logs/devlog.md`:

```
## 2026-11-15 HH:MM — <what I did>
**Bersious**
- what changed
- what broke
- what is next
**Blockers**
- none / <specific>
```

This is not bureaucracy. It is the only thing that prevents two agents from solving the same problem twice, differently.

---

## 6. Interface freeze — the one thing that must not drift

The `computeMission()` contract in `src/README.md` is frozen once agreed. If it must change:

1. Post the proposed shape in the PR **before** writing the code.
2. Wait for the other person to say yes.
3. Change `src/README.md` in the same commit as the code.

Changing the contract silently is the single most expensive mistake available to us. It breaks the other person's work with no error message.

---

## 7. Deadline discipline

| Time to deadline | Mode |
|---|---|
| > 3 h | branches, PRs, review, normal rules |
| 3 h – 1 h | direct push to `main` allowed for **bug fixes only**; note it in devlog |
| < 1 h | anyone may push anything to `main`. Working beats tidy. Say what you did |
| After submission | nobody touches `main`. Tag it `v1.0-submitted` so the exact submitted code exists forever |

**Tag the submitted state.** If a judge asks what we shipped, the tag is the answer.

---

## 8. What to do when it breaks

| Situation | Do this |
|---|---|
| Merge conflict in `data/*.json` | Do not hand-resolve silently. Look at both values, pick one, record why in `decisions.md` |
| `main` is broken | Whoever broke it fixes it, immediately, before any new feature work. This outranks everything |
| Two agents edited the same file | Stop. The file's owner decides. The other person's change goes into a follow-up PR |
| Someone pushes junk | Revert with a commit (`git revert`), do not rewrite history |
| Laptop dies mid-hackathon | Everything that mattered was pushed. That is the point of §1 |

---

## 9. Status board (keep this current — it is the shared source of truth)

| Area | Owner | State | Blocked by |
|---|---|---|---|
| `data/*.json` | Ngọc | v0.1 done — 12 instruments, 3 buses, 4 orbits, 5 launchers, 7 events, 3 scenarios | — |
| `src/engine.js` | Ngọc | not started | needs framework decision |
| `src/scoring.js` | Ngọc | not started | engine |
| `src/index.html` + `ui.js` | Bersious | not started | needs framework decision |
| Mars two-act concept | both | proposed, awaiting decision — PR #1 | Ngọc's call |
| Submission docs / video | Bersious | not started | running game |

Update your row when you finish something. A stale status board is worse than none, because people trust it.
