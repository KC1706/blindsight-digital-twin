# Role guide — Presentation 🎤

**You own:** the Pitch Presentation. **Label:** `role:deck`.
**Milestone:** `Deliverable · Pitch Presentation`.
**Read first:** [`CLAUDE.md`](../CLAUDE.md), [`docs/DEMO_SCRIPT.md`](../docs/DEMO_SCRIPT.md),
and the Round 1 narrative (`../video-script.md`, `../vo-script-clean.md`) — reuse its voice.

## Mission

Tell the Blindsight story so it lands in minutes: the blind line, the insight ("the line is
the sensor"), the working prototype, the proof it can be trusted, and the business case — then
the ask. The demo is the centerpiece; the deck frames it.

## Your board (priority order)

Filter: `label:role:deck`. Suggested sequence:

1. **#48 Deck outline & narrative arc** (p0) — lock the spine first; everything hangs off it.
2. **#50 "The line is the sensor" explainer visual** (p0) — the one visual that must land.
3. **#53 Live-demo integration + fallback video** (p0) — never let a live failure kill the pitch.
4. **#52 Results & validation slides** (p0) — the proof; depends on Dev's validation (#15,#35).
5. **#49 Slide design system** (p1) — brand/template so slides look like one deck.
6. **#51 Architecture / how-it-works diagram** (p1).
7. **#54 Business-case slides** (p1) — from BA's ROI (#43) / roadmap (#46).
8. **#55 Rehearsal, timing & speaker script** (p1).
9. **#56 Q&A / judge-question prep** (p2).

## Working files

A `deck/` folder (create it): `deck/outline.md`, exported slides, `deck/assets/` (diagrams,
recordings), `deck/speaker-notes.md`, `deck/qa.md`. Reuse `../blindsight-animation.html`.

## Conventions

- **One narrative, one voice** (see Round 1 scripts) — factual, not hyped; let the facts be
  the drama.
- Every proof slide traces to something real in the repo (a metric, a scenario, a doc).
- Branch `deck/<issue#>-<slug>`; commit assets/notes; PR into `main`.
- Keep a **fallback recording** of every demo scenario checked in and tested offline.

## Handoffs

- **← Development:** validation metrics (#15,#35) → #52; architecture (PLAN §4) → #51; stable
  demo build + scenarios (#23) → #53. Ask Dev for a frozen demo build before recording.
- **← Business Analysis:** ROI (#43), roadmap (#46), personas (#44) → #54 and the ask.
- Coordinate timing with everyone: the deck's job is to fit the mechanism into the time limit.
