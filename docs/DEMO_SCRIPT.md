# Prototype Demo Storyline

A ~4-minute live run that proves the mechanism, mapped to the three stakeholder views. Each
beat is a thing the judge *sees happen on screen*, not a slide.

## Beat 0 — The blind line (15s)
Open the **Floor Supervisor** view: live line map, ~40 stations. Point out that ~35% are grey
(dark / no sensor) — including the ones that matter. "This is what MES shows you: green lights,
no idea what the manual stations are doing."

## Beat 1 — Seeing the invisible (45s) · *virtual sensing*
Toggle **Blindsight on**. The dark stations light up with *estimated* cycle times **and error
bars**. Split-screen a "truth" overlay (only for the demo) to show estimates track reality at
dark stations. Headline number: *"MAPE X% at stations with no sensor."*

## Beat 2 — The takt slip (45s) · *forecast* — scenario `takt_slip_s14`
Station 14 (dark, manual) starts drifting over takt. Upstream blocks, downstream starves; the
bottleneck signal fingers S14 with no sensor on it. Switch to **Plant Manager** view: the
2-hour forecast says *"S14 becomes the binding constraint in ~90 min → 23 units, P50."* with a
P10–P90 band.

## Beat 3 — The recommendation (30s) · *prescription*
Blindsight ranks levers: *"Move one operator S12→S14 → recover ~19 units (confidence 92%)."*
Supervisor clicks **Accept**; forecast re-runs and the constraint flattens. Then a click
**Override** — show the audit log capturing it.

## Beat 4 — The drifting tool (30s) · *defect trace* — scenario `torque_drift_s8`
An SPC/CUSUM alarm fires at Station 8 (torque 4% out of spec). Blindsight names the **exact
VINs** processed during the drift window and where each is *right now* — a containment list,
before end-of-line audit.

## Beat 5 — Do we trust it? (30s) · *validation*
Open the **validation panel**: calibration curve, false-alarm rate, lead-time distribution
from backtesting. "We don't ask you to trust it — here's it scoring itself on held-out shifts."

## Beat 6 — The business case (30s) · *leadership view + VoI*
Switch to **Leadership** view: units/$ saved per shift, and *"instrument these 3 stations first"*
with the marginal error reduction each buys. Close on the ROI of a **retrofit-free** rollout.

## Fallback
Pre-recorded run of each scenario in `scenarios/` so a live failure never kills the pitch.
