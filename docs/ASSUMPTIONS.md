# Stated Assumptions

The brief repeatedly asks us to "state your assumptions clearly." These are directional and
chosen to generalize beyond one plant.

## Line & operations
- **Mixed-model assembly line, ~40 stations** across Body construction → Paint → General
  Assembly, with inter-zone buffers. 2–4 vehicle variants with different work content.
- **Uneven sensor coverage:** ~65% of stations instrumented (robot cells, powered tools with
  PLC feeds), ~35% dark (manual stations, checklist-only). This ratio is a parameter.
- **Scan checkpoints already exist** at zone boundaries and key stations (VIN/barcode/RFID),
  timestamping each vehicle — the backbone of the tomography.
- **Takt time** ~60 s; ~500 units/shift; two shifts/day. Directional, adjustable per scenario.
- Production can be **paused only during scheduled maintenance windows** → any instrumentation
  recommendation must respect rare change windows.

## Integration & operational technology (OT)
- **Read-only integration.** Blindsight consumes existing MES events, PLC/scan feeds, and
  historian data. It **never writes to PLCs or line-control logic** — zero operational risk,
  no retrofit. Recommendations are advisory to humans.
- Data reaches us via a one-way tap / OPC-UA read / MES export — assume an air-gapped or
  DMZ-bridged read path consistent with **IEC 62443** OT-segmentation practice.
- Latency budget: real-time view refreshes on the order of the takt time (seconds), not
  milliseconds — we are a planning/decision layer, not a safety interlock.

## Data protection & governance
- Line/machine telemetry is **not personal data**; operator identifiers are pseudonymized
  before storage, so **GDPR exposure is minimal** (lawful basis: legitimate interest in
  production quality; operator data minimized and access-controlled).
- Full **audit trail**: every estimate, forecast, and recommendation is logged with its inputs,
  model version, and confidence, so decisions are reviewable — matching the brief's emphasis on
  predictions being validated and overridable.
- Recommendations are **human-in-the-loop**: a supervisor accepts/overrides; overrides are
  captured as feedback (§7 validation loop).

## Modelling scope (what we deliberately do NOT do)
- **No photoreal 3D geometry.** We model *flow* (cycle time, blocking/starvation, WIP), not CAD
  — "the detail follows the decision."
- **Proof-of-concept on simulated data.** A ground-truth simulator stands in for real plant
  data; the twin only sees the observable subset. Real historian integration is future work.
