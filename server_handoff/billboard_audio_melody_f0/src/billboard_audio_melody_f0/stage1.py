from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import yaml

from .config import RunConfig
from .contour_clean import clean_contour
from .f0_extract import extract_f0
from .manifest import build_manifest
from .paths import (
    annotations_csv,
    cache_clean_dir,
    cache_f0_dir,
    ensure_scope_dirs,
    f0_quality_csv,
    manifest_csv,
    run_manifest_stage1,
)
from .workers import run_pool_map


def _track_paths(cfg_dict: Dict[str, Any], track_id: str) -> tuple[Path, Path]:
    f0_path = Path(cfg_dict["cache_f0_dir"]) / f"{track_id}.npz"
    clean_path = Path(cfg_dict["cache_clean_dir"]) / f"{track_id}.npz"
    return f0_path, clean_path


def _process_track_row(row: Dict[str, Any], cfg_dict: Dict[str, Any]) -> Dict[str, Any]:
    track_id = row["track_id"]
    f0_path, clean_path = _track_paths(cfg_dict, track_id)
    out = dict(row)
    out.setdefault("status", "pending")

    try:
        if not cfg_dict.get("force") and f0_path.exists() and clean_path.exists():
            data = np.load(clean_path, allow_pickle=True)
            if str(data.get("status", "success")) == "success":
                out.update(
                    {
                        "status": "success",
                        "cache_path": str(clean_path),
                        "selected_duration_sec": float(data.get("selected_duration_sec", np.nan)),
                        "raw_voiced_coverage": float(data.get("raw_voiced_coverage", np.nan)),
                        "selected_voiced_coverage": float(data.get("selected_voiced_coverage", np.nan)),
                        "median_voiced_prob": float(data.get("median_voiced_prob", np.nan)),
                        "jump_rate": float(data.get("jump_rate", np.nan)),
                        "octave_jump_rate": float(data.get("octave_jump_rate", np.nan)),
                        "skip_reason": "",
                    }
                )
                return out

        f0, voiced_flag, voiced_probs, meta = extract_f0(row["audio_path"], cfg_dict["f0"])
        np.savez_compressed(
            f0_path,
            f0_hz=f0,
            voiced_flag=voiced_flag,
            voiced_probs=voiced_probs,
            sr=meta["sr"],
            hop_length=meta["hop_length"],
            frame_length=cfg_dict["f0"]["frame_length"],
            audio_path=row["audio_path"],
            source=row["source"],
        )

        cleaned = clean_contour(f0, voiced_flag, voiced_probs, cfg_dict["f0"])
        if not cleaned.success:
            np.savez_compressed(
                clean_path,
                status="skipped",
                skip_reason=cleaned.skip_reason,
                raw_voiced_coverage=cleaned.raw_voiced_coverage,
                selected_duration_sec=cleaned.selected_duration_sec,
                selected_voiced_coverage=cleaned.selected_voiced_coverage,
            )
            out.update(
                {
                    "status": "skipped",
                    "cache_path": str(clean_path),
                    "skip_reason": cleaned.skip_reason,
                    "selected_duration_sec": cleaned.selected_duration_sec,
                    "raw_voiced_coverage": cleaned.raw_voiced_coverage,
                    "selected_voiced_coverage": cleaned.selected_voiced_coverage,
                    "median_voiced_prob": float("nan"),
                    "jump_rate": float("nan"),
                    "octave_jump_rate": float("nan"),
                }
            )
            return out

        np.savez_compressed(
            clean_path,
            status="success",
            contour_semitones=cleaned.contour_semitones,
            raw_voiced_coverage=cleaned.raw_voiced_coverage,
            selected_voiced_coverage=cleaned.selected_voiced_coverage,
            selected_duration_sec=cleaned.selected_duration_sec,
            median_voiced_prob=cleaned.median_voiced_prob,
            jump_rate=cleaned.jump_rate,
            octave_jump_rate=cleaned.octave_jump_rate,
            region_start=cleaned.region_start,
            region_end=cleaned.region_end,
            track_id=track_id,
            source=row["source"],
            year=row["year"],
            position=row["position"],
        )
        out.update(
            {
                "status": "success",
                "cache_path": str(clean_path),
                "skip_reason": "",
                "selected_duration_sec": cleaned.selected_duration_sec,
                "raw_voiced_coverage": cleaned.raw_voiced_coverage,
                "selected_voiced_coverage": cleaned.selected_voiced_coverage,
                "median_voiced_prob": cleaned.median_voiced_prob,
                "jump_rate": cleaned.jump_rate,
                "octave_jump_rate": cleaned.octave_jump_rate,
            }
        )
        return out

    except Exception as exc:
        out.update({"status": "failed", "skip_reason": str(exc), "cache_path": ""})
        return out


def _worker(args: tuple[Dict[str, Any], Dict[str, Any]]) -> Dict[str, Any]:
    row, cfg_dict = args
    return _process_track_row(row, cfg_dict)


def _cfg_dict(cfg: RunConfig) -> Dict[str, Any]:
    return {
        "f0": cfg.f0,
        "force": cfg.force,
        "cache_f0_dir": str(cache_f0_dir(cfg)),
        "cache_clean_dir": str(cache_clean_dir(cfg)),
    }


def preflight_vocal_counts(cfg: RunConfig) -> Dict[str, int]:
    counts = {}
    for source in cfg.models:
        spec = cfg.model_specs[source]
        d = cfg.audio_root / spec["subpath"]
        counts[source] = len(list(d.glob("*.mp3")) + list(d.glob("*.wav")))
        expected = int(spec.get("expected", 0))
        if expected and counts[source] != expected:
            raise RuntimeError(f"Preflight failed for {source}: expected {expected}, found {counts[source]} in {d}")
    return counts


def run_stage1(cfg: RunConfig) -> Dict[str, Any]:
    started = datetime.now(timezone.utc)
    ensure_scope_dirs(cfg)

    if cfg.output_scope == "full":
        preflight_vocal_counts(cfg)

    manifest_filter = None
    if cfg.manifest_path and cfg.manifest_path.exists():
        manifest_filter = pd.read_csv(cfg.manifest_path)

    manifest = build_manifest(
        cfg.audio_root,
        annotations_csv(cfg),
        cfg.model_specs,
        cfg.models,
        limit_per_model=cfg.limit_per_model if not cfg.benchmark_mode else None,
        manifest_filter=manifest_filter,
    )

    if manifest.empty:
        raise RuntimeError("Manifest is empty")

    manifest.to_csv(manifest_csv(cfg), index=False)
    cfg_d = _cfg_dict(cfg)
    tasks = [(row._asdict() if hasattr(row, "_asdict") else row.to_dict(), cfg_d) for _, row in manifest.iterrows()]

    results = run_pool_map(
        _worker,
        tasks,
        cfg.workers,
        maxtasksperchild=1,
        desc="Stage1 F0",
    )

    quality_df = pd.DataFrame(results)
    quality_df.to_csv(f0_quality_csv(cfg), index=False)

    finished = datetime.now(timezone.utc)
    summary = {
        "stage": "stage1-f0",
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "elapsed_sec": (finished - started).total_seconds(),
        "workers": cfg.workers,
        "output_scope": cfg.output_scope,
        "benchmark_mode": cfg.benchmark_mode,
        "models": cfg.models,
        "total_tracks": len(quality_df),
        "success_count": int((quality_df["status"] == "success").sum()),
        "skipped_count": int((quality_df["status"] == "skipped").sum()),
        "failed_count": int((quality_df["status"] == "failed").sum()),
        "manifest_path": str(manifest_csv(cfg)),
        "f0_quality_path": str(f0_quality_csv(cfg)),
    }

    per_model = quality_df.groupby("source")["status"].value_counts().unstack(fill_value=0)
    summary["per_model_status"] = json.loads(per_model.to_json())

    with open(run_manifest_stage1(cfg), "w", encoding="utf-8") as f:
        yaml.safe_dump(summary, f, sort_keys=False)

    return summary
