# Blindsight — a digital twin that sees the stations it can't measure

**Team DarkShield · Accenture Innovation Challenge 2026 · Round 2 · Track 4 (DigitalTwin.ai)**

> The stations that most need watching are the ones nothing can see.
> Blindsight reads the sensors already on the line — differently — to estimate the
> dark stations, forecast the line two hours ahead, and tell the plant what to do next.

---

## The problem (Round 2, Track 4)

Real assembly lines are a patchwork of legacy and modern equipment. Sensor coverage is
**uneven** — robot cells are richly instrumented, manual stations often have nothing but a
checklist. And manual stations, where humans vary, are usually *where the bottleneck is*.
Existing MES/PLC dashboards are rear-view mirrors: they tell you the line stopped **after**
it stopped.

Round 2 asks for a working prototype that demonstrates the **core predictive mechanism** on
realistic (simulated) production data — a mixed-model line of ~30–50 stations, with the twin
staying useful at sensor-poor stations, surfacing uncertainty, and being validated against
real outcomes.

## The idea: "the line is the sensor"

Blindsight never assumes it can see every station. Instead it infers the invisible ones from
the physics of flow:

1. **Blocked/starved inference** — a slow ("dark") station *starves* everything downstream
   and *blocks* everything upstream. Both are visible at the instrumented stations on either
   side. The boundary between blocked and starved points straight at the bottleneck.
2. **Travel-time tomography** — vehicles are already timestamped at scan checkpoints. Each
   vehicle's travel time between two checkpoints is one equation over the stations in that
   segment. Thousands of vehicles make an over-determined system you can *solve* for the
   effective cycle time of every station — instrumented or not — with error bars.
3. **Forward Monte Carlo simulation** — from where every vehicle actually is right now, run
   ~500 simulations two hours ahead to predict which station becomes the binding constraint,
   when, and how many units it costs.
4. **Prescriptive recommendation** — re-simulate counterfactual actions ("move one operator
   from Station 12") and rank them by expected units recovered.
5. **Defect propagation trace** — when an SPC signal fires (e.g. a torque tool drifts 4% out
   of spec), use the scan timestamps to name the *exact* vehicles affected and where each one
   is standing right now.
6. **Trust & value-of-information** — every estimate ships with error bars; predictions are
   backtested against replayed outcomes; the twin ranks which 3 stations to instrument first.

**No retrofit. No new sensors. Just the line, finally telling you what it already knows.**

## Three views, one model

| Stakeholder | View | Needs |
|---|---|---|
| Floor supervisor | Real-time line map | live blocked/starved state, alerts, the next action |
| Plant manager | 2-hour forecast | constraint timeline, shift trends, planning |
| Leadership | ROI / business case | units & $ saved, "instrument these 3 first" |

## Repository layout

```
blindsight-prototype/
├── engine/      # the core mechanism (pure Python, testable)
├── api/         # FastAPI service (REST + websocket live stream)
├── web/         # browser dashboard — the 3 stakeholder views
├── scenarios/   # named demo scenarios (torque drift, takt slip, 3× surge)
├── data/        # generated line configs / seeds
├── tests/       # engine unit + validation tests
├── docs/        # business proposal, architecture, validation report
├── PLAN.md      # detailed technical plan & build phases
└── TASKS.md     # taskboard mirror (see GitHub Issues / Milestones)
```

## Status

🟡 **Planning complete — implementation not started.** See [`PLAN.md`](PLAN.md) for the
architecture and phased build, and the [Issues](../../issues) / [Milestones](../../milestones)
for the live taskboard.

## Deliverables (Round 2)

- **Business proposal** → `docs/BUSINESS_PROPOSAL.md`
- **Working prototype** → `engine/` + `api/` + `web/`
- **Pitch** → aligned with the existing Round 1 narrative (`../video-script.md`)
