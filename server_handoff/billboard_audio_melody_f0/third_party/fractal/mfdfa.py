from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Sequence, Tuple

import numpy as np

from .shape import shape_descriptors_from_curve


def _ensure_sorted_qvals(qvals: Sequence[float]) -> np.ndarray:
    q = np.asarray(list(qvals), dtype=np.float64).reshape(-1)
    q = np.unique(q)
    q.sort()
    if not np.any(np.isclose(q, 0.0)):
        q = np.unique(np.concatenate([q, np.array([0.0])]))
        q.sort()
    return q


def _default_lag(n: int, min_scales: int = 25) -> np.ndarray:
    """SAFE policy: min_lag = max(16, 0.01*N), max_lag = 0.10*N. Logspaced, >= min_scales unique."""
    min_lag = max(16, int(np.floor(n * 0.01)))
    max_lag = int(np.floor(n * 0.10))
    if max_lag <= min_lag:
        return np.array([min_lag, min_lag + 1], dtype=int)
    for resolution in (min_scales, 30, 35, 40, 50):
        lag = np.logspace(np.log10(min_lag), np.log10(max_lag), resolution)
        lag = np.unique(lag.astype(int))
        lag = lag[(lag >= min_lag) & (lag <= max_lag)]
        lag = lag[lag > 0]
        if lag.size >= min_scales:
            return lag
    lag = np.logspace(np.log10(min_lag), np.log10(max_lag), 50)
    lag = np.unique(lag.astype(int))
    lag = lag[(lag >= min_lag) & (lag <= max_lag)]
    lag = lag[lag > 0]
    return lag


def mfdfa_spectrum(
    x: np.ndarray,
    *,
    qvals: Sequence[float],
    order: int = 2,
    lag: Optional[Sequence[int]] = None,
) -> Dict[str, object]:
    """
    Compute MFDFA spectrum using the `MFDFA` PyPI package if available.

    Returns:
      - H_q: (len(q),) list
      - tau_q: list
      - alpha_curve: list (alpha / h(q) curve)
      - f_alpha_curve: list
      - alpha_width, alpha_peak, spectrum_skew
      - W_L, W_R, B, R
      - delta_Hq = H(q_min) - H(q_max)
    """
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    if x.size < 64:
        raise ValueError("Signal too short for MFDFA (need >= 64 samples).")
    if float(np.std(x)) < 1e-12:
        raise ValueError("Constant/near-constant signal; MFDFA undefined.")

    q_full = _ensure_sorted_qvals(qvals)

    if lag is None:
        lag = _default_lag(int(x.size))
    lag = np.asarray(list(lag), dtype=int)
    lag = np.unique(lag[lag > 0])
    if lag.size < 3:
        raise ValueError("Need >= 3 lag values for MFDFA.")

    try:
        from MFDFA import MFDFA  # type: ignore
    except Exception as e:
        raise ImportError("MFDFA package not installed. Try: pip install MFDFA") from e

    lag_used, Fq = MFDFA(x, lag=lag, q=q_full, order=order)
    lag_used = np.asarray(lag_used, dtype=np.float64).reshape(-1)
    Fq = np.asarray(Fq, dtype=np.float64)
    if lag_used.size < 3 or Fq.ndim != 2 or Fq.shape[0] != lag_used.size:
        raise ValueError("Unexpected MFDFA output shapes.")
    if np.any(lag_used <= 0):
        raise ValueError("Invalid lag values from MFDFA.")

    # The MFDFA library (0.4.3) drops q=0 from its returned Fq matrix.
    # We keep a full q grid (sorted, including 0) for downstream descriptors.
    if Fq.shape[1] == q_full.size:
        q_used = q_full
        needs_q0_insert = False
    elif Fq.shape[1] == q_full.size - 1 and np.any(np.isclose(q_full, 0.0)):
        q_used = q_full[~np.isclose(q_full, 0.0)]
        needs_q0_insert = True
    else:
        raise ValueError(f"Unexpected MFDFA output shapes: Fq={Fq.shape}, q_full={q_full.shape}")

    log_lag = np.log(lag_used)
    eps = 1e-10

    H_used = np.zeros((q_used.size,), dtype=np.float64)
    for i in range(q_used.size):
        fq = Fq[:, i] + eps
        if np.any(fq <= 0) or np.any(~np.isfinite(fq)):
            raise ValueError("Invalid Fq values (non-positive or non-finite).")
        log_fq = np.log(fq)
        slope, _ = np.polyfit(log_lag, log_fq, deg=1)
        H_used[i] = slope

    if needs_q0_insert:
        # Insert H(0) by linear interpolation between the nearest negative/positive q.
        # (The q=0 definition uses a log-average; interpolation is a stable approximation for summaries.)
        q0_idx = int(np.where(np.isclose(q_full, 0.0))[0][0])
        # Find neighbors in q_used around 0
        neg_mask = q_used < 0
        pos_mask = q_used > 0
        if np.any(neg_mask) and np.any(pos_mask):
            q_neg = float(np.max(q_used[neg_mask]))
            q_pos = float(np.min(q_used[pos_mask]))
            h_neg = float(H_used[np.where(q_used == q_neg)[0][0]])
            h_pos = float(H_used[np.where(q_used == q_pos)[0][0]])
            h0 = h_neg + (0.0 - q_neg) * (h_pos - h_neg) / (q_pos - q_neg)
        elif np.any(neg_mask):
            h0 = float(H_used[np.where(q_used == float(np.max(q_used[neg_mask])))[0][0]])
        else:
            h0 = float(H_used[np.where(q_used == float(np.min(q_used[pos_mask])))[0][0]])
        H_q = np.insert(H_used, q0_idx, h0)
    else:
        H_q = H_used

    tau_q = H_q * q_full - 1.0
    dq = float(q_full[1] - q_full[0]) if q_full.size > 1 else 1.0
    if abs(dq) < 1e-12:
        # If q values are irregular, use gradient w.r.t. q directly.
        alpha_curve = np.gradient(tau_q, q_full)
    else:
        alpha_curve = np.gradient(tau_q, dq)
    f_alpha_curve = q_full * alpha_curve - tau_q

    if np.any(~np.isfinite(alpha_curve)) or np.any(~np.isfinite(f_alpha_curve)):
        raise ValueError("Non-finite spectrum values.")

    # Sort by alpha for stable summaries/plots
    sort_idx = np.argsort(alpha_curve)
    alpha_sorted = alpha_curve[sort_idx]
    f_sorted = f_alpha_curve[sort_idx]

    alpha_width = float(np.max(alpha_sorted) - np.min(alpha_sorted))
    alpha_peak = float(alpha_sorted[np.argmax(f_sorted)])
    shape_desc = shape_descriptors_from_curve(alpha_sorted, alpha_peak)
    if alpha_width > 1e-12:
        spectrum_skew = float((np.max(alpha_sorted) + np.min(alpha_sorted) - 2.0 * alpha_peak) / alpha_width)
    else:
        spectrum_skew = 0.0

    delta_Hq = float(H_q[0] - H_q[-1])  # q sorted low->high

    return {
        "qvals": q_full.tolist(),
        "H_q": H_q.tolist(),
        "tau_q": tau_q.tolist(),
        "alpha_curve": alpha_sorted.tolist(),
        "f_alpha_curve": f_sorted.tolist(),
        "alpha_width": alpha_width,
        "alpha_peak": alpha_peak,
        "W_L": float(shape_desc["W_L"]),
        "W_R": float(shape_desc["W_R"]),
        "B": float(shape_desc["B"]),
        "R": float(shape_desc["R"]),
        "spectrum_skew": spectrum_skew,
        "delta_Hq": delta_Hq,
    }
