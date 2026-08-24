# Target-User Personas & Jobs-to-be-Done

**Issue:** #44 · **Maps to:** the 3 dashboard views in `web/` (`PLAN.md` §4, M7) ·
**Feeds:** [`BUSINESS_PROPOSAL.md`](BUSINESS_PROPOSAL.md) §3, [`PILOT_KPIS.md`](PILOT_KPIS.md)
(#40) adoption metric, business-case slides (#54).

Three stakeholders, three distinct jobs, one underlying model. Each persona below states the
job-to-be-done in the standard "when [situation], I want to [motivation], so I can [outcome]"
form, then maps directly to the dashboard view that serves it.

## 1. Floor Supervisor — "who's the bottleneck, right now"

| | |
|---|---|
| **Role** | Runs one line, one shift; owns immediate throughput |
| **JTBD** | *When* a station starts blocking/starving its neighbours, *I want to* know which station is the real constraint without walking the line, *so I can* act on it before the shift's units-lost number is fixed |
| **Pains today** | Manual (dark) stations give no signal; MES dashboards show *symptoms* (an idle robot cell downstream) not *cause*; diagnosis means physically walking the line |
| **Gains from Blindsight** | Real-time `P(station is bottleneck)` signal, including for dark stations, with no new hardware (`PLAN.md` §2.2) |
| **Time horizon** | Seconds to minutes — this shift, right now |
| **Dashboard view** | **Floor view** — live line map, current constraint highlighted, one recommended next action |
| **Success looks like** | Fewer walk-the-line diagnoses; faster mean-time-to-detect (feeds `COST_OF_BLINDNESS.md` §2.1 `ΔMTTD_min`) |

## 2. Plant Manager — "what's going to happen this shift, and what do I do about it"

| | |
|---|---|
| **Role** | Owns the whole plant's shift/day performance; balances multiple lines and a 2-hour-ish planning horizon |
| **JTBD** | *When* a drift or slip starts developing, *I want to* see the forecast units-at-risk and the ranked action to recover them, *so I can* decide (move an operator, rebalance a buffer) with a confidence number, not a hunch |
| **Pains today** | No forward view — dashboards are rear-view mirrors (`BUSINESS_PROPOSAL.md` §1); decisions on lever choice (move an operator vs. adjust takt) are made without a comparative expected-impact number |
| **Gains from Blindsight** | Monte-Carlo 2-hour forecast (`PLAN.md` §2.4) + counterfactual lever ranking by expected units recovered net of cost (`PLAN.md` §2.5) |
| **Time horizon** | Minutes to hours — this shift's remaining window |
| **Dashboard view** | **Plant-manager view** — forecast bands, binding-constraint probability, ranked action list with expected impact |
| **Success looks like** | Units-lost avoided vs. a persistence baseline (`VALIDATION.md` CRPS metric); fewer reactive, unranked interventions |

## 3. Leadership / Executive — "is this worth the investment, and where do we go next"

| | |
|---|---|
| **Role** | Owns the capital/budget decision — instrument more stations, expand to more lines, or not |
| **JTBD** | *When* deciding whether to fund a pilot or scale-out, *I want to* see ROI, payback, and a costed instrumentation roadmap, *so I can* commit budget with a number that survives a skeptical CFO |
| **Pains today** | Instrumentation spend is usually "instrument everything" (all 40 stations) with no way to rank which 3 matter most; ROI claims from vendors are typically unparameterized headline numbers |
| **Gains from Blindsight** | ROI/payback model built from named parameters (`ROI_MODEL.md`), value-of-information ranking that says "instrument these 3 first" instead of all 14 dark stations (`PLAN.md` §2.7, `VALIDATION.md` §"Value of information") |
| **Time horizon** | Weeks to years — budget cycles, multi-line scale decisions |
| **Dashboard view** | **Leadership view** — ROI tile (value, cost, payback from `ROI_MODEL.md` §1–4), instrumentation roadmap ranked by value of information |
| **Success looks like** | Payback period tracked against the `ROI_MODEL.md` projection; instrumentation spend directed by VoI ranking, not guesswork |

## 4. Persona → view → model traceability (single table, per DoD)

| Persona | Dashboard view | Primary model input | Primary KPI (`PILOT_KPIS.md`) |
|---|---|---|---|
| Floor Supervisor | Floor view | Blocked/starved inference (`PLAN.md` §2.2) | Mean-time-to-detect reduction |
| Plant Manager | Plant-manager view | Monte-Carlo forecast + prescription (`PLAN.md` §2.4–2.5) | Units-lost avoided / false-alarm rate |
| Leadership | Leadership view | ROI model + VoI ranking (`ROI_MODEL.md`, `PLAN.md` §2.7) | Payback vs. projection |

## Handoff

- → `web/` (M7, already built): confirms the 3 views already implemented match the 3 personas
  one-to-one — no fourth view is missing, no view serves two personas at once.
- → `BUSINESS_PROPOSAL.md` §3: this file replaces the one-line persona bullets with the full
  JTBD table.
- → `PILOT_KPIS.md` (#40): the "primary KPI" column here is the seed for that issue's per-persona
  KPI mapping.
