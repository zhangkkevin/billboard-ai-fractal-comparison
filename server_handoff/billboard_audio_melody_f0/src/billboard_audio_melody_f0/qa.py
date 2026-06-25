from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import RunConfig
from .paths import cache_clean_dir, qa_dir


def _plot_contour(out_path: Path, contour: np.ndarray, title: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(contour, linewidth=0.8)
    ax.set_title(title)
    ax.set_xlabel("Frame")
    ax.set_ylabel("Semitones (median-centered)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _pick_tracks(accepted: pd.DataFrame, source: str, criterion: str, n: int = 1) -> List[pd.Series]:
    sub = accepted[accepted["source"] == source]
    if sub.empty:
        return []
    if criterion == "random":
        return [sub.sample(min(n, len(sub)), random_state=42).iloc[i] for i in range(min(n, len(sub)))]
    if criterion == "alpha_min":
        return [sub.loc[sub["alpha_dfa"].idxmin()]]
    if criterion == "alpha_max":
        return [sub.loc[sub["alpha_dfa"].idxmax()]]
    if criterion == "alpha_width_max":
        if "alpha_width" not in sub.columns or sub["alpha_width"].dropna().empty:
            return []
        return [sub.loc[sub["alpha_width"].idxmax()]]
    if criterion == "voiced_cov_min":
        col = "selected_voiced_coverage"
        if col not in sub.columns or sub[col].dropna().empty:
            return []
        return [sub.loc[sub[col].idxmin()]]
    if criterion == "octave_jump_max":
        col = "octave_jump_rate"
        if col not in sub.columns or sub[col].dropna().empty:
            return []
        return [sub.loc[sub[col].idxmax()]]
    return []


def generate_qa_plots(cfg: RunConfig, descriptors: pd.DataFrame, quality: pd.DataFrame) -> None:
    out_dir = qa_dir(cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    accepted = descriptors[descriptors["status"] == "accepted"].copy()
    if accepted.empty:
        return

    if "selected_voiced_coverage" not in accepted.columns and not quality.empty:
        qidx = quality.set_index("track_id")
        accepted["selected_voiced_coverage"] = accepted["track_id"].map(
            lambda t: qidx.loc[t]["selected_voiced_coverage"] if t in qidx.index else np.nan
        )
        accepted["octave_jump_rate"] = accepted["track_id"].map(
            lambda t: qidx.loc[t]["octave_jump_rate"] if t in qidx.index else np.nan
        )

    clean_dir = cache_clean_dir(cfg)
    specs = [
        ("random", "random", 3),
        ("alpha_min", "alpha_dfa_low", 1),
        ("alpha_max", "alpha_dfa_high", 1),
        ("alpha_width_max", "alpha_width_wide", 1),
        ("voiced_cov_min", "voiced_coverage_low", 1),
        ("octave_jump_max", "octave_jump_high", 1),
    ]

    for source in sorted(accepted["source"].dropna().unique()):
        for criterion, label, n in specs:
            picks = _pick_tracks(accepted, source, criterion, n=n)
            for i, row in enumerate(picks):
                cp = clean_dir / f"{row['track_id']}.npz"
                if not cp.exists():
                    continue
                data = np.load(cp, allow_pickle=True)
                if "contour_semitones" not in data:
                    continue
                contour = np.asarray(data["contour_semitones"]).reshape(-1)
                suffix = f"_{i}" if n > 1 else ""
                title = f"{source} | {row.get('artist','')} - {row.get('title','')} | {label}"
                fname = f"{source}_{label}{suffix}_{row['track_id']}.png"
                _plot_contour(out_dir / fname, contour, title)
