from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

FILENAME_RE = re.compile(r"^(\d{4})_([0-9]+[A-Za-z]?)_")


def normalize_position(position: str | int | float) -> str:
    s = str(position).strip().lower()
    m = re.match(r"^(\d+)([a-z]?)$", s)
    if not m:
        raise ValueError(f"Invalid position: {position!r}")
    num, suffix = m.group(1), m.group(2)
    return f"{int(num):02d}{suffix}"


def parse_audio_filename(filename: str) -> Optional[Tuple[int, str]]:
    m = FILENAME_RE.match(filename)
    if not m:
        return None
    year = int(m.group(1))
    position_norm = normalize_position(m.group(2))
    return year, position_norm


def load_annotations(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["position_norm"] = df["position"].apply(normalize_position)
    df["year"] = df["year"].astype(int)
    return df


def scan_model_audio(audio_root: Path, source: str, subpath: str) -> List[Dict[str, Any]]:
    model_dir = audio_root / subpath
    if not model_dir.is_dir():
        raise FileNotFoundError(f"Audio directory not found: {model_dir}")

    rows: List[Dict[str, Any]] = []
    for ext in ("*.mp3", "*.wav", "*.flac"):
        for audio_path in sorted(model_dir.glob(ext)):
            parsed = parse_audio_filename(audio_path.name)
            if parsed is None:
                continue
            year, position_norm = parsed
            track_id = f"{source}_{year}_{position_norm}"
            rows.append(
                {
                    "track_id": track_id,
                    "source": source,
                    "year": year,
                    "position": position_norm,
                    "audio_path": str(audio_path.resolve()),
                    "filename": audio_path.name,
                }
            )
    return rows


def join_annotations(rows: List[Dict[str, Any]], annotations: pd.DataFrame) -> List[Dict[str, Any]]:
    ann = annotations.set_index(["year", "position_norm"])
    out: List[Dict[str, Any]] = []
    for row in rows:
        key = (row["year"], row["position"])
        if key in ann.index:
            meta = ann.loc[key]
            if isinstance(meta, pd.DataFrame):
                meta = meta.iloc[0]
            row["artist"] = meta["artist"]
            row["title"] = meta["title"]
        else:
            row["artist"] = ""
            row["title"] = ""
        out.append(row)
    return out


def build_manifest(
    audio_root: Path,
    annotations_path: Path,
    model_specs: Dict[str, Dict[str, Any]],
    models: List[str],
    *,
    limit_per_model: Optional[int] = None,
    manifest_filter: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    annotations = load_annotations(annotations_path)
    all_rows: List[Dict[str, Any]] = []

    for source in models:
        spec = model_specs[source]
        rows = scan_model_audio(audio_root, source, spec["subpath"])
        rows = join_annotations(rows, annotations)
        rows.sort(key=lambda r: (r["year"], r["position"]))
        if manifest_filter is not None:
            allowed = set(manifest_filter["track_id"].tolist())
            rows = [r for r in rows if r["track_id"] in allowed]
        elif limit_per_model is not None:
            rows = rows[:limit_per_model]
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    if df.empty:
        return df

    df["status"] = "pending"
    df["cache_path"] = ""
    df["selected_duration_sec"] = float("nan")
    df["raw_voiced_coverage"] = float("nan")
    df["selected_voiced_coverage"] = float("nan")
    df["skip_reason"] = ""
    return df
