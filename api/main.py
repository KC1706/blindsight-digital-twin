"""Blindsight API (issues #18, #19).

Serves the engine's analysis to the dashboard:
- REST snapshots per scenario (state, estimates, forecast, recommendation, defect, validation)
- a websocket that streams the live line-map playback (#19)
- the static dashboard at /

Run:  ./.venv/bin/uvicorn api.main:app --reload   (then open http://127.0.0.1:8000)
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from engine.pipeline import analyze, live_frames
from engine.scenarios import available
from engine.validate import build_report, value_of_information

app = FastAPI(title="Blindsight", version="1.0")
WEB = Path(__file__).resolve().parent.parent / "web"


@app.get("/api/scenarios")
def scenarios():
    return {"scenarios": available()}


@app.get("/api/analysis/{scenario}")
def analysis(scenario: str):
    return analyze(scenario)


@app.get("/api/validation")
def validation():
    r = build_report()
    voi = value_of_information("takt_slip_s14")
    return {
        "mape_instrumented": r.cycle_time_mape_instrumented,
        "mape_dark": r.cycle_time_mape_dark,
        "false_alarm_rate": r.false_alarm_rate,
        "forecast_crps": r.forecast_crps,
        "median_lead_time_min": round(r.median_lead_time_s / 60),
        "value_of_information": voi,
    }


@app.websocket("/ws/live/{scenario}")
async def ws_live(ws: WebSocket, scenario: str):
    await ws.accept()
    try:
        frames = live_frames(scenario)
        while True:                          # loop the playback
            for fr in frames:
                await ws.send_json(fr)
                await asyncio.sleep(0.12)
            await asyncio.sleep(0.6)
    except WebSocketDisconnect:
        return
    except Exception:
        await ws.close()


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


if WEB.exists():
    app.mount("/static", StaticFiles(directory=WEB), name="static")
