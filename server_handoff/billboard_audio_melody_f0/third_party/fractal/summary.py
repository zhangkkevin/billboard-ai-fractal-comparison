from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from .dfa import dfa_alpha, _default_nvals
from .mfdfa import mfdfa_spectrum, _default_lag

DEFAULT_QVALS = np.linspace(-5, 5, 21).tolist()  # SAFE: [-5, 5], 21 points, includes 0


def get_fractal_params_for_n(n: int) -> Dict[str, Any]:
    """Return fractal parameter metadata for a signal of length N (SAFE policy)."""
    n_min = max(16, int(np.floor(n * 0.01)))
    n_max = int(np.floor(n * 0.10))
    nvals = _default_nvals(n)
    lag = _default_lag(n)
    return {
        "N": int(n),
        "min_scale": int(n_min),
        "max_scale": int(n_max),
        "number_of_scales": int(nvals.size),
        "q_range": {"min": float(np.min(DEFAULT_QVALS)), "max": float(np.max(DEFAULT_QVALS)), "n_points": len(DEFAULT_QVALS)},
        "segments_at_max_scale": int(n // n_max) if n_max > 0 else 0,
        "policy": "SAFE",
    }


def compute_fractal_descriptors_1d(
    x: np.ndarray,
    *,
    qvals: Sequence[float] = DEFAULT_QVALS,
    compute_mfdfa: bool = True,
) -> Dict[str, Any]:
    """
    Compute a single dict of descriptors for a 1D signal.

    Returns keys (requested shape):
      { alpha_dfa, alpha_width, alpha_peak, W_L, W_R, B, R,
        spectrum_skew, delta_Hq, H_q, alpha_curve, f_alpha_curve }
    plus a few extra fields for debugging/metadata.
    """
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    out: Dict[str, Any] = {}

    out["alpha_dfa"] = float(dfa_alpha(x))

    # MFDFA is optional (dependency may not be installed)
    if compute_mfdfa:
        try:
            spec = mfdfa_spectrum(x, qvals=qvals, order=1)
            out["mfdfa_ok"] = True
            out["mfdfa_error"] = None
            out["alpha_width"] = float(spec["alpha_width"])
            out["alpha_peak"] = float(spec["alpha_peak"])
            out["W_L"] = float(spec["W_L"])
            out["W_R"] = float(spec["W_R"])
            out["B"] = float(spec["B"])
            out["R"] = float(spec["R"])
            out["spectrum_skew"] = float(spec["spectrum_skew"])
            out["delta_Hq"] = float(spec["delta_Hq"])
            out["H_q"] = spec["H_q"]
            out["alpha_curve"] = spec["alpha_curve"]
            out["f_alpha_curve"] = spec["f_alpha_curve"]
            out["qvals"] = spec["qvals"]
        except Exception as exc:
            # Keep DFA even if MFDFA fails on a particular signal.
            out["mfdfa_ok"] = False
            out["mfdfa_error"] = str(exc)
            out["alpha_width"] = None
            out["alpha_peak"] = None
            out["W_L"] = None
            out["W_R"] = None
            out["B"] = None
            out["R"] = None
            out["spectrum_skew"] = None
            out["delta_Hq"] = None
            out["H_q"] = None
            out["alpha_curve"] = None
            out["f_alpha_curve"] = None
            out["qvals"] = sorted(set(list(qvals) + [0.0]))
    else:
        out["mfdfa_ok"] = False
        out["mfdfa_error"] = "mfdfa_disabled"
        out["alpha_width"] = None
        out["alpha_peak"] = None
        out["W_L"] = None
        out["W_R"] = None
        out["B"] = None
        out["R"] = None
        out["spectrum_skew"] = None
        out["delta_Hq"] = None
        out["H_q"] = None
        out["alpha_curve"] = None
        out["f_alpha_curve"] = None
        out["qvals"] = sorted(set(list(qvals) + [0.0]))

    return out


def describe_distribution(values: Sequence[float], percentiles: Sequence[float] = (5, 20, 50, 80, 95)) -> Dict[str, float]:
    arr = np.asarray([v for v in values if v is not None and np.isfinite(v)], dtype=np.float64)
    if arr.size == 0:
        return {}
    p = np.percentile(arr, list(percentiles)).astype(float).tolist()
    out = {
        "count": float(arr.size),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
    }
    for perc, val in zip(percentiles, p):
        out[f"p{int(perc)}"] = float(val)
    return out


def make_quantile_bins(profile: Dict[str, Any], *, metrics: Sequence[str], quantiles=(0.2, 0.5, 0.8)) -> Dict[str, Dict[str, float]]:
    """
    Create low/medium/high bins for each metric from a profile dict that contains percentiles.
    Expects profile["metrics"][metric] to include p20/p50/p80 (or matching quantiles).
    """
    out: Dict[str, Dict[str, float]] = {}
    for m in metrics:
        md = (profile.get("metrics", {}) or {}).get(m, {})
        # Accept p20/p50/p80 naming (preferred)
        low = md.get("p20", None)
        mid = md.get("p50", None)
        high = md.get("p80", None)
        if low is None or mid is None or high is None:
            continue
        out[m] = {"low": float(low), "mid": float(mid), "high": float(high)}
    return out


def target_descriptor_vector(
    bins: Dict[str, Dict[str, float]],
    *,
    setting: Dict[str, str],
) -> Dict[str, float]:
    """
    setting example: {"alpha_dfa": "low", "alpha_width": "high"}
    """
    out: Dict[str, float] = {}
    for metric, level in setting.items():
        if metric not in bins:
            continue
        if level not in bins[metric]:
            raise ValueError(f"Unknown level {level} for metric {metric}.")
        out[metric] = float(bins[metric][level])
    return out
