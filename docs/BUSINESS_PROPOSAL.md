# Business Proposal — Blindsight

**Issue:** #24 · **Track 4 · DigitalTwin.ai · Round 2 · Team DarkShield**

This is the integrated business deliverable Round 2 asks for: "problem framing, solution
design, target users, business case and impact, a phased roadmap, and key risks with
mitigations." Every number below is sourced from a parameterized model under `docs/`, not
asserted here — follow the links for the full derivation, sensitivity, and stated caveats.

## 1. Problem framing

Modern assembly lines are unevenly instrumented: robot cells and powered tools report state,
but manual stations — often the true constraint — are dark (`docs/ASSUMPTIONS.md`: ~25% of the
prototype's 40-station line — 10 stations — and up to ~35% on a representative industry line).
Existing tools compound this:

- **MES/SCADA dashboards** show only what's wired, and only *after* the stop — a rear-view
  mirror, not a forecast (`docs/MARKET_LANDSCAPE.md` §1).
- **APM/predictive-maintenance tools** need a sensor on the specific asset — no help for the
  35% with no sensor at all.
- **Digital-twin/simulation platforms** are offline, design-time tools — not live inference
  from partial real-time data.

The cost of this blindness is not abstract. On a representative line (`docs/
COST_OF_BLINDNESS.md`), three drivers — unmanaged bottleneck ripple, late defect detection, and
reactive firefighting labor — sum to an estimated **≈ $16.5M/year (base case; range
$3.4M–$64.6M)**, dominated by how long it takes to localize a shifting bottleneck without a
sensor on it.

## 2. Solution design

**"The line is the sensor."** Blindsight turns the sensors a plant already has into inference
for the ones it doesn't, then closes the loop with a forecast, a ranked action, and a
self-check:

1. **Virtual sensing** — blocked/starved propagation localizes a dark bottleneck from its
   instrumented neighbours; travel-time tomography over existing scan checkpoints estimates
   every station's cycle time, dark or not, each with an error bar (`PLAN.md` §2.2–2.3,
   `docs/METHODS.md`).
2. **Probabilistic forecast** — a 2-hour Monte-Carlo forward simulation gives
   `P(station is binding constraint)` and expected units lost, with percentile bands
   (`PLAN.md` §2.4).
3. **Prescriptive action** — counterfactual re-simulation ranks candidate levers (move an
   operator, rebalance a buffer, adjust takt) by expected units recovered net of cost
   (`PLAN.md` §2.5).
4. **Defect containment** — an SPC signal plus scan timestamps names the exact VINs in the
   drift window, before end-of-line audit (`PLAN.md` §2.6).
5. **Trust, built in** — every forecast is backtested against replayed outcomes (calibration,
   false-alarm rate, CRPS vs. a persistence baseline — `docs/VALIDATION.md`), and a
   value-of-information ranking says which 3 dark stations to instrument first, not all of them
   (`PLAN.md` §2.7).

It is **retrofit-free and read-only**: no PLC writes, no new hardware to prove the mechanism,
human-in-the-loop throughout (`docs/ASSUMPTIONS.md`). This is also the core differentiator vs.
every category in `docs/MARKET_LANDSCAPE.md` §2: *"the only category of tool that turns the
sensors you already have into sensors for the stations you don't."*

## 3. Target users

Three stakeholders, three jobs-to-be-done, three dashboard views already built in `web/`
(full detail: `docs/PERSONAS.md`):

| Persona | Job-to-be-done | View |
|---|---|---|
| **Floor supervisor** | Know which station is the real constraint right now, without walking the line | Floor view — live map, one recommended action |
| **Plant manager** | See the 2-hour forecast and a ranked, costed action to recover units-at-risk | Plant-manager view — forecast bands, ranked levers |
| **Leadership** | Decide whether to fund a pilot/scale-out with an ROI number and a costed instrumentation roadmap | Leadership view — ROI tile, VoI-ranked roadmap |

## 4. Business case & impact

**Value.** Blindsight doesn't eliminate the cost of blindness outright — it captures a
ramping fraction of it as trust and confidence build over a pilot, plus deferred capex from
instrumenting only the top-VoI stations instead of all of them (`docs/ROI_MODEL.md` §1–2):

```
Value_yr1 = capture_rate × (Loss_ripple + Loss_defect) + deferred_capex_savings
Base case: 45% × $16.5M + $88,000 ≈ $7.5M/year, one line, once ramped
```

**Cost.** Priced per line, per `docs/PRICING.md` Starter tier ($10,000/month) plus one-time
implementation ($40,000) — Year-1 platform cost **$160,000 (base)**.

**Payback.** `docs/ROI_MODEL.md` §4:

| Scenario | Annual value (ramped) | Year-1 cost | Payback |
|---|---|---|---|
| Low | $0.85M | $121,000 | **~5 months** — the number to lead with; survives a skeptic halving every input |
| Base | $7.5M | $160,000 | < 1 month (implementation cost alone) |
| High | $39.0M | $240,000 | < 1 month |

Multi-line scale-out multiplies this per additional line onboarded (`docs/ROI_MODEL.md` §5,
`docs/GTM_ROADMAP.md` Phase 3). Success is tracked against `docs/PILOT_KPIS.md` — throughput
recovered, false-alarm rate, calibration, adoption, and payback, each mapped to a metric
`engine/validate.py` already measures.

## 5. Phased roadmap

Three gated phases (full entry/exit criteria: `docs/GTM_ROADMAP.md`):

| Phase | Scope | Exit gate |
|---|---|---|
| **1 — PoC** (this prototype) | One simulated line, mechanism proven end-to-end | Validation targets met (`docs/VALIDATION.md`); live demo runs clean |
| **2 — Pilot** | One real line, read-only tap, shadow-mode before go-live | `docs/PILOT_KPIS.md` thresholds met on **real** data; referenceable case study |
| **3 — Scale** | Multi-line, multi-site; VoI-driven instrumentation, not "instrument everything" | Steady state — tracked per-line via the same KPI sheet |

Commercial terms per phase are defined in `docs/PRICING.md` (no license fee during Pilot;
per-line SaaS tiers at Scale).

## 6. Key risks & mitigations

Full register with compliance posture: `docs/RISK_REGISTER.md`. Highest-severity, most
pitch-relevant rows:

| Risk | Mitigation |
|---|---|
| Dark-station estimates too uncertain to act on | Error bars everywhere; abstain below a confidence threshold; VoI tells you where a cheap sensor removes the doubt |
| False alarms erode floor trust | Backtested false-alarm rate reported (0% on clean baselines); conservative thresholds; shadow-mode before go-live |
| OT/security concerns | Read-only by construction — no PLC write path exists to remove; DMZ-bridged tap, IEC-62443-aligned segmentation |
| Site-to-site variation | Per-site recalibration required before go-live; hierarchical priors transfer structure, not exact values |
| Change management (fatigued staff ignore it) | One clear action, not a dashboard to interpret; overrides captured as feedback |
| Data/compliance exposure | Operator IDs pseudonymized; telemetry itself is not personal data; minimal GDPR/CCPA-class exposure (`docs/RISK_REGISTER.md` §2) |

## 7. Validation — why the numbers above can be trusted

Every predictive claim in this document is backtested, not asserted (`docs/VALIDATION.md`):
dark-station cycle-time MAPE **3.3%**, error-bar coverage **100%** on the stated 80% band,
false-alarm rate **0%** on 12 clean shifts, forecast CRPS **~10× better** than a persistence
baseline. This is the evidence behind "validated before trusted" (`PLAN.md` §1.4) — and the
gate that must hold on real pilot data before Phase 3 (§5 above).

## Document map

| Section | Full detail |
|---|---|
| Problem sizing | `docs/COST_OF_BLINDNESS.md` |
| Competitive landscape | `docs/MARKET_LANDSCAPE.md` |
| Mechanism | `PLAN.md`, `docs/METHODS.md` |
| Personas | `docs/PERSONAS.md` |
| ROI / payback | `docs/ROI_MODEL.md` |
| Pricing | `docs/PRICING.md` |
| Roadmap | `docs/GTM_ROADMAP.md` |
| Risk & compliance | `docs/RISK_REGISTER.md` |
| Pilot success criteria | `docs/PILOT_KPIS.md` |
| Validation results | `docs/VALIDATION.md` |
| Stated assumptions | `docs/ASSUMPTIONS.md` |
