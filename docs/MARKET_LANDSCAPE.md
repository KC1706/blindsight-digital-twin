# Market & Competitor Landscape

**Issue:** #41 · **Feeds:** [`BUSINESS_PROPOSAL.md`](BUSINESS_PROPOSAL.md) §1–2,
business-case slides (#54).

## 1. Where Blindsight sits

Three adjacent categories exist today. None does what Blindsight does — infer the stations
it cannot instrument, rather than only visualize the ones it can.

| Category | Examples (illustrative, publicly known categories — not an exhaustive vendor audit) | What they do | Gap vs. Blindsight |
|---|---|---|---|
| **MES / SCADA dashboards** | Siemens Opcenter, Rockwell FactoryTalk, generic MES layers | Show state of *instrumented* stations, historically (rear-view) | No inference for dark stations; no forecast; alerts *after* the stop |
| **Traditional APM / predictive maintenance** | GE Digital APM-class tools, vibration/thermal condition-monitoring platforms | Predict *equipment* failure from sensor time-series | Requires a sensor on the asset — doesn't help manual/dark stations at all |
| **Digital twin platforms (general-purpose)** | Siemens Xcelerator/Tecnomatix-class, NVIDIA Omniverse-class simulation twins | Photoreal 3D simulation, offline "what-if" layout studies | Built for design-time simulation, not live inference from partial real-time data; heavy, retrofit-adjacent (needs full instrumentation or CAD rebuild) |
| **Process-mining / analytics** | Celonis-class process mining | Post-hoc pattern mining over event logs | Backward-looking by design; not a live forecast or virtual sensor |

## 2. Differentiation statement

> **Blindsight is the only category of tool that turns the sensors you already have into
> sensors for the stations you don't** — using flow physics (blocked/starved propagation,
> travel-time tomography over existing scan checkpoints), not new hardware, not full
> instrumentation, and not offline simulation. It ships every estimate with an error bar and
> validates itself against replayed outcomes, so a plant manager can trust a number instead of
> just looking at a screen.

Three concrete differentiators, each mapped to a named competitor gap:

1. **Retrofit-free virtual sensing** vs. MES (which shows only what's wired) and APM (which
   needs a sensor on the specific asset).
2. **Live, uncertainty-quantified forecast** vs. digital-twin platforms (offline, deterministic,
   design-time) and process mining (backward-looking).
3. **Self-validating (backtested, VoI-ranked)** vs. all four categories, none of which report a
   calibration/false-alarm rate against their own predictions as a core feature.

## 3. Comparables mapped (5+, per DoD)

| # | Comparable | Category | Strength | Where Blindsight wins |
|---|---|---|---|---|
| 1 | Siemens Opcenter / generic MES | MES dashboard | Deep PLC integration, mature | No inference layer; rear-view only |
| 2 | Rockwell FactoryTalk Analytics | MES/analytics | Strong OT install base | Descriptive, not predictive for dark stations |
| 3 | GE Digital APM-class tools | Predictive maintenance | Proven failure-prediction ROI | Needs instrumentation per asset; no line-flow model |
| 4 | Siemens Tecnomatix / Xcelerator-class twins | Simulation digital twin | Rich 3D, design-time optimization | Not live; heavy setup; not built for partial real-time data |
| 5 | Celonis-class process mining | Process mining | Great for discovering *where* process deviates, historically | No forward forecast, no physical-flow inference, no uncertainty bands |
| 6 | In-house Excel/BI dashboards (the real incumbent on most floors) | Status quo | Free, already trusted, low friction | No inference, no forecast, no prescriptive action — literally what the brief calls "rear-view mirrors" |

## 4. Positioning line for the pitch

*"Not another dashboard for the stations you can already see. The first virtual sensor for
the ones you can't."*

## Handoff

- → `BUSINESS_PROPOSAL.md` §1–2 (problem framing / solution design): use §2 differentiation
  statement verbatim.
- → Presentation (#48 narrative, #54 business-case slides): the comparison table (§3) is
  slide-ready as a 2x3 grid.
