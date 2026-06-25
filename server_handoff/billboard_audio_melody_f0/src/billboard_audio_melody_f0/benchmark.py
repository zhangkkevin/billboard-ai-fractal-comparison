from __future__ import annotations

import re
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import psutil

from .config import RunConfig
from .manifest import build_manifest
from .paths import annotations_csv, benchmark_dir, benchmark_manifest_csv, benchmark_results_csv
from .stage1 import run_stage1


class ProcessTreeMonitor:
    def __init__(self, root_pid: int, interval: float = 1.0):
        self.root_pid = root_pid
        self.interval = interval
        self.peak_rss_kb = 0
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _rss_sum(self) -> int:
        try:
            root = psutil.Process(self.root_pid)
        except psutil.Error:
            return 0
        total = root.memory_info().rss
        for child in root.children(recursive=True):
            try:
                total += child.memory_info().rss
            except psutil.Error:
                continue
        return total

    def _run(self) -> None:
        while not self._stop.is_set():
            rss = self._rss_sum()
            self.peak_rss_kb = max(self.peak_rss_kb, rss // 1024)
            time.sleep(self.interval)

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> int:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)
        return self.peak_rss_kb


def build_benchmark_manifest(cfg: RunConfig) -> Path:
    bdir = benchmark_dir(cfg)
    bdir.mkdir(parents=True, exist_ok=True)
    out = benchmark_manifest_csv(cfg)
    if out.exists():
        return out

    sample_size = cfg.benchmark_sample_size or int(cfg.benchmark.get("sample_size", 192))
    seed = int(cfg.benchmark.get("seed", 42))
    per_model = sample_size // len(cfg.models)

    full = build_manifest(
        cfg.audio_root,
        annotations_csv(cfg),
        cfg.model_specs,
        cfg.models,
    )
    parts = []
    for source in cfg.models:
        sub = full[full["source"] == source].sort_values(["year", "position"])
        n = min(per_model, len(sub))
        parts.append(sub.sample(n, random_state=seed))
    bench = pd.concat(parts, ignore_index=True)
    bench.to_csv(out, index=False)
    return out


def parse_time_v_rss(path: Path) -> Optional[int]:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", text)
    return int(m.group(1)) if m else None


def append_benchmark_result(cfg: RunConfig, row: Dict[str, object]) -> None:
    out = benchmark_results_csv(cfg)
    out.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([row])
    if out.exists():
        prev = pd.read_csv(out)
        df = pd.concat([prev, df], ignore_index=True)
    df.to_csv(out, index=False)


def run_benchmark_worker(cfg: RunConfig, workers: int, time_log: Optional[Path] = None) -> Dict[str, object]:
    import os

    from .paths import benchmark_worker_dir

    worker_root = benchmark_worker_dir(cfg, workers)
    worker_root.mkdir(parents=True, exist_ok=True)

    bench_cfg = RunConfig(
        project_root=cfg.project_root,
        audio_root=cfg.audio_root,
        workers=workers,
        models=cfg.models,
        output_scope="smoke",
        force=True,
        limit_per_model=None,
        benchmark_mode=True,
        benchmark_sample_size=cfg.benchmark_sample_size,
        benchmark_output_root=worker_root,
        manifest_path=benchmark_manifest_csv(cfg),
        raw=cfg.raw,
    )

    monitor = ProcessTreeMonitor(root_pid=os.getpid())
    monitor.start()
    t0 = time.time()
    summary = run_stage1(bench_cfg)
    elapsed = time.time() - t0
    peak_rss = monitor.stop()

    parent_rss = parse_time_v_rss(time_log) if time_log else None
    sample_size = int(summary.get("total_tracks", 0))

    row = {
        "workers": workers,
        "sample_size": sample_size,
        "elapsed_sec": round(elapsed, 2),
        "tracks_per_sec": round(sample_size / elapsed, 4) if elapsed > 0 else 0.0,
        "peak_rss_kb": peak_rss,
        "peak_rss_parent_kb": parent_rss,
        "success_count": summary.get("success_count", 0),
        "skip_count": summary.get("skipped_count", 0),
    }
    append_benchmark_result(cfg, row)
    return row


def choose_benchmark_worker(cfg: RunConfig) -> int:
    path = benchmark_results_csv(cfg)
    if not path.exists():
        return cfg.workers
    df = pd.read_csv(path)
    if df.empty:
        return cfg.workers
    best_tps = df["tracks_per_sec"].max()
    candidates = df[df["tracks_per_sec"] >= best_tps * 0.95]
    return int(candidates.sort_values("workers").iloc[-1]["workers"])
