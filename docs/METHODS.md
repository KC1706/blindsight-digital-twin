# Methods — the deep-tech core of Blindsight

This document specifies the mathematics behind each mechanism. It is the reference the
`engine/` issues implement against. Notation is kept consistent across sections.

**Setup.** A line has stations `j ∈ {1..S}`. A subset `I ⊂ {1..S}` are *instrumented*
(emit state + timestamps); the rest `D = {1..S}\I` are *dark* (manual, no sensor). Vehicles
`i` (each of model/variant `v(i)`) are timestamped at scan checkpoints `c ∈ C`. Between
consecutive checkpoints lies a *segment* containing one or more stations. Blindsight's job is
to estimate, for every station, an effective service-time distribution and the live line
state, using only observations from `I` and `C`.

---

## 1. Bottleneck detection from blocked/starved durations (no sensor on the bottleneck)

We use the **active-period / turning-point** method (Roser, Nakano & Tanaka), which needs
only per-station "active vs. inactive" state — available at instrumented stations, and
*inferable* for a dark station from its instrumented neighbours' blocking/starvation.

- A station's **active period** = it is processing (not blocked, not starved).
- The **momentary bottleneck** at time `t` is the station with the longest *uninterrupted*
  active period covering `t`. Shifts between bottlenecks are detectable when active periods
  of two stations overlap ("shifting bottleneck").
- **Dark-station inference:** if instrumented station `a` (upstream of dark `d`) shows rising
  **blocking** (finished, nowhere to put the unit) *and* instrumented station `b` (downstream
  of `d`) shows rising **starvation** (idle, nothing arriving), then `d` is active and is the
  local constraint. The blocked→starved boundary localizes the bottleneck to the dark span
  between `a` and `b`.

Output: a live `P(station j is momentary bottleneck)` signal, updated each tick.

## 2. Travel-time tomography — estimating dark-station service times (inverse problem)

Each vehicle's checkpoint-to-checkpoint travel time decomposes into service + waiting:

```
T_i (segment for checkpoint pair p) = Σ_{j ∈ seg(p)} [ x_{j,v(i)} + w_{i,j} ]
```

- `x_{j,v}` = effective **service time** of station `j` for variant `v` (unknown, incl. dark j).
- `w_{i,j}` = **waiting/blocking** time vehicle `i` spent at `j` (a nuisance term).

**Separating service from wait.** Waiting is not noise — it is correlated with congestion.
We estimate `w` from flow state: during intervals when the segment is *not* blocked/starved
(known from §1), `w ≈ 0`, so those vehicles give near-pure service-time equations. We build
the design matrix from *free-flow* vehicles first, then treat congested vehicles with a
queueing correction (§2.2).

### 2.1 Linear inverse formulation
Stack free-flow vehicles into `A x = T`, where `A ∈ {0,1}^{N×(S·V)}` is the
station-in-segment incidence (expanded per variant `V`). This is typically over-determined
(`N ≫ S·V`) but **ill-conditioned** (stations that always share a segment are only jointly
identifiable). Solve **Tikhonov-regularized non-negative least squares**:

```
x̂ = argmin_{x ≥ 0}  ‖A x − T‖²_Σ⁻¹ + λ ‖L x‖²
```

- `Σ` = measurement-noise covariance (heteroscedastic: longer segments, noisier).
- `L` = smoothness/prior operator (neighbouring stations of the same type have similar times).
- `λ` chosen by generalized cross-validation (GCV) or L-curve.

### 2.2 Bayesian hierarchical version (uncertainty is first-class)
We prefer a Bayesian formulation so every estimate ships with a posterior, not a point:

```
T_i ~ Normal( Σ_j A_ij x_{j,v(i)} , σ²_seg )
x_{j,v} ~ Normal( μ_type(j) , τ² )         # partial pooling by station type
μ_type, τ, σ ~ weakly-informative hyperpriors
```

Inference by conjugate Gibbs / variational / NUTS (small model → fast). The **posterior
variance of `x_{j,·}` is the station's error bar.** Dark stations that appear only inside long
shared segments get *wide* posteriors — surfaced honestly, and used directly in §5 (VoI).

### 2.3 Online state estimation (live, recursive)
For the real-time view we run a **Bayesian filter** (Rao-Blackwellized particle filter, or an
EKF/UKF on a queueing-network state) whose latent state is `(WIP position of every vehicle,
current service-rate of every station)`. Measurements = instrumented state transitions + scan
events. The filter fuses §1 and §2 into a single live posterior and handles regime changes
(operator swap, micro-stoppage) via a small transition-noise / jump component.

## 3. Root-cause & anomaly detection (multi-causal, intermittent)

- **SPC on service times:** per station, EWMA and CUSUM control charts on `x̂_{j,t}` catch
  slow drift (tool wear) and small persistent shifts that Shewhart charts miss.
- **Attribution:** when a station degrades, decompose the change across candidate drivers
  (equipment wear = monotone trend; operator variation = shift/person-correlated step;
  upstream part quality = correlation with incoming variant/supplier; environment = time-of-day
  / temperature covariate). We fit a simple **interpretable additive model** (change-point +
  covariate regression) and report ranked contributions with confidence — *not* an LLM guess.

## 4. Forward simulation & probabilistic forecast

A fast discrete-event **forward simulator** (event-driven, not the ground-truth sim) is seeded
with the filter posterior at "now": current WIP positions + sampled service-time distributions.

- Run `M ≈ 500` replications over a `H = 2 h` horizon.
- **Uncertainty propagation:** each replication samples a *different* draw from the parameter
  posterior (§2.2) — so the forecast band reflects both process randomness *and* estimation
  uncertainty (crucial for dark stations).
- **Variance reduction:** common random numbers across counterfactuals (§5) so action
  comparisons are apples-to-apples.
- Outputs per station: `P(becomes binding constraint within H)`, ETA distribution, expected
  units lost, throughput band (P10/P50/P90).

## 5. Prescription — simulation-optimization

Given the forecast, search over feasible **levers** `L` (move one operator `Sᵢ→Sⱼ`, open a
buffer, adjust takt, resequence variants). For each candidate we re-run the forward sim with
**common random numbers** and estimate `ΔThroughput`. Because the action space is small and
discrete, use ranking-and-selection (e.g. KN / OCBA) to allocate simulation budget efficiently
and return the best action *with a confidence it truly beats "do nothing."* Output contract:

```
driver → controllable lever → action → expected impact (units, band) → owner → confidence → monitoring plan
```

## 6. Defect propagation trace

On an SPC signal at station `j` with estimated onset window `[t0, t1]` (from the CUSUM
change-point), enumerate every vehicle whose scan history places it *at `j` during `[t0,t1]`*.
Because scans are timestamped, this is an exact set query — the **containment list** — plus
each affected VIN's *current* line position (from the filter). This is the "names the exact
vehicles affected" capability from the pitch.

## 7. Validation & trust (validated before trusted)

- **Distributional scoring:** CRPS for the throughput/ETA forecasts, Brier score for the
  binary "will hit constraint" call.
- **Calibration:** reliability diagram — do 80% bands contain truth 80% of the time?
- **Event metrics:** precision/recall on bottleneck events, **lead-time distribution** (how
  early we called it), and **false-alarm rate** (the trust killer the brief calls out).
- **Estimation accuracy:** recovered `x̂_j` vs. ground-truth `x_j` (MAPE), coverage of error
  bars — reported separately for instrumented vs dark stations (the honest headline number).
- **Backtest protocol:** rolling-origin over held-out shifts; no peeking at ground truth.

## 8. Value of information — "instrument these 3 first"

Sensor placement as **greedy information maximization**. For a candidate set `K` of dark
stations to instrument, the objective is the expected reduction in forecast error (CRPS) — or,
cheaper, the reduction in posterior entropy of throughput:

```
VoI(K) = H[throughput | current] − E[ H[throughput | current + sensors K] ]
```

`VoI` is (approximately) **submodular**, so greedy selection is near-optimal (1−1/e bound).
We report the top-3 stations and the marginal error reduction each buys — turning uncertainty
into a concrete, costed instrumentation roadmap.

---

## References (methods this builds on)
- Roser, Nakano, Tanaka — *Shifting bottleneck detection* (active-period method).
- Tikhonov regularization / GCV for ill-posed linear inverse problems.
- Rao-Blackwellized particle filtering for state-space estimation.
- CRPS & reliability diagrams for probabilistic forecast evaluation (Gneiting & Raftery).
- OCBA / KN ranking-and-selection for simulation-optimization.
- Submodular sensor placement (Krause & Guestrin).
