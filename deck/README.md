# Blindsight pitch deck (`role:deck`)

The Round 2 pitch presentation. Self-contained HTML (reveal.js vendored locally) — **runs
offline**, no network, no build step. Closes #48–#56.

## Present

Open `deck/index.html` in any browser (double-click, or serve the folder):

```bash
# from the repo root, if you want a local server:
python -m http.server -d deck 8090   # then open http://127.0.0.1:8090/
```

- **→ / Space** next · **←** back · **Esc** slide overview · **S** speaker view · **F** fullscreen.
- 13 slides + close; ~5–6 min, then the live demo (slide 12 is the demo runsheet).

## Files

| File | What |
|---|---|
| `index.html` | the deck (reveal.js, offline) |
| `outline.md` | narrative arc & slide-by-slide spine (#48) |
| `speaker-notes.md` | per-slide script & timing (#55) |
| `qa.md` | judge-question prep (#56) |
| `assets/reveal/` | vendored reveal.js (offline) |
| `assets/hero-animation.html` | "line is the sensor" visual (slide 3b), from `../../blindsight-animation.html` |

## The live demo (slide 12) + fallback

The demo runs the real dashboard. Bring it up first and keep it on a second tab:

```bash
./.venv/bin/uvicorn api.main:app --port 8000     # then open http://127.0.0.1:8000/
```

Follow the six beats in `../docs/DEMO_SCRIPT.md`. The new capabilities are live:
`/api/live_state/<scenario>` (recursive constraint) and `/api/variants` (mixed-model).

**Record the fallback** (do this before the pitch, never skip):

1. Start the server, open the dashboard, run each scenario (`baseline`, `takt_slip_s14`,
   `torque_drift_s8`, `surge_3x`) through the six beats.
2. Screen-record each run to `deck/assets/fallback-<scenario>.mp4` (e.g. QuickTime ⇧⌘5 on macOS).
3. Test each recording **with the network off**. If a live demo ever stalls, cut to the
   recording and keep narrating — a live failure must never kill the pitch.

> Recordings are large binaries; keep them out of git if the repo has size limits (they're
> in `.gitignore` by default — commit only if the team wants them versioned).
