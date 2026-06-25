from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

A4_HZ = 440.0


@dataclass
class CleanResult:
    success: bool
    skip_reason: str = ""
    contour_semitones: Optional[np.ndarray] = None
    raw_voiced_coverage: float = float("nan")
    selected_voiced_coverage: float = float("nan")
    selected_duration_sec: float = float("nan")
    median_voiced_prob: float = float("nan")
    jump_rate: float = float("nan")
    octave_jump_rate: float = float("nan")
    region_start: int = 0
    region_end: int = 0


def _raw_voiced_mask(f0: np.ndarray, voiced_flag: np.ndarray) -> np.ndarray:
    mask = np.asarray(voiced_flag, dtype=bool).copy()
    mask &= np.isfinite(f0)
    mask &= f0 > 0
    return mask


def _fill_short_gaps(f0: np.ndarray, voiced: np.ndarray, max_gap_frames: int) -> np.ndarray:
    filled = f0.astype(np.float64).copy()
    n = len(filled)
    i = 0
    while i < n:
        if voiced[i]:
            i += 1
            continue
        gap_start = i
        while i < n and not voiced[i]:
            i += 1
        gap_end = i
        gap_len = gap_end - gap_start
        if gap_len <= max_gap_frames and gap_start > 0 and gap_end < n and voiced[gap_start - 1] and voiced[gap_end]:
            left = filled[gap_start - 1]
            right = filled[gap_end]
            filled[gap_start:gap_end] = np.linspace(left, right, gap_len + 2)[1:-1]
    return filled


def _split_regions(voiced: np.ndarray, min_gap_frames: int) -> List[Tuple[int, int]]:
    regions: List[Tuple[int, int]] = []
    n = len(voiced)
    i = 0
    while i < n:
        while i < n and not voiced[i]:
            i += 1
        if i >= n:
            break
        start = i
        while i < n:
            if not voiced[i]:
                gap_start = i
                while i < n and not voiced[i]:
                    i += 1
                if i - gap_start >= min_gap_frames:
                    break
            else:
                i += 1
        end = i
        if end > start:
            regions.append((start, end))
    return regions


def _hz_to_semitones(f0_hz: np.ndarray) -> np.ndarray:
    return 12.0 * np.log2(f0_hz / A4_HZ)


def _compute_jump_rates(semitones: np.ndarray, voiced: np.ndarray) -> Tuple[float, float]:
    idx = np.where(voiced)[0]
    if idx.size < 2:
        return float("nan"), float("nan")
    diffs = np.abs(np.diff(semitones[idx]))
    if diffs.size == 0:
        return float("nan"), float("nan")
    jump_rate = float(np.mean(diffs > 1.0))
    octave_jump_rate = float(np.mean(diffs > 9.0))
    return jump_rate, octave_jump_rate


def clean_contour(
    f0: np.ndarray,
    voiced_flag: np.ndarray,
    voiced_probs: np.ndarray,
    f0_cfg: Dict[str, Any],
) -> CleanResult:
    hop_length = int(f0_cfg["hop_length"])
    sr = int(f0_cfg["sr"])
    frame_sec = hop_length / sr
    max_gap_frames = max(1, int(round(float(f0_cfg["max_gap_fill_sec"]) / frame_sec)))
    min_region_frames = max(1, int(round(float(f0_cfg["min_region_sec"]) / frame_sec)))
    min_cov = float(f0_cfg["min_region_voiced_coverage"])

    raw_voiced = _raw_voiced_mask(f0, voiced_flag)
    raw_voiced_coverage = float(np.mean(raw_voiced)) if raw_voiced.size else 0.0

    filled_f0 = _fill_short_gaps(f0, raw_voiced, max_gap_frames)
    regions = _split_regions(raw_voiced, max_gap_frames + 1)

    best: Optional[Tuple[int, int, float, float]] = None
    for start, end in regions:
        region_len = end - start
        if region_len < min_region_frames:
            continue
        region_raw = raw_voiced[start:end]
        cov = float(np.mean(region_raw)) if region_raw.size else 0.0
        if cov < min_cov:
            continue
        if best is None or region_len > best[0]:
            best = (region_len, start, end, cov)

    if best is None:
        if not regions:
            return CleanResult(success=False, skip_reason="no_valid_region", raw_voiced_coverage=raw_voiced_coverage)
        longest = max(regions, key=lambda r: r[1] - r[0])
        dur = (longest[1] - longest[0]) * frame_sec
        if dur < float(f0_cfg["min_region_sec"]):
            return CleanResult(
                success=False,
                skip_reason="too_short",
                raw_voiced_coverage=raw_voiced_coverage,
                selected_duration_sec=dur,
            )
        return CleanResult(
            success=False,
            skip_reason="low_region_voiced_coverage",
            raw_voiced_coverage=raw_voiced_coverage,
            selected_duration_sec=dur,
        )

    region_len, start, end, sel_cov = best
    region_f0 = filled_f0[start:end]
    region_raw = raw_voiced[start:end]
    region_probs = np.asarray(voiced_probs[start:end])

    semitones = _hz_to_semitones(region_f0)
    voiced_sem = region_raw & np.isfinite(semitones)
    if not np.any(voiced_sem):
        return CleanResult(success=False, skip_reason="no_valid_region", raw_voiced_coverage=raw_voiced_coverage)

    median = float(np.median(semitones[voiced_sem]))
    centered = semitones.copy()
    centered[voiced_sem] -= median

    jump_rate, octave_jump_rate = _compute_jump_rates(centered, region_raw)
    median_prob = float(np.median(region_probs[region_raw])) if np.any(region_raw) else float("nan")

    return CleanResult(
        success=True,
        contour_semitones=centered.astype(np.float64),
        raw_voiced_coverage=raw_voiced_coverage,
        selected_voiced_coverage=sel_cov,
        selected_duration_sec=region_len * frame_sec,
        median_voiced_prob=median_prob,
        jump_rate=jump_rate,
        octave_jump_rate=octave_jump_rate,
        region_start=start,
        region_end=end,
    )
