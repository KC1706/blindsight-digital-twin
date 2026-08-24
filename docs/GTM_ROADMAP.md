# Phased Go-to-Market Roadmap

**Issue:** #46 · **Matches phasing in:** [`PLAN.md`](../PLAN.md) §1 (PoC → real integration is
explicitly out of scope for this round) and [`BUSINESS_PROPOSAL.md`](BUSINESS_PROPOSAL.md) §5 ·
**Feeds:** [`ROI_MODEL.md`](ROI_MODEL.md) §5 (multi-line scale-out pacing), business-case
slides (#54).

Three phases, each with an entry gate (what must be true to start) and an exit gate (what must
be true to advance). No phase starts before the prior one's exit criteria are met — this is a
credibility mechanism, not bureaucracy: it's the answer to "how do we know you won't overpromise
at scale."

## Phase 1 — PoC (this prototype)

| | |
|---|---|
| **Scope** | One simulated line, illustrative data, mechanism proven end-to-end (virtual sensing → forecast → prescription → defect trace → self-validation) |
| **Entry criteria** | None — this is where we start |
| **Duration** | Round 2 timeline (this build) |
| **Exit criteria (gate to Phase 2)** | (a) All M0–M8 milestones shipped (`PLAN.md` §5); (b) validation metrics reported and meet PoC targets (`docs/VALIDATION.md` — MAPE, calibration, false-alarm rate, CRPS beat a persistence baseline); (c) a live demo runs the 4 scenarios end-to-end without a human editing data mid-run |
| **Owner** | Dev + BA (mechanism + business case must both be demo-ready) |

## Phase 2 — Pilot (one real line, shadow mode)

| | |
|---|---|
| **Scope** | One real production line at a design-partner plant; read-only tap into existing historian/MES/scan feeds — **no code or line changes**; runs in **shadow mode** (recommendations logged, not acted on) before any supervisor-facing rollout |
| **Entry criteria** | (a) Phase 1 exit gate met; (b) a design partner identified with ≥60% sensor coverage and existing scan checkpoints (matches `ASSUMPTIONS.md` line profile); (c) IT/OT security review scoped against `RISK_REGISTER.md` §2 completed and passed |
| **Duration** | ~3 months: weeks 1–2 integration + per-site recalibration (`RISK_REGISTER.md` risk #7), weeks 3–8 shadow mode, weeks 9–12 supervisor-facing with human-in-the-loop overrides captured |
| **Exit criteria (gate to Phase 3)** | (a) Pilot KPI thresholds met (`PILOT_KPIS.md`, #40) — false-alarm rate, calibration, and adoption bars all cleared on **real** (not simulated) data; (b) at least one instrumentation recommendation (VoI-ranked) acted on and validated; (c) a signed reference/case-study commitment from the pilot site |
| **Owner** | BA (commercial terms, KPI tracking) + Dev (integration, recalibration) |
| **Commercial terms this phase** | Pilot pricing tier — see [`PRICING.md`](PRICING.md) (#45) §2 |

## Phase 3 — Scale (multi-line, multi-site)

| | |
|---|---|
| **Scope** | Additional lines at the pilot site, then additional sites; VoI-driven instrumentation roadmap replaces ad hoc sensor purchases; per-site recalibration becomes a standard onboarding step, not a bespoke project |
| **Entry criteria** | Phase 2 exit gate met — a validated, referenceable pilot exists |
| **Duration** | Ongoing; paced by onboarding throughput, not calendar time |
| **Exit criteria** | N/A — steady state. Progress is tracked per-line via the same KPI sheet used in Phase 2 |
| **Owner** | BA (commercial scale-out, pricing tier transitions) + Dev (multi-tenant hardening, out of scope for this PoC per `PLAN.md` §11) |
| **Commercial terms this phase** | Scale SaaS tiers — see [`PRICING.md`](PRICING.md) (#45) §3 |

## Gate summary (single table)

| Gate | From → To | Key condition |
|---|---|---|
| G1 | PoC → Pilot | Validation targets met on simulated data + design partner secured |
| G2 | Pilot → Scale | KPI thresholds met on **real** data + referenceable case study |

## What could stall a phase (and the mitigation on file)

- **G1 stall** — validation targets missed: re-tune thresholds, extend PoC; do not carry an
  unvalidated model into a real plant (violates `PLAN.md` §1.4 "validated before trusted").
- **G2 stall** — real-world false-alarm rate higher than simulated: this is exactly why shadow
  mode exists before supervisor-facing rollout (`RISK_REGISTER.md` risk #2); extend shadow mode
  rather than force the gate.

## Handoff

- → `ROI_MODEL.md` §5: multi-line scale-out in Phase 3 multiplies the per-line ROI once G2 is
  cleared; that model's 3-year view assumes a single line and should be re-run per additional
  line onboarded.
- → `BUSINESS_PROPOSAL.md` §5: this file is the source of truth for the roadmap section;
  quote the gate summary table directly.
- → Presentation (#54): the 3-phase table with gates is slide-ready as a horizontal roadmap.
