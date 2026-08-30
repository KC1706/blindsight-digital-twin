"""Online state estimation — a live, recursive posterior (issue #29, METHODS §2.3).

The batch tomography (`virtual_sensor`) answers "what were the station cycle times over the
shift?". The real-time floor view needs a different thing: a *recursive* posterior over the
live line state that updates every tick and reacts to regime changes (an operator swap, a
tool drift) within minutes — not one that has to see the whole shift first.

We run a **Rao-Blackwellized particle filter**. The expensive latent — where every vehicle
is — is not sampled: vehicle positions are pinned by the scan timestamps (conditionally
deterministic given the observations), so particles carry only the cheap latent, the vector
of per-segment effective service times. Each tick:

- **predict**: every particle random-walks its segment times, plus a rare heavy-tailed
  *jump* so the filter can snap to a regime change instead of crawling toward it;
- **update**: when a vehicle completes a segment (a fresh downstream scan lands), its travel
  time is a measurement of that segment's service time; particles are reweighted by the
  Gaussian likelihood and resampled when the effective sample size collapses.

The per-segment posterior is attributed to stations exactly as the batch estimator does — the
flow-identified bottleneck in a segment carries the segment's excess — so the live view and
the shift report tell the same story, one recursively and one in hindsight.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .observe import Observation
from .schemas import Band


@dataclass
class _Completion:
    seg: tuple[int, int]
    travel: float


def _completions_by_tick(obs: Observation, duration_s: float) -> dict[int, list[_Completion]]:
    """Bucket each vehicle's segment completions at the tick of its *downstream* scan.

    A vehicle that scans checkpoint a then checkpoint b has completed segment (a, b) at
    time t_b, and its travel time t_b - t_a measures that segment's service+wait.
    """
    out: dict[int, list[_Completion]] = {}
    for sc in obs.vehicle_scans.values():
        cps = sorted(sc)
        for a, b in zip(cps, cps[1:]):
            if sc[b] > sc[a]:
                out.setdefault(int(sc[b]), []).append(_Completion((a, b), sc[b] - sc[a]))
    return out


class LiveFilter:
    """Recursive per-segment service-time posterior, updated one tick at a time."""

    def __init__(self, obs: Observation, n_particles: int = 400, seed: int = 0,
                 walk_s: float = 0.4, jump_prob: float = 0.02, jump_s: float = 8.0,
                 meas_noise_s: float = 12.0):
        self.obs = obs
        self.line = obs.line
        self.rng = np.random.default_rng(seed)
        self.P = n_particles
        self.walk_s = walk_s
        self.jump_prob = jump_prob
        self.jump_s = jump_s
        self.meas_noise = meas_noise_s

        self.segments = list(zip(self.line.checkpoints(), self.line.checkpoints()[1:]))
        self.seg_index = {seg: i for i, seg in enumerate(self.segments)}
        self.S = len(self.segments)

        # prior: a segment's service time ≈ its span × a nominal per-station cycle
        nominal = float(np.median(list(obs.measured_cycle_s.values()))) \
            if obs.measured_cycle_s else 0.85 * self.line.takt_s
        span = np.array([b - a for a, b in self.segments], float)
        self.prior = span * nominal
        # particles: (P, S) segment service times; weights: (P,)
        self.particles = self.prior[None, :] + self.rng.normal(
            0, 0.05 * self.prior, size=(self.P, self.S))
        self.particles = np.clip(self.particles, 1.0, None)
        self.weights = np.full(self.P, 1.0 / self.P)

    # -------------------------------- one tick -------------------------------- #
    def predict(self):
        self.particles += self.rng.normal(0, self.walk_s, size=self.particles.shape)
        jump = self.rng.random(self.particles.shape) < self.jump_prob
        self.particles += jump * self.rng.normal(0, self.jump_s, size=self.particles.shape)
        np.clip(self.particles, 1.0, None, out=self.particles)

    def update(self, completions: list[_Completion]):
        if not completions:
            return
        logw = np.log(self.weights + 1e-300)
        for c in completions:
            si = self.seg_index.get(c.seg)
            if si is None:
                continue
            resid = c.travel - self.particles[:, si]      # travel ≥ service (wait ≥ 0)
            # one-sided-ish Gaussian: service under travel is expected, well over is unlikely
            logw += -0.5 * (resid / self.meas_noise) ** 2
        logw -= logw.max()
        w = np.exp(logw)
        s = w.sum()
        if s <= 0 or not np.isfinite(s):
            self.weights = np.full(self.P, 1.0 / self.P)
            return
        self.weights = w / s
        ess = 1.0 / np.sum(self.weights ** 2)
        if ess < self.P / 2:                              # resample when degenerate
            idx = self.rng.choice(self.P, self.P, p=self.weights)
            self.particles = self.particles[idx]
            self.weights = np.full(self.P, 1.0 / self.P)

    # ----------------------------- read the posterior ------------------------- #
    def segment_posterior(self) -> dict[tuple[int, int], Band]:
        out = {}
        for seg, si in self.seg_index.items():
            col = self.particles[:, si]
            mean = float(np.average(col, weights=self.weights))
            # weighted percentiles via resample for a quick, honest band
            samp = self.rng.choice(col, size=512, p=self.weights)
            lo, hi = np.percentile(samp, [5, 95])
            out[seg] = Band(mean=round(mean, 2), lo=round(float(lo), 2), hi=round(float(hi), 2))
        return out

    def relative_load(self) -> np.ndarray:
        """Per-segment posterior travel time relative to its prior (0 = at prior)."""
        return np.array([np.average(self.particles[:, i], weights=self.weights) / self.prior[i]
                         for i in range(self.S)]) - 1.0

    def hottest_segment(self) -> tuple[int, int]:
        """The live constraint segment, via the blocked→starved boundary.

        A slow station blocks everything upstream (travel inflated) and starves everything
        downstream (travel fast), so blocking *propagates upstream* — the upstream segments
        are inflated at least as much as the constraint. The constraint sits at the boundary:
        the segment after which relative load drops the most going downstream. Robust to a
        naturally-slow tail segment, which shows no such downstream drop.
        """
        rel = self.relative_load()
        nxt = np.append(rel[1:], 0.0)                # downstream of the last segment: starved
        drop = rel - nxt                             # blocked→starved boundary = biggest drop
        return self.segments[int(np.argmax(drop))]


def run_live(obs: Observation, duration_s: float, n_frames: int = 80,
             seed: int = 0, **kw) -> list[dict]:
    """Stream the filter tick-by-tick over the shift, sampling the posterior into frames.

    Returns one frame per sample point with the per-segment posterior and the current live
    constraint — the recursive counterpart to the batch cycle-time estimates.
    """
    filt = LiveFilter(obs, seed=seed, **kw)
    comps = _completions_by_tick(obs, duration_s)
    dur = int(duration_s)
    sample_at = {int(round((dur - 1) * f / (n_frames - 1))) for f in range(n_frames)}
    frames: list[dict] = []
    for t in range(dur):
        filt.predict()
        filt.update(comps.get(t, []))
        if t in sample_at:
            post = filt.segment_posterior()
            hot = filt.hottest_segment()
            frames.append({
                "t_s": t, "t_min": round(t / 60),
                "hot_segment": list(hot),
                "segments": [{"a": a, "b": b, "mean": post[(a, b)].mean,
                              "lo": post[(a, b)].lo, "hi": post[(a, b)].hi}
                             for (a, b) in filt.segments],
            })
    return frames
