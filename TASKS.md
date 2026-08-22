# Taskboard

**GitHub Issues + Milestones is the source of truth** (39 issues across 9 milestones) —
built from the reusable convention in `~/software-learning/taskboard-template/`. Issues carry
`area:* · type:* · priority:* · size:*` labels; deep-tech tasks reference
[`docs/METHODS.md`](docs/METHODS.md). This file is a human-readable summary; milestones = build
phases (see [`PLAN.md`](PLAN.md) §5, §9–10). Statuses: ⬜ todo · 🟨 in progress · ✅ done.

> Deep-tech issues added on top of the summary below: Bayesian hierarchical tomography,
> service/wait separation, variant-aware design matrix, online particle/Kalman filter,
> uncertainty-propagating forecast, SPC+change-point, causal attribution, OCBA/KN
> simulation-optimization, CRPS/calibration backtest, submodular value-of-information,
> shared `api/schemas.py` seam, mock server, CI. See the [Issues](../../issues) for detail.

## M0 · Foundations
- ✅ Repo, planning docs, directory skeleton
- ⬜ `requirements.txt` + dev setup (venv, Makefile)
- ⬜ `engine/line.py` — line topology & station config schema
- ⬜ Scenario config format (`scenarios/*.yaml|json`)

## M1 · Ground truth + observability
- ⬜ `engine/ground_truth_sim.py` — DES producing "reality" + event log
- ⬜ `engine/observe.py` — sensor-coverage mask → observable stream only
- ⬜ Scenario: `baseline`, `torque_drift_s8`, `takt_slip_s14`, `surge_3x`

## M2 · Virtual sensing
- ⬜ Blocked/starved real-time bottleneck inference
- ⬜ Travel-time tomography solver (regularized least squares)
- ⬜ Per-station confidence / error bars
- ⬜ Test: recovered cycle times vs ground truth (accuracy report)

## M3 · Forecast
- ⬜ `engine/forecast.py` — Monte Carlo forward sim (500× / 2h)
- ⬜ Constraint probability, expected units lost, ETA + percentile bands

## M4 · Prescription + defect trace
- ⬜ `engine/prescribe.py` — counterfactual lever search + ranking
- ⬜ `engine/defect_trace.py` — VIN containment from scan timestamps

## M5 · Validation & trust
- ⬜ `engine/validate.py` — backtest (Brier, calibration, lead time, false-alarm rate)
- ⬜ Value-of-information: "instrument these 3 first"
- ⬜ `docs/VALIDATION.md`

## M6 · API
- ⬜ `api/main.py` — FastAPI REST snapshots
- ⬜ Websocket live line-state stream

## M7 · Dashboard (3 views)
- ⬜ Floor supervisor — real-time line map + alerts + next action
- ⬜ Plant manager — 2-hour forecast + constraint timeline
- ⬜ Leadership — ROI / units & $ saved / instrument-3-first

## M8 · Demo & proposal
- ⬜ Scripted demo scenarios end-to-end
- ⬜ `docs/BUSINESS_PROPOSAL.md`
- ⬜ Pitch alignment with Round 1 narrative
