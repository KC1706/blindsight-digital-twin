"""Online filter tests (issue #29, M2) — the live recursive posterior.

The filter must maintain a per-segment posterior that updates every tick and reacts to an
injected regime change within a few minutes — not one that needs the whole shift first.
"""

import numpy as np

from engine.ground_truth_sim import GroundTruthSim
from engine.observe import extract_observation
from engine.online_filter import LiveFilter, run_live, _completions_by_tick
from engine.scenarios import load_scenario

DETECT_WITHIN_S = 600          # "within N ticks": react inside 10 minutes of onset


def _obs(name):
    res = GroundTruthSim(scenario=load_scenario(name)).run()
    return res, extract_observation(res)


def test_posterior_present_and_bracketing_every_tick():
    res, obs = _obs("baseline")
    filt = LiveFilter(obs, seed=0)
    comps = _completions_by_tick(obs, res.duration_s)
    for t in range(0, 400):                       # a live posterior exists from tick 1
        filt.predict()
        filt.update(comps.get(t, []))
        post = filt.segment_posterior()
        assert post, "no segments in posterior"
        for b in post.values():
            assert b.lo <= b.mean <= b.hi         # never a bare number


def test_tracks_injected_regime_change_within_N_ticks():
    """takt_slip_s14 injects +18s at dark S14 (segment 8->16) at t=1800; the filter's
    posterior for that segment must rise well above its pre-shift level within N ticks."""
    res, obs = _obs("takt_slip_s14")
    onset = next(e.at_s for e in res.scenario.events if e.station_id == 14)
    filt = LiveFilter(obs, seed=0)
    comps = _completions_by_tick(obs, res.duration_s)
    si = filt.seg_index[(8, 16)]

    baseline = None
    detected_at = None
    for t in range(int(res.duration_s)):
        filt.predict()
        filt.update(comps.get(t, []))
        mean = float(np.average(filt.particles[:, si], weights=filt.weights))
        if t == int(onset) - 1:
            baseline = mean
        if baseline is not None and detected_at is None and t > onset and mean > baseline + 8:
            detected_at = t
            break

    assert detected_at is not None, "filter never detected the regime change"
    assert detected_at - onset <= DETECT_WITHIN_S, \
        f"detection lag {detected_at - onset:.0f}s exceeds {DETECT_WITHIN_S}s"


def test_live_constraint_localizes_to_the_shifted_segment():
    res, obs = _obs("takt_slip_s14")
    filt = LiveFilter(obs, seed=0)
    comps = _completions_by_tick(obs, res.duration_s)
    for t in range(int(res.duration_s)):
        filt.predict()
        filt.update(comps.get(t, []))
    assert filt.hottest_segment() == (8, 16)     # the segment holding the shifted S14


def test_run_live_frames_shape():
    res, obs = _obs("takt_slip_s14")
    frames = run_live(obs, res.duration_s, n_frames=40, seed=0)
    assert len(frames) == 40
    f = frames[-1]
    assert set(f) >= {"t_s", "t_min", "hot_segment", "segments"}
    assert len(f["segments"]) == len(obs.line.checkpoints()) - 1
    for seg in f["segments"]:
        assert seg["lo"] <= seg["mean"] <= seg["hi"]
