# Risk, Compliance & OT-Security Register

**Issue:** #47 · **Extends:** [`ASSUMPTIONS.md`](ASSUMPTIONS.md) · **Feeds:**
[`BUSINESS_PROPOSAL.md`](BUSINESS_PROPOSAL.md) §6.

`ASSUMPTIONS.md` states the read-only, human-in-the-loop, IEC-62443-aligned posture Blindsight
is built on. This register turns those assumptions into named risks with owners and
mitigations, plus the compliance posture a prospect's security/legal team will ask about.

## 1. Top risks & mitigations

| # | Risk | Category | Likelihood | Impact | Mitigation | Residual |
|---|---|---|---|---|---|---|
| 1 | Dark-station estimate is wrong with high confidence → bad action taken | Model | Medium | High | Error bars on every estimate; abstain below a stated confidence threshold; backtested calibration reported (`VALIDATION.md`) before any pilot go-live | Low |
| 2 | False alarms erode floor trust, supervisors start ignoring the tool | Adoption | Medium | High | False-alarm rate is a first-class reported metric (0% on clean baselines, `VALIDATION.md`); conservative alert thresholds; shadow-mode period before the tool drives action | Low |
| 3 | OT/security team blocks integration over PLC-write fear | OT security | Low | High | Architecture is **read-only by construction** — no PLC write path exists to remove; one-way tap / OPC-UA read / MES export, IEC-62443 zone/conduit segmented (§2 below) | Low |
| 4 | Data tap becomes a pivot point into the OT network | OT security | Low | Critical | DMZ-bridged or air-gapped read path (no inbound OT connection); Blindsight compute sits in IT/cloud DMZ, never inside the OT zone; no credentials flow from Blindsight into PLC/SCADA | Low |
| 5 | Personal/operator data exposure (GDPR or equivalent) | Data/compliance | Low | Medium | Operator identifiers pseudonymized at ingestion; line/machine telemetry itself is not personal data; lawful basis = legitimate interest in production quality, data minimized (§2) | Low |
| 6 | Model/version drift — a silently changed estimator changes plant decisions | Governance | Medium | Medium | Every estimate, forecast, and recommendation logged with inputs, model version, and confidence (full audit trail per `ASSUMPTIONS.md`); reviewable after the fact | Low |
| 7 | Site-to-site variation makes a pretrained model wrong at a new plant | Model | High | Medium | Per-site recalibration required before go-live; hierarchical priors transfer *structure* (which variables matter), not point values, across sites | Medium |
| 8 | Change management — fatigued floor staff ignore another dashboard | Adoption | Medium | Medium | Single clear next-best-action, not a dashboard to interpret; overrides captured as feedback and fed back into the validation loop | Low |
| 9 | Vendor lock-in / continuity concern if Blindsight (the company) fails | Commercial | Low | Medium | Read-only integration means removal is a no-op for the line (nothing to unwind); recommend the customer retains raw scan/MES exports independently | Low |
| 10 | Scan-checkpoint or MES feed itself has gaps/latency, degrading estimates silently | Data quality | Medium | Medium | Confidence bands widen automatically with sparser input (tomography residual variance, §2.3 `PLAN.md`); a stale-feed watchdog alerts instead of failing silently | Low |

## 2. Compliance posture per jurisdiction

| Jurisdiction / regime | Relevant framework | Posture | Rationale |
|---|---|---|---|
| **EU** | GDPR | Minimal exposure | Line/machine telemetry is not personal data; operator IDs pseudonymized before storage; lawful basis is legitimate interest in production quality (Art. 6(1)(f)); no special-category data processed |
| **US** (state privacy — CCPA/CPRA-class) | State consumer/employee privacy laws | Minimal exposure | Same minimization/pseudonymization posture; no consumer data touched; employee-data provisions addressed by pseudonymization + access control |
| **Any jurisdiction, OT/ICS** | IEC 62443 | Aligned by design | Read-only, zone/conduit-segmented data path; Blindsight never issues a write to control logic — it sits outside the control zone entirely, consistent with 62443's segmentation model |
| **Automotive-sector quality** | IATF 16949-class traceability expectations | Supportive | The audit trail (every estimate/forecast/recommendation logged with model version + confidence) strengthens, not weakens, existing quality-traceability requirements |
| **General cybersecurity posture** | NIST CSF (illustrative mapping) | Supportive | *Identify* (asset = read-only tap only), *Protect* (DMZ segmentation, no inbound OT path), *Detect* (stale-feed watchdog), *Respond/Recover* (no OT footprint to recover — worst case is the dashboard going dark, not a line stoppage) |

## 3. What we are explicitly not claiming

This is a PoC-stage register built on stated assumptions, not a completed third-party security
audit or a signed DPA. Before a real pilot: (a) the target plant's actual data-tap mechanism
must be reviewed against its own OT security policy, (b) a real DPA/data-processing addendum
must be executed if any field turns out to be personal data at that specific site, (c) risk #7
(site-to-site variation) should be re-scored once the first pilot's recalibration effort is
measured.

## Handoff

- → `BUSINESS_PROPOSAL.md` §6: this table replaces the five-row placeholder risk table with the
  full register; quote row 1–4 and 7–8 as the pitch's risk slide (highest severity × most
  pitch-relevant).
- → Presentation (#53/#56 Q&A prep): rows 3–5 (OT security, data tap, GDPR) are the most likely
  judge questions — keep the one-line mitigation ready verbatim.
