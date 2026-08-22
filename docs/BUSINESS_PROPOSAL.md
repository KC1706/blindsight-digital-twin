# Business Proposal — Blindsight (outline)

> Skeleton to be filled during M8. Structure follows exactly what Round 2 asks to deliver:
> "problem framing, solution design, target users, business case and impact, a phased roadmap,
> and key risks with mitigations."

## 1. Problem framing
- Uneven sensor coverage; manual stations are both the likely bottleneck and the blind spot.
- MES/PLC dashboards are rear-view mirrors (post-hoc, after the stop).
- Cost of blindness: late defect detection (whole batches contaminated), unmanaged bottlenecks
  (starving/blocking ripple), reactive firefighting. *(quantify per assumptions)*

## 2. Solution design
- "The line is the sensor": virtual sensing (blocked/starved + travel-time tomography) →
  probabilistic forecast → prescriptive action → defect trace → validated & self-scoring.
- Retrofit-free, read-only, human-in-the-loop. (See `METHODS.md`, `ASSUMPTIONS.md`.)

## 3. Target users
- **Floor supervisor** — real-time constraint + next action.
- **Plant manager** — 2-hour planning horizon + shift trends.
- **Leadership** — ROI + instrumentation roadmap.

## 4. Business case & impact
- Value levers: throughput recovered, scrap/rework avoided (early defect containment), deferred
  capex (instrument 3 stations, not 40).
- Illustrative ROI model *(to compute)*: units recovered/shift × margin/unit − platform cost.
- Payback dominated by avoided instrumentation + one prevented batch defect.

## 5. Phased roadmap
- **Phase 1 (PoC, this prototype):** one line, simulated data, mechanism proven.
- **Phase 2 (Pilot):** one real line, read-only historian/MES tap, shadow-mode validation.
- **Phase 3 (Scale):** multi-line/multi-site; per-site recalibration; VoI-driven instrumentation.

## 6. Key risks & mitigations
| Risk | Mitigation |
|---|---|
| Dark-station estimates too uncertain to act on | Error bars everywhere; abstain below confidence threshold; VoI tells you where a cheap sensor removes the doubt |
| False alarms erode floor trust | Backtested false-alarm rate reported; conservative thresholds; shadow-mode before go-live |
| OT/security concerns | Read-only, no PLC writes, IEC-62443-aligned segmentation |
| Site-to-site variation | Per-site recalibration; hierarchical priors transfer structure, not exact values |
| Change management (fatigued staff ignore it) | One clear action, not a dashboard to interpret; capture overrides as feedback |
