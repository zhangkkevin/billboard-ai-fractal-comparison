from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence, Tuple

import numpy as np


def _ensure_1d_float(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    return x


def _default_nvals(n: int) -> np.ndarray:
    # SAFE policy: max_scale = 0.10*N, min_scale = max(16, 0.01*N). Logspaced, 20-30 scales.
    n_min = max(16, int(np.floor(n * 0.01)))
    n_max = int(np.floor(n * 0.10))
    if n_max <= n_min:
        return np.array([n_min, n_min + 1], dtype=int)
    for resolution in (25, 30, 35, 40):
        nvals = np.unique(np.logspace(np.log10(n_min), np.log10(n_max), resolution).astype(int))
        nvals = nvals[(nvals >= n_min) & (nvals <= n_max)]
        if nvals.size >= 20:
            return nvals
    nvals = np.unique(np.logspace(np.log10(n_min), np.log10(n_max), 30).astype(int))
    nvals = nvals[(nvals >= n_min) & (nvals <= n_max)]
    return nvals


def dfa_alpha(
    x: np.ndarray,
    *,
    nvals: Optional[Sequence[int]] = None,
    order: int = 1,
) -> float:
    """
    Detrended Fluctuation Analysis (DFA) scaling exponent alpha.

    - Uses `nolds.dfa` if available.
    - Otherwise uses a small, stable implementation with polynomial detrending.
    """
    x = _ensure_1d_float(x)
    if x.size < 16:
        raise ValueError("Signal too short for DFA (need >= 16 samples).")
    if float(np.std(x)) < 1e-12:
        raise ValueError("Constant/near-constant signal; DFA undefined.")

    if nvals is None:
        nvals = _default_nvals(int(x.size))
    nvals = np.asarray(list(nvals), dtype=int)
    nvals = np.unique(nvals[nvals > 1])
    if nvals.size < 2:
        raise ValueError("Need at least 2 window sizes for DFA.")

    # Try nolds if installed
    try:
        import nolds  # type: ignore

        alpha = nolds.dfa(x, nvals=nvals.tolist(), overlap=True, order=order)
        alpha_f = float(alpha)
        if not np.isfinite(alpha_f):
            raise ValueError("nolds returned non-finite alpha.")
        return alpha_f
    except Exception:
        pass

    # Internal DFA
    y = np.cumsum(x - np.mean(x))

    log_n: list[float] = []
    log_fn: list[float] = []

    for nwin in nvals:
        if nwin < 4 or nwin >= y.size:
            continue
        nseg = y.size // nwin
        if nseg < 2:
            continue

        yy = y[: nseg * nwin].reshape(nseg, nwin)
        t = np.arange(nwin, dtype=np.float64)

        # polynomial detrend per segment
        # Using polyfit in a loop keeps dependencies minimal and is fine for eval-first.
        rms = []
        for seg in yy:
            coeff = np.polyfit(t, seg, deg=order)
            trend = np.polyval(coeff, t)
            rms.append(np.sqrt(np.mean((seg - trend) ** 2)))
        fn = float(np.sqrt(np.mean(np.square(rms))))
        if fn > 0 and np.isfinite(fn):
            log_n.append(float(np.log(nwin)))
            log_fn.append(float(np.log(fn)))

    if len(log_n) < 2:
        raise ValueError("Not enough valid (n, F(n)) points for DFA fit.")

    slope, intercept = np.polyfit(np.array(log_n), np.array(log_fn), deg=1)
    alpha = float(slope)
    if not np.isfinite(alpha):
        raise ValueError("Non-finite DFA alpha.")
    return alpha


def dfa_log_log_points(
    x: np.ndarray,
    *,
    nvals: Optional[Sequence[int]] = None,
    order: int = 1,
) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Return (log_n, log_fn, alpha) for DFA log-log plot.
    Same protocol as dfa_alpha; use for visualization.
    """
    x = _ensure_1d_float(x)
    if x.size < 16:
        raise ValueError("Signal too short for DFA (need >= 16 samples).")
    if float(np.std(x)) < 1e-12:
        raise ValueError("Constant/near-constant signal; DFA undefined.")

    if nvals is None:
        nvals = _default_nvals(int(x.size))
    nvals = np.asarray(list(nvals), dtype=int)
    nvals = np.unique(nvals[nvals > 1])
    if nvals.size < 2:
        raise ValueError("Need at least 2 window sizes for DFA.")

    y = np.cumsum(x - np.mean(x))
    log_n: list[float] = []
    log_fn: list[float] = []

    for nwin in nvals:
        if nwin < 4 or nwin >= y.size:
            continue
        nseg = y.size // nwin
        if nseg < 2:
            continue

        yy = y[: nseg * nwin].reshape(nseg, nwin)
        t = np.arange(nwin, dtype=np.float64)

        rms = []
        for seg in yy:
            coeff = np.polyfit(t, seg, deg=order)
            trend = np.polyval(coeff, t)
            rms.append(np.sqrt(np.mean((seg - trend) ** 2)))
        fn = float(np.sqrt(np.mean(np.square(rms))))
        if fn > 0 and np.isfinite(fn):
            log_n.append(float(np.log(nwin)))
            log_fn.append(float(np.log(fn)))

    if len(log_n) < 2:
        raise ValueError("Not enough valid (n, F(n)) points for DFA fit.")

    log_n_arr = np.array(log_n, dtype=np.float64)
    log_fn_arr = np.array(log_fn, dtype=np.float64)
    slope, intercept = np.polyfit(log_n_arr, log_fn_arr, deg=1)
    alpha = float(slope)
    if not np.isfinite(alpha):
        raise ValueError("Non-finite DFA alpha.")
    return log_n_arr, log_fn_arr, alpha

