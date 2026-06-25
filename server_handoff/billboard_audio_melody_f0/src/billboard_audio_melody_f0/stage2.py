from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import yaml

from .config import RunConfig
from .paths import (
    cache_clean_dir,
    dissertation_root,
    ensure_scope_dirs,
    f0_fractal_descriptors_csv,
    f0_quality_csv,
    group_summary_csv,
    qa_dir,
    run_manifest_stage2,
    scope_root,
)
from .qa import generate_qa_plots
from .summaries import write_dissertation_summaries, write_group_summary
from .workers import run_pool_map


def _import_fractal():
    from fractal.summary import compute_fractal_descriptors_1d

    return compute_fractal_descriptors_1d


def _contour_for_fractal(contour: np.ndarray) -> np.ndarray | None:
    x = np.asarray(contour, dtype=np.float64).reshape(-1)
    valid = np.isfinite(x)
    if valid.sum() < 32:
        return None
    if np.all(valid):
        return x
    idx = np.arange(x.size)
    return np.interp(idx, idx[valid], x[valid])


def _process_fractal(args: tuple[str, Dict[str, Any], Dict[str, Any], set]) -> Dict[str, Any]:
    clean_path, row, fractal_cfg, skip_ids = args
    track_id = row.get("track_id", Path(clean_path).stem)
    out = dict(row)
    out["cache_path"] = clean_path
    out["track_id"] = track_id

    if track_id in skip_ids:
        return None  # type: ignore[return-value]

    try:
        data = np.load(clean_path, allow_pickle=True)
        if str(data.get("status", "")) != "success":
            out.update({"status": "skipped", "reason": str(data.get("skip_reason", "no_clean_contour"))})
            return out

        contour_raw = np.asarray(data["contour_semitones"], dtype=np.float64).reshape(-1)
        contour = _contour_for_fractal(contour_raw)
        if contour is None:
            out.update({"status": "skipped", "reason": "contour_too_short"})
            return out

        qvals = np.linspace(float(fractal_cfg["q_min"]), float(fractal_cfg["q_max"]), int(fractal_cfg["q_n"]))
        compute = _import_fractal()
        desc = compute(contour, qvals=qvals, compute_mfdfa=True)

        alpha = desc.get("alpha_dfa")
        if alpha is None or not np.isfinite(alpha):
            out.update({"status": "failed", "reason": "non_finite_alpha_dfa", "alpha_dfa": alpha})
            return out

        out.update({"status": "accepted", "reason": ""})
        out["alpha_dfa"] = float(alpha)
        out["mfdfa_ok"] = bool(desc.get("mfdfa_ok", False))
        out["mfdfa_error"] = desc.get("mfdfa_error")
        for key in ("alpha_width", "alpha_peak", "W_L", "W_R", "B", "R", "spectrum_skew", "delta_Hq"):
            val = desc.get(key)
            out[key] = float(val) if val is not None and np.isfinite(val) else None

        for key in ("H_q", "alpha_curve", "f_alpha_curve", "qvals"):
            val = desc.get(key)
            out[key] = json.dumps(val.tolist() if hasattr(val, "tolist") else val) if val is not None else None

        out["contour_length"] = int(contour.size)
        out["selected_voiced_coverage"] = float(data.get("selected_voiced_coverage", np.nan))
        out["octave_jump_rate"] = float(data.get("octave_jump_rate", np.nan))
        return out

    except Exception as exc:
        out.update({"status": "failed", "reason": str(exc)})
        return out


def _load_quality_index(cfg: RunConfig) -> pd.DataFrame:
    qpath = f0_quality_csv(cfg)
    if qpath.exists():
        return pd.read_csv(qpath).set_index("track_id", drop=False)
    return pd.DataFrame()


def run_stage2(cfg: RunConfig) -> Dict[str, Any]:
    started = datetime.now(timezone.utc)
    ensure_scope_dirs(cfg)
    qa_dir(cfg).mkdir(parents=True, exist_ok=True)

    clean_dir = cache_clean_dir(cfg)
    clean_files = sorted(clean_dir.glob("*.npz"))
    if not clean_files:
        raise RuntimeError(f"No clean contours in {clean_dir}")

    quality = _load_quality_index(cfg)
    existing = pd.DataFrame()
    out_csv = f0_fractal_descriptors_csv(cfg)
    skip_ids: set = set()
    if out_csv.exists() and not cfg.force:
        existing = pd.read_csv(out_csv)
        if "track_id" in existing.columns:
            skip_ids = set(existing["track_id"].tolist())

    tasks = []
    for cp in clean_files:
        track_id = cp.stem
        row = quality.loc[track_id].to_dict() if track_id in quality.index else {"track_id": track_id}
        row["track_id"] = track_id
        tasks.append((str(cp), row, cfg.fractal, skip_ids))

    results = run_pool_map(_process_fractal, tasks, cfg.workers, desc="Stage2 fractal")
    results = [r for r in results if r is not None]

    new_df = pd.DataFrame(results)
    if not cfg.force and not existing.empty:
        combined = pd.concat([existing, new_df], ignore_index=True).drop_duplicates(subset=["track_id"], keep="last")
    else:
        combined = new_df

    combined.to_csv(out_csv, index=False)
    write_group_summary(combined, group_summary_csv(cfg))

    if cfg.output_scope == "full":
        dissertation_root(cfg).mkdir(parents=True, exist_ok=True)
        write_dissertation_summaries(cfg, combined, pd.read_csv(f0_quality_csv(cfg)) if f0_quality_csv(cfg).exists() else pd.DataFrame())

    generate_qa_plots(cfg, combined, quality if not quality.empty else pd.DataFrame())

    finished = datetime.now(timezone.utc)
    summary = {
        "stage": "stage2-fractal",
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "elapsed_sec": (finished - started).total_seconds(),
        "workers": cfg.workers,
        "output_scope": cfg.output_scope,
        "total_tracks": len(combined),
        "accepted_count": int((combined["status"] == "accepted").sum()),
        "skipped_count": int((combined["status"] == "skipped").sum()),
        "failed_count": int((combined["status"] == "failed").sum()),
        "descriptors_path": str(out_csv),
        "group_summary_path": str(group_summary_csv(cfg)),
    }

    with open(run_manifest_stage2(cfg), "w", encoding="utf-8") as f:
        yaml.safe_dump(summary, f, sort_keys=False)

    return summary
