# Cost of Line Blindness — baseline loss model

**Issue:** #42 · **Owner:** BA · **Feeds:** [`ROI_MODEL.md`](ROI_MODEL.md) (#43),
[`BUSINESS_PROPOSAL.md`](BUSINESS_PROPOSAL.md) §4.

This model quantifies what uneven sensor coverage and rear-view dashboards cost a plant
*today*, before Blindsight. It is deliberately parameterized — every figure below is a named
variable with a stated default, so it can be re-run against a real plant's numbers without
rederiving the structure. Defaults are directional, chosen to be defensible for a mixed-model
automotive-style final-assembly line, and consistent with [`ASSUMPTIONS.md`](ASSUMPTIONS.md).

## 1. Line parameters (from ASSUMPTIONS.md)

| Parameter | Symbol | Default |
|---|---|---|
| Stations | `N` | 40 |
| Dark (uninstrumented) station share | `d` | 35% (14 stations) |
| Takt time | `takt` | 60 s → 1 unit/min at line rate |
| Units per shift (nameplate) | `U_shift` | 500 |
| Shifts per day | `S_day` | 2 |
| Working days per year | `D_yr` | 250 |
| → Annual nameplate volume | `U_yr` | `U_shift × S_day × D_yr` = **250,000 units** |

## 2. Three loss drivers

### 2.1 Unmanaged bottleneck ripple (blocked/starved propagation)

A dark station drifting slow starves downstream and blocks upstream, but a rear-view MES
dashboard only shows the *symptom* (idle robot cells) — not which of the 14 dark stations
caused it — until a supervisor manually walks the line. Blindsight's blocked/starved
inference (§2.2 of `PLAN.md`) localizes the constraint in real time instead.

```
Loss_ripple = episodes_per_shift × ΔMTTD_min × (60 / takt_s) × margin_per_unit
```

| Variable | Meaning | Low | Base | High |
|---|---|---|---|---|
| `episodes_per_shift` | bottleneck-migration events/shift needing diagnosis | 0.5 | 1 | 2 |
| `ΔMTTD_min` | mean-time-to-detect saved (walk-the-line vs. instant localization) | 8 | 15 | 25 |
| `margin_per_unit` | contribution margin per completed unit (assumption, replace with plant figure) | $1,500 | $2,000 | $3,000 |

Base case: `1 × 15 × 1 × $2,000` = **$30,000/shift** → `× S_day × D_yr` = **$15.0M/yr**.

### 2.2 Late defect detection (undetected SPC drift)

Without a defect-propagation trace, a drift (e.g. a torque tool 4% out of spec — see
`scenarios/torque_drift_s8`) is usually caught at end-of-line audit or later, contaminating
every VIN processed since the drift began. With Blindsight's SPC + scan-timestamp trace, the
exact affected VINs are named and contained within minutes.

```
Loss_defect = events_per_year × (units_affected_baseline − units_affected_blindsight) × cost_per_unit_rework
            + events_per_year × field_escape_rate × units_affected_baseline × cost_per_field_escape
```

| Variable | Low | Base | High |
|---|---|---|---|
| `events_per_year` (SPC drift events) | 26 | 52 | 104 |
| `units_affected_baseline` (undetected window → units) | 60 | 120 | 240 |
| `units_affected_blindsight` (contained window) | 5 | 10 | 20 |
| `cost_per_unit_rework` | $100 | $150 | $250 |
| `field_escape_rate` (fraction of baseline-affected units that reach the field) | 2% | 5% | 8% |
| `cost_per_field_escape` (warranty/recall-class cost) | $1,000 | $2,000 | $4,000 |

Base case: rework avoided = `52 × (120-10) × $150` = **$858,000/yr**; field-escape avoided =
`52 × 5% × 120 × $2,000` = **$624,000/yr** → **≈ $1.48M/yr**.

### 2.3 Reactive firefighting labor

Time engineers/supervisors spend diagnosing "why did we lose 40 units on 2nd shift" after the
fact, without a tool that already localized the cause.

```
Loss_firefighting = hours_per_day × loaded_hourly_cost × D_yr × reduction_fraction
```

| Variable | Low | Base | High |
|---|---|---|---|
| `hours_per_day` (diagnosis time across shifts) | 0.5 | 1 | 2 |
| `loaded_hourly_cost` | $60 | $75 | $100 |
| `reduction_fraction` (Blindsight removes most of the search, not the fix) | 50% | 70% | 85% |

Base case: `1 × $75 × 250 × 70%` = **$13,125/yr** (small relative to §2.1–2.2 — included for
completeness, not as a pitch headline).

## 3. Total cost of blindness (annual)

| Scenario | Ripple | Defect | Firefighting | **Total** | % of `U_yr × margin` |
|---|---|---|---|---|---|
| Low | $3.0M | $0.4M | $0.005M | **$3.4M** | ~9% |
| **Base** | **$15.0M** | **$1.5M** | **$0.01M** | **≈ $16.5M** | ~33% |
| High | $60.0M | $4.6M | $0.04M | **$64.6M** | — |

## 4. Sensitivity — top drivers

Ranked by swing in total annual loss between Low and High, holding others at Base:

1. **`episodes_per_shift` × `ΔMTTD_min`** (ripple) — dominates the total; this is why the
   pitch leads with blocked/starved localization, not the defect trace.
2. **`margin_per_unit`** — plant-specific; the model should be re-run with the target plant's
   actual figure before it's quoted externally.
3. **`events_per_year` (SPC drift frequency)** — second-order but drives the defect-trace
   narrative and the containment-list demo.

**Caveat, stated plainly:** these are illustrative defaults, not measured data (this is a
PoC on simulated data — see `ASSUMPTIONS.md`). The structure (which variables matter, in what
direction) is the deliverable; the numbers should be replaced with a target plant's actuals
before this model is used in a real sales conversation.

## 5. Handoff

- → [`ROI_MODEL.md`](ROI_MODEL.md) (#43): uses `Loss_ripple`, `Loss_defect` as the "avoidable
  loss" side of the ROI equation, applying a capture-rate discount (Blindsight recovers a
  fraction of the addressable loss, not all of it).
- → Presentation (#54): quote the **Base** row only; keep Low/High in the appendix.
