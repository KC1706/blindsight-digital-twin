# Blindsight — Business Proposal

**Team DarkShield · Accenture Innovation Challenge 2026 · Round 2 · Track 4 · DigitalTwin.ai**

## Executive summary

Assembly lines are unevenly instrumented — and the manual stations that most often set the
pace have no sensor at all. **Blindsight is a digital twin that infers those dark stations from
the sensors a plant already has**, forecasts the line two hours ahead, and prescribes the
single best action — with **no new hardware and no changes to the line**.

On a representative line, the cost of this blindness is **≈ ₹140 Cr/year**. Blindsight captures
a validated fraction of it — **≈ ₹64 Cr/year per line (base case)** — at a Year-1 cost of
**₹1.36 Cr**, a **payback under one month**, and **~5 months even on the most conservative
assumptions**. The mechanism is already built and validated against ground truth: dark-station
cycle-time error **3.3%**, **0% false alarms** on clean shifts, and forecasts **~10× better**
than a naïve baseline.

> Figures in INR (₹1 Cr = 10 million, ₹1 lakh = 100 thousand); underlying models converted at
> **₹85/USD**. This document is self-contained; the appendix lists the detailed models behind
> each number.

## 1. Problem framing

Modern assembly lines mix legacy and modern equipment, so sensor coverage is uneven: robot
cells and powered tools report their state, but manual stations — often the true constraint —
are **dark** (~25% of our prototype's 40-station line; a representative industry line runs
higher). The stations where humans vary most are exactly the ones nothing can see.

Existing tools each miss this gap:

- **MES / SCADA dashboards** show only what's wired, and only *after* the stop — a rear-view
  mirror, not a forecast.
- **APM / predictive-maintenance tools** need a sensor on the specific asset — no help for the
  stations with no sensor at all.
- **Digital-twin / simulation platforms** are offline, design-time tools — not live inference
  from partial real-time data.

**No existing category turns the sensors you already have into sensors for the stations you
don't** — that is the opening Blindsight takes.

The cost of this blindness is not abstract. Three drivers — unmanaged bottleneck ripple, late
defect detection, and reactive firefighting labor — sum to an estimated **≈ ₹140 Cr/year (base
case; range ₹29 Cr–₹549 Cr)**, dominated by how long it takes to localize a shifting bottleneck
with no sensor on it.

## 2. Solution design

**"The line is the sensor."** Blindsight turns the sensors a plant already has into inference
for the ones it doesn't, then closes the loop with a forecast, a ranked action, and a
self-check:

1. **Virtual sensing** — blocked/starved propagation localizes a dark bottleneck from its
   instrumented neighbours; travel-time tomography over existing scan checkpoints estimates
   every station's cycle time, dark or not, each with an error bar.
2. **Probabilistic forecast** — a 2-hour Monte-Carlo forward simulation gives the probability
   each station becomes the binding constraint and the expected units lost, with percentile
   bands.
3. **Prescriptive action** — counterfactual re-simulation ranks candidate levers (move an
   operator, rebalance a buffer, adjust takt) by expected units recovered net of cost.
4. **Defect containment** — an SPC signal plus scan timestamps names the exact vehicles built
   in a drift window, before end-of-line audit.
5. **Trust, built in** — every forecast is backtested against replayed outcomes, and a
   value-of-information ranking says which dark stations to instrument first, not all of them.

It is **retrofit-free and read-only**: no PLC writes, no new hardware to prove the mechanism,
and a human in the loop throughout. That is also the core differentiator — the only category of
tool that turns the sensors you already have into sensors for the stations you don't.

## 3. Target users

Three stakeholders, three jobs-to-be-done, three dashboard views — all built in the prototype:

| Persona | Job-to-be-done | View |
|---|---|---|
| **Floor supervisor** | Know which station is the real constraint right now, without walking the line | Live line map + one recommended action |
| **Plant manager** | See the 2-hour forecast and a ranked, costed action to recover units-at-risk | Forecast bands + ranked levers |
| **Leadership** | Decide whether to fund a pilot or scale-out, with an ROI number and a costed instrumentation roadmap | ROI tile + value-of-information roadmap |

## 4. Business case & impact

**Value.** Blindsight doesn't eliminate the cost of blindness outright — it captures a ramping
fraction of it as trust builds over a pilot, plus deferred capex from instrumenting only the
highest-value stations instead of all of them:

```
Value_yr1 = capture_rate × (bottleneck loss + defect loss) + deferred_capex_savings
Base case: 45% × ₹140 Cr + ₹75 lakh  ≈  ₹64 Cr/year, one line, once ramped
```

**Cost.** Priced per line: Starter tier **₹8.5 lakh/month** plus one-time implementation
**₹34 lakh** — **Year-1 platform cost ₹1.36 Cr (base)**. Software on data the plant already
emits; the only integration is a read-only tap on the scan log and PLC feed.

**Payback.**

| Scenario | Annual value (ramped) | Year-1 cost | Payback |
|---|---|---|---|
| **Low** | ₹7.2 Cr | ₹1.03 Cr | **~5 months** — the number to lead with; survives halving every input |
| **Base** | ₹64 Cr | ₹1.36 Cr | **< 1 month** (implementation cost alone) |
| **High** | ₹332 Cr | ₹2.04 Cr | **< 1 month** |

Read the sub-month base payback honestly: it is because line-blindness loss is large, not
because the tool is expensive. The **~5-month low case** is the conservative number to plan on.
Multi-line scale-out multiplies this per additional line onboarded.

## 5. Phased roadmap

Three gated phases, each with an explicit exit gate:

| Phase | Scope | Exit gate |
|---|---|---|
| **1 — PoC** (this prototype) | One simulated line, mechanism proven end-to-end | Validation targets met; live demo runs clean |
| **2 — Pilot** | One real line, read-only tap, shadow-mode before go-live | KPI thresholds met on **real** data; a referenceable case study |
| **3 — Scale** | Multi-line, multi-site; value-of-information-driven instrumentation | Steady state, tracked per-line via the same KPI sheet |

Commercially: **no license fee during the Pilot** (removes budget as an adoption barrier);
per-line SaaS tiers at Scale.

## 6. Key risks & mitigations

| Risk | Mitigation |
|---|---|
| Dark-station estimates too uncertain to act on | Error bars everywhere; the twin abstains below a confidence threshold; value-of-information says where a cheap sensor removes the doubt |
| False alarms erode floor trust | Backtested false-alarm rate reported (0% on clean baselines); conservative thresholds; shadow-mode before go-live |
| OT / security concerns | Read-only by construction — there is no PLC write path to exploit; DMZ-bridged tap, IEC-62443-aligned segmentation |
| Site-to-site variation | Per-site recalibration before go-live; hierarchical priors transfer structure, not exact values |
| Change management (fatigued staff ignore it) | One clear action, not a dashboard to interpret; overrides captured as feedback |
| Data / compliance exposure | Operator IDs pseudonymized; telemetry is not personal data; minimal GDPR/CCPA-class exposure |

## 7. Validation — why these numbers can be trusted

Every predictive claim here is **backtested against ground truth, not asserted**: dark-station
cycle-time MAPE **3.3%** (instrumented: 1.9%), error-bar coverage **100%** on the stated 80%
band, false-alarm rate **0%** on 12 clean shifts, and forecast CRPS **~10× better** than a
persistence baseline. This is the evidence behind "validated before trusted" — and the same
gate must hold on real pilot data before we scale.

## The ask

**One line, one shift-pattern, read-only.** We deploy on the plant's existing scan + PLC feed,
backtest against the last month of production, and prove units recovered in the first pilot —
**no new hardware, no line downtime, exit at any time.** From there, the value-of-information
roadmap tells the plant exactly which three sensors to buy first.

---

## Appendix — the models behind each number

Every figure in this proposal is derived in a parameterized model in the project repository
(not asserted here), so each claim is traceable and re-runnable:

| Topic | Model |
|---|---|
| Problem sizing (cost of blindness) | `docs/COST_OF_BLINDNESS.md` |
| Competitive landscape | `docs/MARKET_LANDSCAPE.md` |
| Mechanism & methods | `PLAN.md`, `docs/METHODS.md` |
| Personas | `docs/PERSONAS.md` |
| ROI / payback | `docs/ROI_MODEL.md` |
| Pricing | `docs/PRICING.md` |
| Roadmap | `docs/GTM_ROADMAP.md` |
| Risk & compliance | `docs/RISK_REGISTER.md` |
| Pilot success criteria | `docs/PILOT_KPIS.md` |
| Validation results | `docs/VALIDATION.md` |
| Stated assumptions | `docs/ASSUMPTIONS.md` |
