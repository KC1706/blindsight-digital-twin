# Pricing & Commercial Model

**Issue:** #45 · **Aligns with:** [`GTM_ROADMAP.md`](GTM_ROADMAP.md) (#46) phases ·
**Referenced by:** [`ROI_MODEL.md`](ROI_MODEL.md) §3 (platform cost side).

Priced against **value captured** (a fraction of the cost of blindness, `COST_OF_BLINDNESS.md`),
not cost-plus off engineering effort — `ROI_MODEL.md` §6 shows license price barely moves the
payback conclusion at this loss scale, so pricing should optimize for adoption speed and
reference-ability, not for squeezing the early tiers.

## 1. Model: SaaS per-line, with an on-prem option for OT-sensitive customers

| Deployment | When offered | Why |
|---|---|---|
| **SaaS (default)** | PoC, Pilot, most of Scale | Faster to deploy (read-only tap only, `ASSUMPTIONS.md`); Blindsight owns upgrades/model versioning centrally |
| **On-prem / VPC-hosted** | Scale, on request — typically OEMs with strict data-residency or OT-segmentation policy that forbids any external egress | Same read-only architecture, deployed inside the customer's DMZ; priced at a premium to cover deployment/ops overhead (§3) |

Unit of sale is **per production line**, not per seat or per station — matches how the value
(`COST_OF_BLINDNESS.md`) and the ROI model (`ROI_MODEL.md`) are both scoped per line.

## 2. Pricing tiers by GTM phase

| Phase (`GTM_ROADMAP.md`) | Tier | Price | Term | Rationale |
|---|---|---|---|---|
| **Phase 1 — PoC** | Not sold | $0 | N/A | This prototype; proves the mechanism before any commercial conversation |
| **Phase 2 — Pilot** | Pilot | **Fixed fee, $40,000** one-time (implementation only, mid-point of `ROI_MODEL.md` §3 range) + **no license fee** during the pilot term | 3 months (matches `GTM_ROADMAP.md` Phase 2 duration) | Removes price as a pilot-adoption barrier; the ask is data access and a shadow-mode window, not budget approval |
| **Phase 3 — Scale, Starter** | 1–3 lines | **$10,000/line/month** (SaaS, `ROI_MODEL.md` §3 Base) + $40,000 one-time implementation per new line | 12-month term | Matches ROI model's Base case exactly, so the payback claim in the pitch and the actual quote never diverge |
| **Phase 3 — Scale, Multi-line** | 4–15 lines | **$8,500/line/month** (volume discount) | 12-month term, auto-renew | Implementation cost amortizes (shared integration work across lines at one site) |
| **Phase 3 — Scale, Enterprise / multi-site** | 16+ lines or on-prem | **Custom** (starts at $8,000/line/month, `ROI_MODEL.md` Low bound) + on-prem premium | Multi-year | On-prem deployment ops cost recovered via the premium, not the per-line rate |

## 3. On-prem premium

On-prem/VPC deployment adds a flat **+$5,000/month** platform fee (covers dedicated
infra/ops) on top of the per-line rate above. This keeps the per-line rate comparable across
deployment modes so the ROI model's Low/Base/High license figures ($8k/$10k/$15k) still bound
the total: the High end of that range is effectively "on-prem, small line count."

## 4. What's included at every tier

- Full mechanism (virtual sensing, forecast, prescription, defect trace) and all 3 dashboard
  views (floor / plant-manager / leadership, `PERSONAS.md`).
- Read-only integration support (one-time, within the implementation fee).
- Backtest/validation reporting (`VALIDATION.md`-class metrics) as a standing feature, not an
  add-on — trust-building is core to the product, not upsell.
- VoI-ranked instrumentation roadmap (which dark stations to sensor next) — this is a retention
  lever: as a customer instruments more stations, `capture_rate` in `ROI_MODEL.md` rises and the
  value case strengthens, without a corresponding price increase.

## 5. What is priced separately (not included)

- New sensor hardware if a customer chooses to act on a VoI recommendation (third-party
  procurement — Blindsight recommends, does not sell, hardware).
- On-prem infrastructure premium (§3).
- Custom integration beyond a standard read-only tap (scoped case-by-case).

## 6. Commercial risk guard

Per `RISK_REGISTER.md` #9 (vendor continuity), the pilot and every subsequent contract commits
to a **data-portability clause**: the customer's raw scan/MES exports remain theirs, so removal
of Blindsight is a no-op for the line — a stated commercial term, not just an architectural
fact, because prospects will ask.

## Handoff

- → `ROI_MODEL.md` §3: license figures already match this file exactly (Starter tier = Base
  case) — no reconciliation needed if either file changes; update both together.
- → `GTM_ROADMAP.md`: pilot terms (§2) and phase pacing are the same document's source of truth
  for phase-by-phase commercial terms.
- → Presentation (#54): quote the Starter tier ($10,000/line/month) as the headline number;
  keep Pilot/Enterprise terms in the appendix for Q&A (#56).
