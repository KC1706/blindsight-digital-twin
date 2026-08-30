# Blindsight — pitch deck outline & narrative arc (#48)

**Team DarkShield · Accenture Innovation Challenge 2026 · Round 2 · Track 4 (DigitalTwin.ai)**

The spine everything else hangs off. One narrative, one voice (see `../video-script.md`,
`../vo-script-clean.md`): **factual, not hyped — let the facts be the drama.** Every proof
slide traces to something real in the repo.

Target: **~5–6 min of slides + ~4 min live demo**. The demo is the centerpiece; the deck
frames it.

## Arc

1. **Hook** — a real blindness (the 9:14am torque drift; found at 2pm, hundreds of cars carry it).
2. **Problem** — sensor coverage is uneven; the manual stations that vary most are the dark ones.
3. **Insight** — *the line is the sensor.* Infer the invisible from the physics of flow.
4. **Mechanism** — five moves: virtual sensing → forecast → prescribe → defect trace → trust.
5. **Proof** — the twin scores itself: dark-station MAPE, 0% false alarms, 10× forecast.
6. **Reach** — live & recursive, and mixed-model (variant) work content, no new sensors.
7. **Business** — retrofit-free, sub-month payback, "instrument these 3 first."
8. **Ask** — the pilot.

## Slide-by-slide (12 slides)

| # | Slide | One-line message | Proof source |
|---|---|---|---|
| 1 | Title | Blindsight — the line is the sensor | — |
| 2 | The blind line | ~35% of stations are dark; the bottleneck hides there | `line.py`, DEMO Beat 0 |
| 3 | The insight | The line already knows — read it differently | `hero-animation.html`, README |
| 4 | How it works | 5 moves on sensors you already have | PLAN §4, METHODS |
| 5 | See the invisible | Dark cycle times with error bars — MAPE **3.3%** | VALIDATION.md |
| 6 | Forecast the jam | takt_slip_s14: dark S14 fingered, ~15 units at risk | VALIDATION.md |
| 7 | Live & recursive | Tracks a regime change in ~5 min, live (#29) | `online_filter.py` |
| 8 | Mixed-model | Per-variant work content, no sensor (#28) | `virtual_sensor.py` |
| 9 | Do we trust it? | 0% false alarms · CRPS 10× · 100% band coverage | VALIDATION.md |
| 10 | Business case | ~$7.5M/yr/line · retrofit-free · sub-month payback | ROI_MODEL.md |
| 11 | Roadmap + ask | Phased rollout; instrument these 3 first | GTM_ROADMAP.md, VoI |
| 12 | Live demo | 6 beats on the real dashboard (fallback recorded) | DEMO_SCRIPT.md |

## Timing budget

| Section | Slides | Time |
|---|---|---|
| Hook + problem | 1–2 | 0:45 |
| Insight + mechanism | 3–4 | 1:15 |
| Proof + reach | 5–9 | 2:00 |
| Business + ask | 10–11 | 1:15 |
| **Live demo** | 12 | **4:00** |
| Close / Q&A handoff | — | 0:30 |

## The three things a judge must remember

1. **The line is the sensor** — no retrofit, no new hardware.
2. It **estimates the stations nothing can see**, and **says so honestly** (error bars, 0% false alarms).
3. It turns that into **money and a costed roadmap** — sub-month payback, "instrument these 3 first."
