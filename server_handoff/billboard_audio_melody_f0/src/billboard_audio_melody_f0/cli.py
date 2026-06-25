from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .benchmark import build_benchmark_manifest, choose_benchmark_worker, run_benchmark_worker
from .config import build_run_config
from .stage1 import run_stage1
from .stage2 import run_stage2


def _pkg_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--project-root", type=Path, required=True)
    p.add_argument("--workers", type=int, default=128)
    p.add_argument("--output-scope", choices=["smoke", "full"], default="full")
    p.add_argument("--force", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="billboard_audio_melody_f0")
    sub = parser.add_subparsers(dest="command", required=True)

    s1 = sub.add_parser("stage1-f0")
    _add_common_args(s1)
    s1.add_argument("--audio-root", type=Path, required=True)
    s1.add_argument("--models", nargs="+", default=["billboard", "suno_v4_5", "yue"])
    s1.add_argument("--limit-per-model", type=int, default=None)
    s1.add_argument("--benchmark-mode", action="store_true")
    s1.add_argument("--benchmark-sample-size", type=int, default=None)
    s1.add_argument("--benchmark-output-root", type=Path, default=None)
    s1.add_argument("--manifest-path", type=Path, default=None)

    s2 = sub.add_parser("stage2-fractal")
    _add_common_args(s2)

    sb = sub.add_parser("benchmark-stage1")
    sb.add_argument("--project-root", type=Path, required=True)
    sb.add_argument("--audio-root", type=Path, required=True)
    sb.add_argument("--models", nargs="+", default=["billboard", "suno_v4_5", "yue"])
    sb.add_argument("--benchmark-sample-size", type=int, default=192)
    sb.add_argument("--worker-counts", type=str, default="16,32,64,128")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    pkg_root = _pkg_root()

    if args.command == "stage1-f0":
        if args.limit_per_model and args.output_scope != "smoke" and not args.benchmark_mode:
            print("error: --limit-per-model requires --output-scope smoke", file=sys.stderr)
            return 2
        cfg = build_run_config(
            args.project_root,
            args.audio_root,
            pkg_root,
            workers=args.workers,
            models=args.models,
            output_scope=args.output_scope,
            force=args.force,
            limit_per_model=args.limit_per_model,
            benchmark_mode=args.benchmark_mode,
            benchmark_sample_size=args.benchmark_sample_size,
            benchmark_output_root=args.benchmark_output_root,
            manifest_path=args.manifest_path,
        )
        if cfg.benchmark_mode:
            build_benchmark_manifest(cfg)
        summary = run_stage1(cfg)
        print(summary)
        return 0

    if args.command == "stage2-fractal":
        cfg = build_run_config(
            args.project_root,
            args.project_root / "audio_data",
            pkg_root,
            workers=args.workers,
            models=["billboard", "suno_v4_5", "yue"],
            output_scope=args.output_scope,
            force=args.force,
            limit_per_model=None,
            benchmark_mode=False,
            benchmark_sample_size=None,
            benchmark_output_root=None,
            manifest_path=None,
        )
        summary = run_stage2(cfg)
        print(summary)
        return 0

    if args.command == "benchmark-stage1":
        worker_counts = [int(x) for x in args.worker_counts.split(",")]
        sample_size = args.benchmark_sample_size
        if sample_size < max(worker_counts):
            print(
                f"error: benchmark sample_size {sample_size} < max workers {max(worker_counts)}",
                file=sys.stderr,
            )
            return 2

        cfg = build_run_config(
            args.project_root,
            args.audio_root,
            pkg_root,
            workers=worker_counts[0],
            models=args.models,
            output_scope="smoke",
            force=True,
            limit_per_model=None,
            benchmark_mode=True,
            benchmark_sample_size=sample_size,
            benchmark_output_root=None,
            manifest_path=None,
        )
        build_benchmark_manifest(cfg)
        for w in worker_counts:
            print(f"Benchmark workers={w} ...")
            run_benchmark_worker(cfg, w)
        chosen = choose_benchmark_worker(cfg)
        print({"chosen_workers": chosen})
        return 0

    return 1
