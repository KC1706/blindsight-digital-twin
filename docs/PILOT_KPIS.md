# Pilot KPIs & Success Criteria

**Issue:** #40 · **Depends on:** #35 (distributional backtest — delivered in
[`VALIDATION.md`](VALIDATION.md)) · **Ties BA value metrics to:** `PLAN.md` §7 (engine
acceptance criteria) · **Feeds:** [`GTM_ROADMAP.md`](GTM_ROADMAP.md) Phase 2 exit gate.

A pilot (`GTM_ROADMAP.md` Phase 2) is judged a success against these thresholds, each mapped to
a metric the prototype **already measures** (`docs/VALIDATION.md` / `engine/validate.py`), not
a metric we'd need to build. Where the PoC has a measured value on simulated data, it is shown
alongside the pilot's real-world target — the gap between them is exactly what the pilot exists
to close.

## 1. KPI sheet

| KPI | What it measures | Target threshold (real pilot) | PoC measured value (simulated, `VALIDATION.md`) | Measured by |
|---|---|---|---|---|
| **Throughput recovered** | Units/shift saved vs. a do-nothing baseline, on scenarios with an injected drift/slip | ≥ 60% of the forecast units-at-risk recovered when a recommendation is acted on | 15 units lost forecast on `takt_slip_s14` (band [10,19]); recommended action re-simulated to rank recovery | `engine/prescribe.py` counterfactual ranking + `engine/validate.py` |
| **False-alarm rate** | Fraction of shifts where the tool predicts material units lost with no real fault | ≤ 5% of clean shifts | **0%** on 12 clean baseline runs | `engine/validate.py` `false_alarm_rate` |
| **Forecast calibration** | Do stated confidence bands contain the truth at the stated rate | 80% band contains truth ≥ 75% of the time (allows real-world slack vs. PoC) | **100%** coverage on dark stations (PoC, simulated) | `engine/validate.py` error-bar coverage check |
| **Cycle-time accuracy (dark stations)** | MAPE of inferred vs. actual cycle time for uninstrumented stations | ≤ 15% MAPE | **3.3%** MAPE (simulated) | `engine/validate.py` `accuracy_vs_truth` |
| **Lead time** | Minutes of advance warning before a constraint would have been caught manually | ≥ 30 minutes median | Not yet measured on a real shift — PoC demonstrates localization is instantaneous vs. a manual walk (`COST_OF_BLINDNESS.md` §2.1 `ΔMTTD_min`, base 15 min saved) | Pilot-only metric — timestamp of tool alert vs. timestamp of historical manual detection, logged during shadow mode |
| **Adoption** | Fraction of recommendations a supervisor acts on (accepts) vs. overrides, tracked weekly | ≥ 50% acceptance by week 8 of pilot, trending up | N/A — requires human-in-the-loop shadow mode (`GTM_ROADMAP.md` Phase 2) | Override log (`ASSUMPTIONS.md` — overrides captured as feedback) |
| **Payback** | Time for realized value (throughput + defect containment) to exceed platform cost | Payback ≤ 6 months (the Low-scenario floor from `ROI_MODEL.md` §4) | Base-case model payback < 1 month; Low-scenario ~5 months (`ROI_MODEL.md` §4) | Realized value tracked against `ROI_MODEL.md` §1 formula using the pilot's actual loss figures |
| **Instrumentation efficiency (VoI)** | Forecast uncertainty removed per dollar of new sensor spend, vs. instrumenting stations at random | Top-3 VoI-ranked stations remove ≥ 50% of the removable uncertainty that instrumenting all dark stations would | On `takt_slip_s14`: instrumenting S14 alone removes 4.8 of 8.3 units (~58%) of forecast uncertainty | `engine/validate.py` value-of-information ranking |

## 2. Mapping KPIs to what the prototype can measure (per DoD)

Every KPI above except **Adoption** and **Lead time** is measured by a function that already
exists in `engine/validate.py` and is reported in `VALIDATION.md` today, on simulated data —
the pilot's job is to re-run the same measurement on real data, not build new instrumentation.
Adoption and Lead time are pilot-only by nature (they require a human supervisor and a real
historical baseline to compare against) and are explicitly named as such rather than
retrofitted onto a PoC number that doesn't exist yet.

## 3. Gate use

These thresholds are the concrete content behind `GTM_ROADMAP.md` Phase 2's exit criterion
"Pilot KPI thresholds met... on real (not simulated) data." A pilot that misses False-alarm
rate or Calibration does **not** proceed to Phase 3, regardless of how good Throughput or
Payback look — trust metrics gate the adoption metric, not the reverse (per `PLAN.md` §1.4).

## Handoff

- ← Development: KPI targets for cycle-time accuracy, false-alarm rate, and calibration are
  taken directly from the acceptance criteria already stated in `PLAN.md` §7 — kept identical
  on purpose so BA and Dev report the same numbers.
- → Leadership dashboard (#22): Payback and Throughput-recovered rows render as the ROI tile's
  supporting metrics.
- → `GTM_ROADMAP.md`: this sheet is the named content behind the Phase 2 exit gate.
