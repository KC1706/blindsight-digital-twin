# Blindsight — team working agreement (read me first)

This file is auto-loaded by Claude Code for everyone in the repo. It defines **how we work**.
For *what* we're building, see [`README.md`](README.md), [`PLAN.md`](PLAN.md), and
[`docs/METHODS.md`](docs/METHODS.md).

## The team: three roles, three deliverables

Round 2 asks for three things. One person owns each.

| Role | Owns (Round 2 deliverable) | Guide | Label | Milestone |
|---|---|---|---|---|
| **Development** | Working Prototype | [`roles/DEVELOPMENT.md`](roles/DEVELOPMENT.md) | `role:dev` | M0–M8 |
| **Business Analysis** | Detailed Business Proposal | [`roles/BUSINESS_ANALYSIS.md`](roles/BUSINESS_ANALYSIS.md) | `role:ba` | `Deliverable · Business Proposal` |
| **Presentation** | Pitch Presentation | [`roles/PRESENTATION.md`](roles/PRESENTATION.md) | `role:deck` | `Deliverable · Pitch Presentation` |

**Start of every session:** open your role guide, then filter the board to your label.

## The board

GitHub **Issues + Milestones** (+ a Projects v2 "By Role" view) is the single source of truth.
Every issue carries four labels: `role:*` · `area:*` · `type:*` · `priority:*` (+ `size:*`).

- Board: https://github.com/KC1706/blindsight-digital-twin/issues
- Your work = `label:role:<you>`. Sort by priority (below), pull from the top.

## Priority order (always)

Work **p0 → p1 → p2**. Never start a p2 while a p0 in your lane is unstarted.

- `priority:p0-critical` — the demo/pitch fails without it. This is the critical path.
- `priority:p1-high` — makes the pitch *win*, not merely *run*.
- `priority:p2-normal` — polish.

## Branching & PRs (trunk-based, one branch per issue)

We do **not** keep a long-lived branch per role. One short-lived branch per issue:

```
<role>/<issue#>-<short-slug>
  dev/34-ocba-lever-ranking
  ba/43-roi-model
  deck/50-line-is-sensor-visual
```

1. `git switch -c <role>/<issue#>-<slug>` off latest `main`.
2. Commit small; reference the issue (`#34`) in messages.
3. Open a PR into `main`; keep it small; get one review; squash-merge.
4. Delete the branch. Move the issue to Done.

**`main` is protected** (PR + 1 approval). Keep branches short-lived (< ~2 days) so nobody
drifts far from trunk.

## Working across roles (encouraged when it unblocks the team)

Your prefix shows your focus, but anyone can pick up any issue:

- Assign yourself the issue and branch with **that issue's role prefix** (e.g. a Dev helping
  the deck uses `deck/…`). The prefix follows the *work*, not the person.
- Respect the owner: comment on the issue first so two people don't collide.
- When you touch another role's area, follow **that role's guide** for its conventions.

## Definition of Done (every issue)

- [ ] The issue's own "Definition of Done" checkboxes are all ticked.
- [ ] PR merged to `main`; branch deleted.
- [ ] If it changes behaviour: a test (Dev) or a reviewed artifact (BA/Deck) exists.
- [ ] Handoffs noted on the issue (e.g. "ROI numbers ready for deck #54").

## Cadence

- Short daily sync: each person names their current p0 and any blocker.
- The seam between roles is explicit: `api/schemas.py` (Dev↔Dev), ROI/validation numbers
  (BA/Dev → Deck). Agree these shapes early so nobody waits.
