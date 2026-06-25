from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class RunConfig:
    project_root: Path
    audio_root: Path
    workers: int = 128
    models: List[str] = field(default_factory=lambda: ["billboard", "suno_v4_5", "yue"])
    output_scope: str = "full"
    force: bool = False
    limit_per_model: Optional[int] = None
    benchmark_mode: bool = False
    benchmark_sample_size: Optional[int] = None
    benchmark_output_root: Optional[Path] = None
    manifest_path: Optional[Path] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def f0(self) -> Dict[str, Any]:
        return self.raw.get("f0", {})

    @property
    def fractal(self) -> Dict[str, Any]:
        return self.raw.get("fractal", {})

    @property
    def model_specs(self) -> Dict[str, Dict[str, Any]]:
        return self.raw.get("models", {})

    @property
    def benchmark(self) -> Dict[str, Any]:
        return self.raw.get("benchmark", {})


def load_default_config(pkg_root: Path) -> Dict[str, Any]:
    path = pkg_root / "config" / "default.yml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_run_config(
    project_root: Path,
    audio_root: Path,
    pkg_root: Path,
    *,
    workers: int,
    models: List[str],
    output_scope: str,
    force: bool,
    limit_per_model: Optional[int],
    benchmark_mode: bool,
    benchmark_sample_size: Optional[int],
    benchmark_output_root: Optional[Path],
    manifest_path: Optional[Path],
) -> RunConfig:
    raw = load_default_config(pkg_root)
    return RunConfig(
        project_root=project_root.resolve(),
        audio_root=audio_root.resolve(),
        workers=workers,
        models=models,
        output_scope=output_scope,
        force=force,
        limit_per_model=limit_per_model,
        benchmark_mode=benchmark_mode,
        benchmark_sample_size=benchmark_sample_size,
        benchmark_output_root=benchmark_output_root,
        manifest_path=manifest_path,
        raw=raw,
    )
