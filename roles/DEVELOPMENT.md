# Role guide — Development 🧩

**You own:** the Working Prototype. **Label:** `role:dev`. **Milestones:** M0–M8.
**Read first:** [`CLAUDE.md`](../CLAUDE.md) (shared workflow), [`PLAN.md`](../PLAN.md),
[`docs/METHODS.md`](../docs/METHODS.md) (the math you implement against).

## Mission

Turn the Blindsight mechanism into a runnable, self-scoring proof-of-concept on simulated
data: virtual sensing → probabilistic forecast → prescription → defect trace → validation,
surfaced through three dashboard views. Depth is the goal (see METHODS.md).

## Your board

Filter: `label:role:dev`. Work p0 → p1 → p2. Milestone order = dependency order.

**Critical path (p0):** M0 scaffolding + `api/schemas.py` (#37) → M1 ground-truth sim (#4,#5)
→ M2 virtual sensing (#7,#8,#9,#26,#27) → M3 forecast (#11,#12,#30) → M6 API (#18) →
M7 dashboard views (#20,#21). That's a runnable demo.

**Depth that wins (p1):** particle/Kalman filter (#29), SPC + change-point (#32), causal
attribution (#33), OCBA/KN prescription (#34), CRPS/calibration backtest (#35), value-of-
information (#36), defect trace (#14), variant-aware tomography (#28).

Start each of M2/M3 with its SPIKE (#25, #31) to de-risk before committing.

## Working directories

`engine/` (core mechanism, pure & tested) · `api/` (FastAPI, the seam) · `web/` (3 views) ·
`scenarios/`, `data/` · `tests/`.

## Conventions

- **Agree `api/schemas.py` (#37) on day one** — it's the seam BA/Deck and the UI build against.
- Keep `engine/` free of web/API imports (testable in isolation).
- Every estimate/forecast returns a **confidence/error bar** — never a bare number.
- Every headline metric is reported **split instrumented vs dark stations**.
- Branch `dev/<issue#>-<slug>`; small PRs; a test per behaviour change; CI (#39) stays green.

## Handoffs

- **→ Presentation:** validation numbers (#15,#35) feed results slides (#52); architecture
  (PLAN §4) feeds #51; a stable demo build + scenarios (#23) feed the fallback video (#53).
- **→ Business Analysis:** the leadership view (#22) consumes BA's ROI model (#43); tell BA
  which value metrics the prototype can actually measure (#40).
- **← Business Analysis:** personas (#44) shape the 3 views; pilot KPIs (#40) shape #17.
