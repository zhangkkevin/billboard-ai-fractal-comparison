# Billboard Audio-Melody F0 Fractal Analysis — Server Runbook

Project root: `/home/data/kevinzhang/research/fractal_analysis`  
Package: `server_handoff/billboard_audio_melody_f0/`  
Conda env: `fractal_analysis`

## Preflight (verified 2026-06-22)

| Source | Path | Count |
|--------|------|------:|
| Billboard | `audio_data/billboard/vocals/full_duration/` | 381 |
| Suno v4.5 batch 1 | `audio_data/suno_v4_5/vocals/batch_1/` | 381 |
| YuE | `audio_data/YuE/vocals/` | 347 |

## Environment

```bash
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate fractal_analysis
export PKG=/home/data/kevinzhang/research/fractal_analysis/server_handoff/billboard_audio_melody_f0
export PROJECT=/home/data/kevinzhang/research/fractal_analysis
export AUDIO=$PROJECT/audio_data
```

Shell scripts set `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, etc., and resolve `PKG_ROOT` internally.

## Smoke test (completed)

```bash
bash $PKG/scripts/run_stage1_f0.sh \
  --project-root $PROJECT --audio-root $AUDIO \
  --models billboard suno_v4_5 yue --workers 16 \
  --limit-per-model 3 --output-scope smoke

bash $PKG/scripts/run_stage2_fractal.sh \
  --project-root $PROJECT --workers 16 --output-scope smoke
```

Results: 4/9 F0 success (instrumental/short tracks skipped as expected); 4/4 accepted fractal rows after NaN interpolation fix.

Output: `results/audio_melody_f0/smoke/`

## Worker benchmark (completed)

```bash
bash $PKG/scripts/run_benchmark_stage1.sh \
  --project-root $PROJECT --audio-root $AUDIO \
  --models billboard suno_v4_5 yue \
  --benchmark-sample-size 192 --worker-counts 16,32,64,128
```

| workers | tracks/sec | peak_rss_kb (process tree) | success | skip |
|--------:|-----------:|---------------------------:|--------:|-----:|
| 16 | 0.256 | 12,597,480 (~12 GB) | 110 | 82 |
| 32 | 0.399 | 24,085,504 (~23 GB) | 110 | 82 |
| 64 | 0.368 | 43,946,468 (~42 GB) | 110 | 82 |
| **128** | **0.478** | 83,683,868 (~80 GB) | 110 | 82 |

**Chosen worker count: 128** (best throughput; within server RAM headroom).

Benchmark artifacts: `results/audio_melody_f0/smoke/benchmark/`

## Full Stage 1 (completed)

```bash
bash $PKG/scripts/run_stage1_f0.sh \
  --project-root $PROJECT --audio-root $AUDIO \
  --models billboard suno_v4_5 yue --workers 128 \
  --output-scope full
```

| Metric | Value |
|--------|------:|
| Elapsed | 2490 s (~41.5 min) |
| Workers | 128 |
| Total tracks | 1109 |
| F0 success | 700 |
| F0 skipped | 409 |
| F0 failed | 0 |

Per-model F0 success: billboard 255, suno_v4_5 292, yue 153

Outputs:
- `results/audio_melody_f0/manifest.csv`
- `results/audio_melody_f0/f0_quality.csv`
- `results/audio_melody_f0/cache/f0/*.npz`
- `results/audio_melody_f0/cache/clean_contours/*.npz`
- `results/audio_melody_f0/run_manifest_stage1.yml`

## Full Stage 2 (completed)

```bash
bash $PKG/scripts/run_stage2_fractal.sh \
  --project-root $PROJECT --workers 128 --output-scope full
```

| Metric | Value |
|--------|------:|
| Elapsed | 5.9 s |
| Workers | 128 |
| Accepted (finite alpha_dfa) | 700 |
| Skipped | 409 |
| Failed | 0 |

Outputs:
- `results/audio_melody_f0/f0_fractal_descriptors.csv`
- `results/audio_melody_f0/group_summary.csv`
- `results/audio_melody_f0/run_manifest_stage2.yml`
- `results/audio_melody_f0/qa/*.png` (required QA plots)
- `data/results/audio_melody_f0/f0_fractal_summary.csv`
- `data/results/audio_melody_f0/f0_quality_summary.csv`
- `data/results/audio_melody_f0/README.md`

## Stage 3 local bundle (completed)

```bash
bash $PKG/scripts/package_stage3_local.sh --project-root $PROJECT
```

Bundle: `results/audio_melody_f0/local_post_analysis_bundle.tar.gz` (~2.2 MB)

Excludes: audio, `.npz` caches, `smoke/` subtree.

## CLI reference

```bash
python -m billboard_audio_melody_f0 stage1-f0 --help
python -m billboard_audio_melody_f0 stage2-fractal --help
python -m billboard_audio_melody_f0 benchmark-stage1 --help
```

## Notes

- Tied-chart positions (`2a`, `2b`) parsed via `^(\d{4})_([0-9]+[A-Za-z]?)_`; normalized to e.g. `02a`.
- The repo-facing `config/default.yml` points to
  `data/annotations/billboard_annotations_redacted.csv`; this contains all
  metadata needed for manifest joins. The historical server run used the
  private lyrics-bearing annotation CSV before bundle redaction.
- `selected_voiced_coverage` uses raw pre-fill voiced mask within selected region (not gap-interpolated frames).
- Fractal: vendored `scripts/fractal/` → `third_party/fractal/`; SAFE scale policy, q ∈ [-5, 5] × 21.
- Does **not** read BiMMuDa MIDI, `vocal_to_midi.py`, or `results/midi/*`.
