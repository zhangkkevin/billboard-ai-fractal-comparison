# Audio-Melody F0 Reproducibility Bundle

Local repo note: this document was copied from the verified server bundle
`audio_melody_f0_repro_bundle_20260625.tar.gz`. The raw tarball inventory below
records the server bundle exactly, including Python bytecode cache entries. The
repo-facing copy under `server_handoff/billboard_audio_melody_f0/` intentionally
excludes `__pycache__/`, `.pyc`, audio files, and contour/cache arrays. The
repo-facing config uses the redacted annotation CSV because the pipeline only
needs `year`, `position`, `artist`, and `title` for manifest joins.

## Provenance

- **Bundle created (UTC):** 2026-06-25T09:58:21.589297+00:00
- **Bundle date stamp:** 20260625
- **Server project path:** `/home/data/kevinzhang/research/fractal_analysis`
- **Git HEAD:** `49fc576604a88685ebd8b7c340e5e74a4086c88e`
- **Stage 1 run:** 2026-06-22T12:10:40.818923+00:00 → 2026-06-22T12:52:11.228451+00:00 (2490.409528 s)
- **Stage 2 run:** 2026-06-22T12:52:24.836845+00:00 → 2026-06-22T12:52:30.720908+00:00 (5.884063 s)

### Rebuild this bundle

```bash
PROJECT=/path/to/fractal_analysis bash create_audio_melody_f0_repro_bundle.sh
```

The build script is included at `create_audio_melody_f0_repro_bundle.sh`.

## Server launch commands (completed full run)

```bash
export PROJECT=/home/data/kevinzhang/research/fractal_analysis
export PKG=$PROJECT/server_handoff/billboard_audio_melody_f0
export AUDIO=$PROJECT/audio_data

bash $PKG/scripts/run_stage1_f0.sh \
  --project-root $PROJECT --audio-root $AUDIO \
  --models billboard suno_v4_5 yue --workers 128 --output-scope full

bash $PKG/scripts/run_stage2_fractal.sh \
  --project-root $PROJECT --workers 128 --output-scope full
```

**CPU workers:** 128 (thread caps: OMP_NUM_THREADS=1, MKL_NUM_THREADS=1, etc.)

## Audio input roots (vocal stems)

| Source | Path under `$PROJECT/audio_data` | Expected |
|--------|-----------------------------------|----------|
| Billboard | `billboard/vocals/full_duration/` | 381 |
| Suno v4.5 | `suno_v4_5/vocals/batch_1/` | 381 |
| YuE | `YuE/vocals/` | 347 |

## Annotations (redacted)

- **Included:** `data/annotations/billboard_annotations_redacted.csv` (columns: title, artist, year, position, mood_tone, instrumentation, genre)
- **Excluded:** `data/annotations/billboard_annotations.csv` (contains generated prompt **lyrics**; not for redistribution)
- **Audit use:** redacted file supports methodology audit and track metadata review in the dissertation bundle
- **Re-run note:** manifest join uses only `year`, `position`, `artist`, `title` from annotations (`manifest.py`); redacted CSV is sufficient for manifest rebuild. Exact historical server state used the full private CSV; keep original locally if needed for other workflows

## F0 extraction

- **Method:** `librosa.load(..., sr=22050, mono=True)` → `librosa.pyin(...)`
- **Sample rate:** 22050 Hz
- **Frame length:** 2048
- **Hop length:** 512 (frame duration = 0.02322 s)
- **fmin / fmax:** 65.41 / 2093.0 Hz
- **Voiced handling:** raw mask = pyin `voiced_flag` AND `f0 > 0` AND finite; `voiced_probs` summarized as median over raw voiced frames in selected region

## Contour cleaning

- **Conversion:** Hz → semitones via `12*log2(f0/440)`; median-center voiced semitones in selected region
- **Gap fill:** linear interpolation for unvoiced gaps ≤ 0.5 s
- **Region selection:** longest voiced region with duration ≥ 30.0 s and raw voiced coverage ≥ 0.3
- **Jump rate:** fraction of consecutive voiced-frame semitone diffs with `|diff| > 1.0`
- **Octave jump rate:** fraction with `|diff| > 9.0`
- **Server skip reasons:** `no_valid_region`, `too_short`, `low_region_voiced_coverage`

## Server acceptance vs local robustness filters

| Layer | Where | Criteria | Effect |
|-------|-------|----------|--------|
| Server Stage 1 acceptance | `contour_clean.py` | Valid region; duration ≥ 30.0 s; coverage ≥ 0.3 | `f0_quality.csv` status=success; clean contour NPZ on server (not bundled) |
| Server Stage 1 skip | same | fails gates above | status=skipped + reason |
| Server Stage 2 acceptance | `stage2.py` | Stage 1 success; ≥ 32 finite samples after NaN interp; finite `alpha_dfa` | row in `f0_fractal_descriptors.csv` |
| Local robustness filters | `analysis/audio_melody_f0_post_analysis.py` | on accepted rows: coverage ≥ 0.70, median_voiced_prob ≥ 0.20, jump_rate ≤ 0.10, octave_jump_rate ≤ 0.01 | sensitivity tables only; **does not change server CSV statuses** |

## DFA settings

- **Input:** median-centered semitone contour
- **Normalization / detrending:** integrate `cumsum(x - mean(x))`; polynomial detrend order 1 per window (`nolds.dfa`, overlap=True)
- **Scale range (SAFE, per signal length N):**
  - `n_min = max(16, floor(0.01 * N))`
  - `n_max = floor(0.10 * N)`
  - Try resolutions [25, 30, 35, 40]; take first `unique(logspace(log10(n_min), log10(n_max), resolution).astype(int))` within `[n_min, n_max]` with **size ≥ 20**; fallback resolution **30**
  - Pre-fit filter: unique, keep `nvals > 1`
- **Example (N=3000):** min_scale=30, max_scale=300, number_of_scales=24
- Per-track scale count is **N-dependent**; see `METHOD_PARAMETERS.json`

## MFDFA settings

- **q values:** linspace(-5, 5, 21); sorted unique; insert 0.0 if missing
- **Lag range (SAFE, per N):**
  - `min_lag = max(16, floor(0.01 * N))`
  - `max_lag = floor(0.10 * N)`
  - Try resolutions [25, 30, 35, 40, 50]; first array with **size ≥ 25**; fallback resolution **50**
- **Polynomial order:** 1 (MFDFA package)
- **Descriptors:** alpha_width, alpha_peak, W_L, W_R, B, R, spectrum_skew, delta_Hq — definitions in `METHOD_PARAMETERS.json`

## Run outcomes (from run manifests)

- **Stage 1:** total=1109, success=700, skipped=409, failed=0, workers=128
- **Stage 2:** accepted=700, skipped=409, failed=0, workers=128

## Known caveats

- F0 contours are audio-derived audits, not symbolic melody transcriptions
- Layered vocals/harmonies can affect pYIN tracking
- BiMMuDa symbolic melodies are not directly compared against AI auto-transcriptions
- Suno v4.5 is treated as a fixed historical model snapshot
- `manifest.csv` may retain pre-run placeholder statuses; treat `f0_quality.csv` and `f0_fractal_descriptors.csv` as authoritative

## Bundle inventory

- **Total files:** 111
- **QA PNGs:** 24
- **Post-analysis tables:** 8 (acceptance_by_decade.csv, acceptance_by_source.csv, alpha_dfa_by_decade.csv, descriptor_summary_by_source.csv, quality_summary_by_source.csv, robustness_filter_summary.csv, skip_reasons_by_source.csv, statistical_tests_by_filter.csv)

### Included files

- `METHOD_PARAMETERS.json`
- `README_AUDIO_MELODY_F0_REPRO.md`
- `SHA256SUMS.txt`
- `analysis/audio_melody_f0_post_analysis.py`
- `create_audio_melody_f0_repro_bundle.sh`
- `data/annotations/billboard_annotations_redacted.csv`
- `data/results/audio_melody_f0/README.md`
- `data/results/audio_melody_f0/f0_fractal_summary.csv`
- `data/results/audio_melody_f0/f0_quality_summary.csv`
- `env/git_info.txt`
- `env/pip_freeze.txt`
- `env/python_version.txt`
- `env/system_info.txt`
- `pipeline/billboard_audio_melody_f0/README_CURSOR.md`
- `pipeline/billboard_audio_melody_f0/VENDORED_FRACTAL_SOURCE.md`
- `pipeline/billboard_audio_melody_f0/config/default.yml`
- `pipeline/billboard_audio_melody_f0/environment.yml`
- `pipeline/billboard_audio_melody_f0/scripts/package_stage3_local.sh`
- `pipeline/billboard_audio_melody_f0/scripts/run_benchmark_stage1.sh`
- `pipeline/billboard_audio_melody_f0/scripts/run_stage1_f0.sh`
- `pipeline/billboard_audio_melody_f0/scripts/run_stage2_fractal.sh`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__init__.py`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__main__.py`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__pycache__/__init__.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__pycache__/__main__.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__pycache__/benchmark.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__pycache__/cli.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__pycache__/config.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__pycache__/contour_clean.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__pycache__/f0_extract.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__pycache__/manifest.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__pycache__/paths.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__pycache__/qa.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__pycache__/stage1.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__pycache__/stage2.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__pycache__/summaries.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/__pycache__/workers.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/benchmark.py`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/cli.py`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/config.py`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/contour_clean.py`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/f0_extract.py`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/manifest.py`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/paths.py`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/qa.py`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/stage1.py`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/stage2.py`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/summaries.py`
- `pipeline/billboard_audio_melody_f0/src/billboard_audio_melody_f0/workers.py`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__init__.py`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__pycache__/__init__.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__pycache__/__init__.cpython-311.pyc`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__pycache__/__init__.cpython-313.pyc`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__pycache__/dfa.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__pycache__/dfa.cpython-311.pyc`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__pycache__/dfa.cpython-313.pyc`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__pycache__/mfdfa.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__pycache__/mfdfa.cpython-311.pyc`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__pycache__/mfdfa.cpython-313.pyc`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__pycache__/shape.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__pycache__/shape.cpython-311.pyc`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__pycache__/shape.cpython-313.pyc`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__pycache__/summary.cpython-310.pyc`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__pycache__/summary.cpython-311.pyc`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/__pycache__/summary.cpython-313.pyc`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/dfa.py`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/mfdfa.py`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/shape.py`
- `pipeline/billboard_audio_melody_f0/third_party/fractal/summary.py`
- `requirements.txt`
- `results/audio_melody_f0/f0_fractal_descriptors.csv`
- `results/audio_melody_f0/f0_quality.csv`
- `results/audio_melody_f0/group_summary.csv`
- `results/audio_melody_f0/manifest.csv`
- `results/audio_melody_f0/post_analysis/post_analysis_summary.md`
- `results/audio_melody_f0/post_analysis/tables/acceptance_by_decade.csv`
- `results/audio_melody_f0/post_analysis/tables/acceptance_by_source.csv`
- `results/audio_melody_f0/post_analysis/tables/alpha_dfa_by_decade.csv`
- `results/audio_melody_f0/post_analysis/tables/descriptor_summary_by_source.csv`
- `results/audio_melody_f0/post_analysis/tables/quality_summary_by_source.csv`
- `results/audio_melody_f0/post_analysis/tables/robustness_filter_summary.csv`
- `results/audio_melody_f0/post_analysis/tables/skip_reasons_by_source.csv`
- `results/audio_melody_f0/post_analysis/tables/statistical_tests_by_filter.csv`
- `results/audio_melody_f0/qa/billboard_alpha_dfa_high_billboard_1988_05.png`
- `results/audio_melody_f0/qa/billboard_alpha_dfa_low_billboard_2006_02.png`
- `results/audio_melody_f0/qa/billboard_alpha_width_wide_billboard_1980_01.png`
- `results/audio_melody_f0/qa/billboard_octave_jump_high_billboard_1962_03.png`
- `results/audio_melody_f0/qa/billboard_random_0_billboard_2015_01.png`
- `results/audio_melody_f0/qa/billboard_random_1_billboard_1950_02.png`
- `results/audio_melody_f0/qa/billboard_random_2_billboard_1994_03.png`
- `results/audio_melody_f0/qa/billboard_voiced_coverage_low_billboard_1988_05.png`
- `results/audio_melody_f0/qa/suno_v4_5_alpha_dfa_high_suno_v4_5_1975_01.png`
- `results/audio_melody_f0/qa/suno_v4_5_alpha_dfa_low_suno_v4_5_2015_04.png`
- `results/audio_melody_f0/qa/suno_v4_5_alpha_width_wide_suno_v4_5_1998_04.png`
- `results/audio_melody_f0/qa/suno_v4_5_octave_jump_high_suno_v4_5_1998_03.png`
- `results/audio_melody_f0/qa/suno_v4_5_random_0_suno_v4_5_1973_04.png`
- `results/audio_melody_f0/qa/suno_v4_5_random_1_suno_v4_5_2019_03.png`
- `results/audio_melody_f0/qa/suno_v4_5_random_2_suno_v4_5_1962_04.png`
- `results/audio_melody_f0/qa/suno_v4_5_voiced_coverage_low_suno_v4_5_1958_02b.png`
- `results/audio_melody_f0/qa/yue_alpha_dfa_high_yue_1961_02.png`
- `results/audio_melody_f0/qa/yue_alpha_dfa_low_yue_2013_04.png`
- `results/audio_melody_f0/qa/yue_alpha_width_wide_yue_2016_05.png`
- `results/audio_melody_f0/qa/yue_octave_jump_high_yue_1952_01.png`
- `results/audio_melody_f0/qa/yue_random_0_yue_2007_05.png`
- `results/audio_melody_f0/qa/yue_random_1_yue_1987_05.png`
- `results/audio_melody_f0/qa/yue_random_2_yue_2017_02.png`
- `results/audio_melody_f0/qa/yue_voiced_coverage_low_yue_1952_01.png`
- `results/audio_melody_f0/run_manifest_stage1.yml`
- `results/audio_melody_f0/run_manifest_stage2.yml`
- `results/audio_melody_f0/smoke/benchmark/benchmark_manifest.csv`
- `results/audio_melody_f0/smoke/benchmark/benchmark_results.csv`

## Intentionally excluded (patterns / counts)

- `results/audio_melody_f0/cache/f0/*.npz` — ~1,109 files (~25 MB on server)
- `results/audio_melody_f0/cache/clean_contours/*.npz` — ~1,109 files (~8 MB)
- `results/audio_melody_f0/smoke/**` except 2 benchmark CSVs — smoke caches, QA, worker dirs (~1,536 benchmark NPZ files)
- `post_analysis/figures/**` — local figure outputs (~1.8 MB)
- `audio_data/**` — vocal stem audio (copyrighted / generated media)
- `data/annotations/billboard_annotations.csv` — lyrics-bearing original (redacted version included instead)
- Forbidden extensions: `*.mp3`, `*.wav`, `*.flac`, `*.m4a`, `*.aac`, `*.npz`, `*.npy`, `*.pkl`, `*.joblib`, `*.pt`, `*.pth`

## Machine-readable parameters

See `METHOD_PARAMETERS.json` and `env/pip_freeze.txt`.
