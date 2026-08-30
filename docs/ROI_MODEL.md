# ROI / Business-Case Model

> Figures in INR (₹ Cr = 10M, ₹ lakh = 100k). Underlying model in USD, converted at **₹85/USD**.

**Issue:** #43 · **Depends on:** [`COST_OF_BLINDNESS.md`](COST_OF_BLINDNESS.md) (#42) ·
**Feeds:** Leadership dashboard (#22), business-case slides (#54),
[`BUSINESS_PROPOSAL.md`](BUSINESS_PROPOSAL.md) §4.

This is the number that has to survive a skeptical CFO. It is built entirely from named,
adjustable parameters — none of it is a hard-coded headline figure — so it can be re-run
against a real target plant before it is quoted externally.

## 1. Value side — what Blindsight captures

Blindsight does not eliminate the cost of blindness (§`COST_OF_BLINDNESS.md`) outright; it
captures a fraction of the addressable loss, ramping up as virtual-sensing confidence and
floor trust build over the pilot.

```
Value_yr1 = capture_rate × (Loss_ripple + Loss_defect)   [Loss_firefighting excluded — too small to matter]
          + deferred_capex_savings
```

| Variable | Low | Base | High |
|---|---|---|---|
| `Loss_ripple + Loss_defect` (from #42, annual, one line) | ₹29 Cr | ₹140 Cr | ₹549 Cr |
| `capture_rate` (share of addressable loss realized once ramped — not 100%: some episodes are still unrecoverable even with instant localization) | 25% | 45% | 60% |
| `deferred_capex_savings` — instrument top-3 (VoI, #36) vs. all 14 dark stations, at `₹6.8 lakh`/station installed | (14-3)×₹6.8 lakh = **₹75 lakh** one-time | same | same |

Base case: `45% × ₹140 Cr + ₹0.75 Cr` = **≈ ₹64 Cr** addressable value, one line, once ramped to
steady state.

## 2. Ramp — value is not day-one

Virtual-sensing confidence (tomography error bars) and floor trust (backtested false-alarm
rate) both build over the pilot. We model a linear ramp to full `capture_rate` by month 6:

| Month | 1 | 2 | 3 | 4 | 5 | 6+ |
|---|---|---|---|---|---|---|
| Ramp fraction of full `capture_rate` | 10% | 25% | 45% | 65% | 85% | 100% |

## 3. Cost side — platform cost

| Component | Low | Base | High |
|---|---|---|---|
| SaaS license (per line, per month) — see [`PRICING.md`](PRICING.md) (#45) | ₹6.8 lakh | ₹8.5 lakh | ₹12.75 lakh |
| One-time implementation (read-only tap setup, scan-log integration) | ₹21 lakh | ₹34 lakh | ₹51 lakh |
| **Year-1 platform cost** (`license×12 + implementation`) | ₹1.03 Cr | ₹1.36 Cr | ₹2.04 Cr |

## 4. Payback period

```
Payback_month = first month m where Σ(Value_month, 1..m) ≥ Σ(Platform_cost_month, 1..m)
```

| Scenario | Annual value (ramped) | Year-1 platform cost | **Payback** |
|---|---|---|---|
| Low (Low loss × Low capture) | ₹7.2 Cr/yr | ₹1.03 Cr | ~5 months |
| **Base** | **₹64 Cr/yr** | **₹1.36 Cr** | **< 1 month** (implementation cost alone) |
| High | ₹332 Cr/yr | ₹2.04 Cr | **< 1 month** |

**Read this honestly, not as a headline:** the sub-month payback in Base/High is an artifact
of the scale gap between an OEM assembly line's throughput value and a software subscription
— it is directionally consistent with how virtual-sensing/APM vendors price against plant
losses, not a claim of literal same-month cash recovery. The **Low** scenario (5 months) is
the number to lead with in the pitch; it survives a skeptic halving every input.

## 5. 3-year view (single line, no re-investment)

| Year | Value (ramped, Base) | Platform cost (Base) | Cumulative net |
|---|---|---|---|
| 1 | ₹64 Cr × (avg ramp ≈ 55%) ≈ ₹35 Cr | ₹1.36 Cr | ₹33 Cr |
| 2 | ₹64 Cr | ₹1.02 Cr (license only) | ₹96 Cr |
| 3 | ₹64 Cr | ₹1.02 Cr | ₹159 Cr |

Multi-line scale-out (GTM §3) multiplies this per additional line onboarded; see
[`GTM_ROADMAP.md`](GTM_ROADMAP.md) (#46) for the pacing.

## 6. Sensitivity — what would change the pitch's answer

Ranked by leverage over the payback conclusion:

1. **`capture_rate`** — the single biggest lever; also the one most within Blindsight's own
   control (accuracy + trust-building UX), which is why the pitch should spend time on the
   validation/backtest story (§2.7 `PLAN.md`), not just the mechanism.
2. **`Loss_ripple`** magnitude (from #42) — plant-specific; must be re-derived per prospect.
3. **License price** — has almost no effect on payback at this loss scale; price on value
   captured, not cost-plus (informs #45 pricing rationale).

## 7. Caveats (state before anyone quotes this externally)

- Built on the PoC's simulated-data cost model (#42), not a measured plant.
- Assumes the pilot plant resembles the stated line profile (40 stations, 35% dark, mixed
  model); re-parameterize for a different scale.
- `capture_rate` is a judgment call today — the M5 backtest (Brier score, false-alarm rate,
  lead time — `docs/VALIDATION.md`) is what will let a future revision replace it with a
  measured number instead of an assumption.

## Handoff

- → Leadership dashboard (#22): render §1–§4 (value, cost, payback) as the ROI tile.
- → Business-case slides (#54): quote **Base** payback and the **Low-scenario** floor
  together — "even in the conservative case, under 6 months."
