"""Variant-aware design matrix tests (issue #28, M2).

The twin must recover per-variant service times on a mixed-model line — where different
variants carry different work content — and localize a variant-specific operation to the
right (dark) station, all from travel-time tomography with no sensor on that station.
"""

import numpy as np

from engine.ground_truth_sim import GroundTruthSim
from engine.line import build_default_line, build_variant_line
from engine.observe import extract_observation
from engine.scenarios import load_scenario
from engine.virtual_sensor import estimate_service_times_variant


def _run(variant_ops=None):
    line = build_variant_line(variant_ops) if variant_ops else build_variant_line()
    res = GroundTruthSim(line=line, scenario=load_scenario("baseline")).run()
    return line, res, estimate_service_times_variant(extract_observation(res))


def test_default_line_unchanged_by_variant_fields():
    """A single-model line (no variant content) is byte-identical to before #28."""
    line = build_default_line()
    assert line.variant_content == {} and line.variant_ops == {}
    assert line.variant_mult("A") == 1.0
    assert line.variant_extra_s("A", 8) == 0.0


def test_per_variant_estimates_have_bands_for_every_station():
    line, res, est = _run()
    assert set(est) == {s.id for s in res.line.stations}
    for e in est.values():
        assert set(e.per_variant) == set(line.variants)      # a band per variant
        for b in e.per_variant.values():
            assert b.lo <= b.mean <= b.hi                     # never a bare number


def test_dark_per_variant_mape_tracks_truth():
    line, res, est = _run()
    dark = res.line.dark_stations()
    errs = [abs(est[j].per_variant[v].mean - res.true_mean_cycle_variant[j][v])
            / res.true_mean_cycle_variant[j][v]
            for j in dark for v in line.variants
            if v in res.true_mean_cycle_variant[j]]
    mape = 100 * float(np.mean(errs))
    assert mape < 25, f"dark per-variant MAPE too high: {mape:.0f}%"


def test_variant_specific_operation_is_localized():
    """The optioned variant (sunroof at S19, trim at S24) must read highest there."""
    line, res, est = _run()
    for variant, ops in line.variant_ops.items():
        for station_id in ops:
            here = est[station_id].per_variant
            others = [here[o].mean for o in line.variants if o != variant]
            assert here[variant].mean > max(others), (
                f"S{station_id}: variant {variant} carries the extra op but is not "
                f"estimated highest ({here[variant].mean} vs {others})")
            # and the excess is materially above the base line, not noise
            assert here[variant].mean - max(others) > 5


def test_handles_two_and_four_variants():
    for ops in ({"X": {}, "Y": {19: 20.0}},
                {"A": {}, "B": {19: 18.0}, "C": {24: 12.0}, "D": {19: 10.0, 24: 6.0}}):
        line, res, est = _run(ops)
        assert len(line.variants) == len(ops)
        dark = res.line.dark_stations()
        errs = [abs(est[j].per_variant[v].mean - res.true_mean_cycle_variant[j][v])
                / res.true_mean_cycle_variant[j][v]
                for j in dark for v in line.variants
                if v in res.true_mean_cycle_variant[j]]
        assert 100 * float(np.mean(errs)) < 25
