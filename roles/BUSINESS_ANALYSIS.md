# Role guide — Business Analysis 📊

**You own:** the Detailed Business Proposal. **Label:** `role:ba`.
**Milestone:** `Deliverable · Business Proposal`.
**Read first:** [`CLAUDE.md`](../CLAUDE.md), [`docs/BUSINESS_PROPOSAL.md`](../docs/BUSINESS_PROPOSAL.md)
(your master doc), [`docs/ASSUMPTIONS.md`](../docs/ASSUMPTIONS.md).

## Mission

Make the case that Blindsight is worth building and buying: frame the problem in money,
quantify the value, define who it's for, and lay out a credible path to scale — all traceable
to stated assumptions, not vibes.

## Your board (priority order)

Filter: `label:role:ba`. Suggested sequence:

1. **#42 Cost-of-line-blindness model** (p0) — the baseline losses everything else builds on.
2. **#43 ROI / business-case model** (p0) — depends on #42; the number that wins the pitch.
3. **#41 Market & competitor landscape** (p1) — where we differentiate.
4. **#44 Personas & JTBD** (p1) — feeds the 3 dashboard views.
5. **#46 GTM roadmap** (p1) — PoC → pilot → scale with gates.
6. **#47 Risk, compliance & OT-security** (p1) — extends ASSUMPTIONS into a risk register.
7. **#40 Pilot KPIs & success criteria** (p1) — ties value to what the prototype measures.
8. **#45 Pricing & commercial model** (p2).
9. **#24 Author `docs/BUSINESS_PROPOSAL.md`** — integrate all of the above into the deliverable.

## Working files

`docs/BUSINESS_PROPOSAL.md` (your master), `docs/ASSUMPTIONS.md` (shared — coordinate edits),
plus any models under `docs/` (e.g. a `docs/roi_model.*`). You rarely touch code → few conflicts.

## Conventions

- **State every assumption** and cite it (the brief demands this). Keep numbers in one model
  so the deck can quote them without re-deriving.
- Branch `ba/<issue#>-<slug>`; PR docs into `main` like code (gives a review trail).
- Prefer parameterized models (a sheet/notebook) over hard-coded figures.

## Handoffs

- **← Development:** which value metrics the prototype can measure (#40 ↔ #17,#35); the
  leadership view (#22) will render your ROI.
- **→ Presentation:** ROI (#43), GTM/roadmap (#46), personas (#44) feed the business-case
  slides (#54) and the "ask." Hand over final numbers, not drafts.
