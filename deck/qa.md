# Q&A / judge-question prep (#56)

Anticipated questions, with honest answers grounded in the repo.

**"Is this real data or simulated?"**
Simulated ground truth (a discrete-event simulator we built) — Round 2 asks for the mechanism
on realistic production data. The key discipline: the twin consumes only the *observable*
subset (instrumented states + scan timestamps) via an enforced boundary (`engine/observe.py`);
it never peeks at ground truth. That's why the validation numbers are meaningful.

**"How accurate on stations with no sensor, really?"**
3.3% cycle-time MAPE on dark stations (1.9% on instrumented — the noise floor), and 100% of
our 80% error bars contain the truth. Reproducible: `python -m engine.validate`.

**"Won't it cry wolf?"**
0% false-alarm rate across 12 clean baseline shifts. We report that first because false alarms
are what make crews ignore a system.

**"What can't it do?" (asked or not, volunteer one honest limit)**
On a no-overtaking line, a *globally faster* variant is pinned behind slower units, so its true
speed isn't identifiable — we surface that as a wide/one-sided band rather than a false number.
The forecast uses a bottleneck-rate metamodel, not a full DES per replication (a deliberate
speed/fidelity trade, validated against the DES).

**"How is this different from MES / existing OEE dashboards?"**
Those are rear-view: they report what already happened, and only at instrumented stations. We
*estimate the dark stations*, *forecast* the constraint 2h out, and *prescribe* an action — on
the same data, no new hardware.

**"What does deployment actually require?"**
A read-only tap on the scan log + PLC feed. No new sensors, no line downtime. ~$25k one-time
integration, $8k/line/month.

**"Why should we believe the ROI?"**
Base ~$7.5M/yr/line is 45% capture of a modeled $16.5M line-blindness loss; the low-case floor
(~$0.85M/yr) still pays back in ~5 months. The sub-month base payback is because loss scale is
large — we say that plainly (`docs/ROI_MODEL.md`).

**"Does it scale to a real 200-station plant / multiple lines?"**
The engine is per-segment and Monte-Carlo over the parameter posterior — milliseconds per
forecast. Scaling is more scans and more segments, not a new method.

**"What's the moat?"**
The mechanism (flow-physics inference + value-of-information roadmap) and being retrofit-free.
Competitors sell sensors; we sell seeing without them.

**"What's next after the pilot?"**
Online particle filter is already in (live regime tracking); next is variant-aware design
matrix at plant scale and a Kalman/particle fusion of instrumented transitions per tick.
