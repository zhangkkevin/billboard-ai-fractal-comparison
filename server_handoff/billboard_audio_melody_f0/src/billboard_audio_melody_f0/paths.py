from __future__ import annotations

from pathlib import Path

from .config import RunConfig


def results_root(cfg: RunConfig) -> Path:
    rel = cfg.raw.get("outputs", {}).get("results_root", "results/audio_melody_f0")
    return cfg.project_root / rel


def dissertation_root(cfg: RunConfig) -> Path:
    rel = cfg.raw.get("outputs", {}).get("dissertation_root", "data/results/audio_melody_f0")
    return cfg.project_root / rel


def smoke_subdir(cfg: RunConfig) -> str:
    return cfg.raw.get("outputs", {}).get("smoke_subdir", "smoke")


def scope_root(cfg: RunConfig) -> Path:
    if cfg.benchmark_output_root is not None:
        return cfg.benchmark_output_root
    root = results_root(cfg)
    if cfg.output_scope == "smoke":
        return root / smoke_subdir(cfg)
    return root


def cache_f0_dir(cfg: RunConfig) -> Path:
    return scope_root(cfg) / "cache" / "f0"


def cache_clean_dir(cfg: RunConfig) -> Path:
    return scope_root(cfg) / "cache" / "clean_contours"


def manifest_csv(cfg: RunConfig) -> Path:
    if cfg.manifest_path is not None:
        return cfg.manifest_path
    return scope_root(cfg) / "manifest.csv"


def f0_quality_csv(cfg: RunConfig) -> Path:
    return scope_root(cfg) / "f0_quality.csv"


def run_manifest_stage1(cfg: RunConfig) -> Path:
    return scope_root(cfg) / "run_manifest_stage1.yml"


def f0_fractal_descriptors_csv(cfg: RunConfig) -> Path:
    return scope_root(cfg) / "f0_fractal_descriptors.csv"


def group_summary_csv(cfg: RunConfig) -> Path:
    return scope_root(cfg) / "group_summary.csv"


def run_manifest_stage2(cfg: RunConfig) -> Path:
    return scope_root(cfg) / "run_manifest_stage2.yml"


def qa_dir(cfg: RunConfig) -> Path:
    return scope_root(cfg) / "qa"


def benchmark_dir(cfg: RunConfig) -> Path:
    return results_root(cfg) / smoke_subdir(cfg) / "benchmark"


def benchmark_manifest_csv(cfg: RunConfig) -> Path:
    return benchmark_dir(cfg) / "benchmark_manifest.csv"


def benchmark_results_csv(cfg: RunConfig) -> Path:
    return benchmark_dir(cfg) / "benchmark_results.csv"


def benchmark_worker_dir(cfg: RunConfig, workers: int) -> Path:
    return benchmark_dir(cfg) / f"workers_{workers}"


def annotations_csv(cfg: RunConfig) -> Path:
    rel = cfg.raw.get("annotations", "data/annotations/billboard_annotations_redacted.csv")
    return cfg.project_root / rel


def ensure_scope_dirs(cfg: RunConfig) -> None:
    cache_f0_dir(cfg).mkdir(parents=True, exist_ok=True)
    cache_clean_dir(cfg).mkdir(parents=True, exist_ok=True)
    scope_root(cfg).mkdir(parents=True, exist_ok=True)
