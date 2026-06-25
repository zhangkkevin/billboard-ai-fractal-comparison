from __future__ import annotations

import ast
import json
from typing import Any, Dict, Tuple

import numpy as np


def _coerce_curve(values: Any) -> np.ndarray:
    """Coerce an alpha-curve payload into a finite float array."""
    if values is None:
        return np.array([], dtype=np.float64)

    if isinstance(values, np.ndarray):
        arr = values.astype(np.float64, copy=False).reshape(-1)
        return arr[np.isfinite(arr)]

    if isinstance(values, (list, tuple)):
        arr = np.asarray(values, dtype=np.float64).reshape(-1)
        return arr[np.isfinite(arr)]

    if isinstance(values, str):
        text = values.strip()
        if not text:
            return np.array([], dtype=np.float64)
        parsed = None
        for loader in (json.loads, ast.literal_eval):
            try:
                parsed = loader(text)
                break
            except Exception:
                continue
        if parsed is None:
            return np.array([], dtype=np.float64)
        arr = np.asarray(parsed, dtype=np.float64).reshape(-1)
        return arr[np.isfinite(arr)]

    try:
        arr = np.asarray(values, dtype=np.float64).reshape(-1)
    except (TypeError, ValueError):
        return np.array([], dtype=np.float64)
    return arr[np.isfinite(arr)]


def curve_minmax(alpha_curve: Any) -> Tuple[float, float]:
    """Return (alpha_min, alpha_max) from a stored alpha-curve payload."""
    arr = _coerce_curve(alpha_curve)
    if arr.size == 0:
        return np.nan, np.nan
    return float(np.min(arr)), float(np.max(arr))


def shape_widths(alpha_curve: Any, alpha_peak: float) -> Tuple[float, float]:
    """Return left/right widths around alpha_peak: (W_L, W_R)."""
    if not np.isfinite(alpha_peak):
        return np.nan, np.nan
    alpha_min, alpha_max = curve_minmax(alpha_curve)
    if not np.isfinite(alpha_min) or not np.isfinite(alpha_max):
        return np.nan, np.nan
    w_l = max(float(alpha_peak) - alpha_min, 0.0)
    w_r = max(alpha_max - float(alpha_peak), 0.0)
    return float(w_l), float(w_r)


def shape_balance_B(w_l: float, w_r: float, eps: float = 1e-12) -> float:
    """Normalized balance B = (W_L - W_R) / (W_L + W_R)."""
    if not np.isfinite(w_l) or not np.isfinite(w_r):
        return np.nan
    denom = float(w_l) + float(w_r)
    if denom <= eps:
        return 0.0
    return float((float(w_l) - float(w_r)) / denom)


def shape_log_ratio_R(w_l: float, w_r: float, eps: float = 1e-6) -> float:
    """Training-time log-ratio R = log((W_L + eps) / (W_R + eps))."""
    if not np.isfinite(w_l) or not np.isfinite(w_r):
        return np.nan
    ratio = (max(float(w_l), 0.0) + eps) / (max(float(w_r), 0.0) + eps)
    return float(np.log(ratio))


def shape_descriptors_from_curve(
    alpha_curve: Any,
    alpha_peak: float,
    *,
    balance_eps: float = 1e-12,
    ratio_eps: float = 1e-6,
) -> Dict[str, float]:
    """Derive W_L, W_R, B, and R from a spectrum curve and alpha_peak."""
    w_l, w_r = shape_widths(alpha_curve, alpha_peak)
    return {
        "W_L": w_l,
        "W_R": w_r,
        "B": shape_balance_B(w_l, w_r, eps=balance_eps),
        "R": shape_log_ratio_R(w_l, w_r, eps=ratio_eps),
    }


def ensure_shape_descriptors(df, *, curve_col: str = "alpha_curve", peak_col: str = "alpha_peak", copy: bool = True):
    """
    Ensure a dataframe has W_L, W_R, B, and R columns.

    Existing finite values are preserved; missing values are derived from
    alpha_curve + alpha_peak when available.
    """
    try:
        import pandas as pd  # type: ignore
    except Exception as exc:  # pragma: no cover - pandas is available in analysis env
        raise ImportError("ensure_shape_descriptors requires pandas.") from exc

    if copy:
        df = df.copy()

    n = len(df)
    w_l = np.full(n, np.nan, dtype=np.float64)
    w_r = np.full(n, np.nan, dtype=np.float64)

    if "W_L" in df.columns:
        vals = pd.to_numeric(df["W_L"], errors="coerce").to_numpy(dtype=np.float64, copy=False)
        mask = np.isfinite(vals)
        w_l[mask] = vals[mask]
    if "W_R" in df.columns:
        vals = pd.to_numeric(df["W_R"], errors="coerce").to_numpy(dtype=np.float64, copy=False)
        mask = np.isfinite(vals)
        w_r[mask] = vals[mask]

    if curve_col in df.columns and peak_col in df.columns:
        peaks = pd.to_numeric(df[peak_col], errors="coerce").to_numpy(dtype=np.float64, copy=False)
        for i in range(n):
            if np.isfinite(w_l[i]) and np.isfinite(w_r[i]):
                continue
            if not np.isfinite(peaks[i]):
                continue
            derived = shape_descriptors_from_curve(df.iloc[i][curve_col], float(peaks[i]))
            if not np.isfinite(w_l[i]) and np.isfinite(derived["W_L"]):
                w_l[i] = derived["W_L"]
            if not np.isfinite(w_r[i]) and np.isfinite(derived["W_R"]):
                w_r[i] = derived["W_R"]

    df["W_L"] = w_l
    df["W_R"] = w_r

    b_vals = np.array([shape_balance_B(a, b) for a, b in zip(w_l, w_r)], dtype=np.float64)
    r_vals = np.array([shape_log_ratio_R(a, b) for a, b in zip(w_l, w_r)], dtype=np.float64)

    if "B" in df.columns:
        existing = pd.to_numeric(df["B"], errors="coerce").to_numpy(dtype=np.float64, copy=False)
        mask = np.isfinite(existing)
        b_vals[mask] = existing[mask]
    if "R" in df.columns:
        existing = pd.to_numeric(df["R"], errors="coerce").to_numpy(dtype=np.float64, copy=False)
        mask = np.isfinite(existing)
        r_vals[mask] = existing[mask]

    df["B"] = b_vals
    df["R"] = r_vals
    return df
