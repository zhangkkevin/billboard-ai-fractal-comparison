#!/usr/bin/env bash
# Build lightweight audio_melody_f0 reproducibility bundle (methodology + CSV summaries, no audio/cache).
set -euo pipefail

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
PROJECT="${PROJECT:-/home/data/kevinzhang/research/fractal_analysis}"
DATE="${DATE:-$(date +%Y%m%d)}"
STAGING="${PROJECT}/server_handoff/audio_melody_f0_repro_bundle"
OUTPUT="${PROJECT}/server_handoff/audio_melody_f0_repro_bundle_${DATE}.tar.gz"
PKG="${PROJECT}/server_handoff/billboard_audio_melody_f0"
RESULTS="${PROJECT}/results/audio_melody_f0"
DISS="${PROJECT}/data/results/audio_melody_f0"
CONDA_ENV="${CONDA_ENV:-fractal_analysis}"

log() { echo "[bundle] $*"; }
die() { echo "[bundle] ERROR: $*" >&2; exit 1; }

require_file() {
  local f="$1"
  [[ -f "$f" ]] || die "missing required file: $f"
}

copy_file() {
  local src="$1" dst="$2"
  require_file "$src"
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
}

copy_glob() {
  local src_pattern="$1" dst_dir="$2"
  shopt -s nullglob
  local files=( $src_pattern )
  shopt -u nullglob
  [[ ${#files[@]} -gt 0 ]] || return 1
  mkdir -p "$dst_dir"
  cp "${files[@]}" "$dst_dir/"
}

MISSING=()

check_required() {
  local rel="$1"
  if [[ ! -e "${PROJECT}/${rel}" ]]; then
    MISSING+=("$rel")
  fi
}

validate_staging() {
  log "validating staging directory"
  local bad
  bad="$(find "$STAGING" \( \
    -iname '*.mp3' -o -iname '*.wav' -o -iname '*.flac' -o -iname '*.m4a' -o -iname '*.aac' -o \
    -iname '*.npz' -o -iname '*.npy' -o -iname '*.pkl' -o -iname '*.joblib' -o \
    -iname '*.pt' -o -iname '*.pth' \
  \) -print -quit || true)"
  [[ -z "$bad" ]] || die "forbidden file type in bundle: $bad"

  bad="$(find "$STAGING" -path '*/audio_data/*' -print -quit || true)"
  [[ -z "$bad" ]] || die "audio_data path in bundle: $bad"

  bad="$(find "$STAGING" -type l -print -quit || true)"
  [[ -z "$bad" ]] || die "symlink in bundle: $bad"

  PROJECT="$PROJECT" STAGING="$STAGING" python - <<'PY'
import os
import pandas as pd

staging = os.environ["STAGING"]
redacted = os.path.join(staging, "data/annotations/billboard_annotations_redacted.csv")
assert os.path.isfile(redacted), "redacted annotations missing"
cols = pd.read_csv(redacted, nrows=0).columns
assert "lyrics" not in cols, f"lyrics column still present: {list(cols)}"
PY

  bad="$(find "$STAGING" -name 'billboard_annotations.csv' -print -quit || true)"
  [[ -z "$bad" ]] || die "original annotations CSV in bundle: $bad"

  log "validation passed"
}

write_env_snapshots() {
  mkdir -p "${STAGING}/env"
  if command -v conda >/dev/null 2>&1; then
    conda run -n "$CONDA_ENV" pip freeze > "${STAGING}/env/pip_freeze.txt" 2>/dev/null || echo "(conda run pip freeze failed)" > "${STAGING}/env/pip_freeze.txt"
    {
      conda run -n "$CONDA_ENV" python --version 2>&1 || true
      conda run -n "$CONDA_ENV" which python 2>&1 || true
    } > "${STAGING}/env/python_version.txt"
  else
    echo "conda not found" > "${STAGING}/env/pip_freeze.txt"
    python3 --version > "${STAGING}/env/python_version.txt" 2>&1 || true
  fi
  {
    echo "=== uname ==="
    uname -a
    echo "=== lscpu (head) ==="
    lscpu 2>/dev/null | head -20 || echo "lscpu unavailable"
    echo "=== free ==="
    free -h 2>/dev/null || echo "free unavailable"
    echo "=== conda info ==="
    conda info 2>/dev/null || echo "conda unavailable"
  } > "${STAGING}/env/system_info.txt"

  if [[ -d "${PROJECT}/.git" ]]; then
    {
      echo "=== HEAD ==="
      git -C "$PROJECT" rev-parse HEAD
      echo "=== status --short ==="
      git -C "$PROJECT" status --short
      echo "=== remotes ==="
      git -C "$PROJECT" remote -v
    } > "${STAGING}/env/git_info.txt"
    GIT_INCLUDED=1
  else
    echo "not a git repository" > "${STAGING}/env/git_info.txt"
    GIT_INCLUDED=0
  fi
}

maybe_copy_logs() {
  LOGS_INCLUDED=0
  local candidates=(
    "${RESULTS}/logs"
    "${PROJECT}/logs"
  )
  local total=0
  for d in "${candidates[@]}"; do
    [[ -d "$d" ]] || continue
    total=$(find "$d" -type f -printf '%s\n' 2>/dev/null | awk '{s+=$1} END {print s+0}')
    if [[ "$total" -gt 0 && "$total" -lt 102400 ]]; then
      mkdir -p "${STAGING}/logs"
      cp -R "$d/." "${STAGING}/logs/"
      LOGS_INCLUDED=1
      log "included logs from $d (${total} bytes)"
      return
    fi
  done
  log "no small logs directory found; skipping logs/"
}

generate_redacted_annotations() {
  if [[ "${INCLUDE_FULL_ANNOTATIONS:-0}" == "1" ]]; then
    die "INCLUDE_FULL_ANNOTATIONS=1 is disabled by default for dissertation-safe bundles; contact maintainer"
  fi
  require_file "${PROJECT}/data/annotations/billboard_annotations.csv"
  mkdir -p "${STAGING}/data/annotations"
  PROJECT="$PROJECT" STAGING="$STAGING" python - <<'PY'
import os
import pandas as pd

src = os.path.join(os.environ["PROJECT"], "data/annotations/billboard_annotations.csv")
dst = os.path.join(os.environ["STAGING"], "data/annotations/billboard_annotations_redacted.csv")
df = pd.read_csv(src)
df = df.drop(columns=["lyrics"], errors="ignore")
df.to_csv(dst, index=False)
PY
  PROJECT="$PROJECT" STAGING="$STAGING" python - <<'PY'
import os, pandas as pd
p = os.path.join(os.environ["STAGING"], "data/annotations/billboard_annotations_redacted.csv")
cols = pd.read_csv(p, nrows=0).columns
assert "lyrics" not in cols, f"lyrics column still present: {list(cols)}"
PY
  log "created redacted annotations (lyrics column removed)"
}

generate_method_parameters() {
  PROJECT="$PROJECT" STAGING="$STAGING" PKG="$PKG" RESULTS="$RESULTS" DATE="$DATE" \
    python - <<'PY'
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

project = Path(os.environ["PROJECT"])
staging = Path(os.environ["STAGING"])
pkg = Path(os.environ["PKG"])
results = Path(os.environ["RESULTS"])
date_stamp = os.environ["DATE"]

cfg_path = pkg / "config/default.yml"
dfa_path = pkg / "third_party/fractal/dfa.py"
mfdfa_path = pkg / "third_party/fractal/mfdfa.py"
contour_path = pkg / "src/billboard_audio_melody_f0/contour_clean.py"
f0_path = pkg / "src/billboard_audio_melody_f0/f0_extract.py"
stage2_path = pkg / "src/billboard_audio_melody_f0/stage2.py"
post_path = project / "analysis/audio_melody_f0_post_analysis.py"

source_files = [cfg_path, dfa_path, mfdfa_path, contour_path, f0_path, stage2_path, post_path]
for p in source_files:
    if not p.is_file():
        raise SystemExit(f"missing source file for metadata: {p}")

with cfg_path.open() as f:
    cfg = yaml.safe_load(f)

dfa_src = dfa_path.read_text()
mfdfa_src = mfdfa_path.read_text()

def extract_dfa_resolutions(src: str) -> list[int]:
    m = re.search(r"def _default_nvals\(.*?\n(.*?)(?:\ndef |\Z)", src, re.S)
    if not m:
        raise SystemExit("could not find _default_nvals")
    m2 = re.search(r"for resolution in \(([^)]+)\)", m.group(1))
    if not m2:
        raise SystemExit("could not find DFA resolution loop")
    return [int(x.strip()) for x in m2.group(1).split(",")]

def extract_mfdfa_resolutions(src: str) -> list[int]:
    m = re.search(r"def _default_lag\(.*?min_scales:\s*int\s*=\s*(\d+)\).*?\n(.*?)(?:\ndef |\Z)", src, re.S)
    if not m:
        raise SystemExit("could not find _default_lag")
    min_scales_default = int(m.group(1))
    m2 = re.search(r"for resolution in \(([^)]+)\)", m.group(2))
    if not m2:
        raise SystemExit("could not find MFDFA resolution loop")
    parts = [x.strip() for x in m2.group(1).split(",")]
    out = []
    for p in parts:
        if p == "min_scales":
            out.append(min_scales_default)
        else:
            out.append(int(p))
    return out

dfa_resolutions = extract_dfa_resolutions(dfa_src)
mfdfa_resolutions = extract_mfdfa_resolutions(mfdfa_src)

if dfa_resolutions != [25, 30, 35, 40]:
    raise SystemExit(f"DFA resolution tuple mismatch: {dfa_resolutions}")
if mfdfa_resolutions != [25, 30, 35, 40, 50]:
    raise SystemExit(f"MFDFA resolution tuple mismatch: {mfdfa_resolutions}")

import sys
sys.path.insert(0, str(staging / "pipeline/billboard_audio_melody_f0/third_party"))
from fractal.summary import get_fractal_params_for_n  # noqa: E402

example_n = 3000
example_params = get_fractal_params_for_n(example_n)

method = {
    "bundle_date": date_stamp,
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "project_root": str(project),
    "config": cfg,
    "f0_extraction": {
        "library": "librosa.pyin",
        "load": "librosa.load(..., sr=sr, mono=True)",
        "sr": cfg["f0"]["sr"],
        "frame_length": cfg["f0"]["frame_length"],
        "hop_length": cfg["f0"]["hop_length"],
        "frame_duration_sec": cfg["f0"]["hop_length"] / cfg["f0"]["sr"],
        "fmin_hz": cfg["f0"]["fmin_hz"],
        "fmax_hz": cfg["f0"]["fmax_hz"],
        "voiced_mask": "voiced_flag from pyin AND f0 > 0 AND finite",
        "voiced_probs": "median over raw voiced frames in selected region",
    },
    "contour_cleaning": {
        "semitone_formula": "12 * log2(f0_hz / 440.0)",
        "reference_pitch_hz": 440.0,
        "centering": "subtract median of voiced semitones in selected region",
        "smoothing": "none beyond short-gap linear interpolation",
        "max_gap_fill_sec": cfg["f0"]["max_gap_fill_sec"],
        "min_region_sec": cfg["f0"]["min_region_sec"],
        "min_region_voiced_coverage": cfg["f0"]["min_region_voiced_coverage"],
        "region_selection": "longest voiced region meeting duration and coverage thresholds",
        "region_split_gap_frames": "max_gap_frames + 1",
        "jump_rate": "fraction of consecutive voiced semitone diffs with abs(diff) > 1.0",
        "octave_jump_rate": "fraction with abs(diff) > 9.0",
        "skip_reasons": ["no_valid_region", "too_short", "low_region_voiced_coverage"],
    },
    "server_acceptance": {
        "stage1_success": "contour_clean success (valid region, duration, coverage gates)",
        "stage2_acceptance": ">= 32 finite semitone samples; NaNs linearly interpolated; finite alpha_dfa",
    },
    "local_robustness_filters": {
        "note": "post_analysis only; does not change server CSV statuses",
        "coverage_ge": 0.70,
        "median_voiced_prob_ge": 0.20,
        "jump_rate_le": 0.10,
        "octave_jump_rate_le": 0.01,
    },
    "dfa_scales": {
        "policy": "SAFE",
        "input_signal": "median-centered semitone contour",
        "integration": "cumsum(x - mean(x))",
        "n_min_formula": "max(16, floor(0.01 * N))",
        "n_max_formula": "floor(0.10 * N)",
        "resolution_candidates": dfa_resolutions,
        "selection_rule": "first unique(logspace(...).astype(int)) filtered to [n_min, n_max] with size >= 20",
        "fallback_resolution": 30,
        "post_filter": "unique nvals; keep only nvals > 1",
        "order": cfg["fractal"]["dfa_order"],
        "library": "nolds.dfa(..., overlap=True, order=1)",
    },
    "mfdfa_lags": {
        "policy": "SAFE",
        "q_min": cfg["fractal"]["q_min"],
        "q_max": cfg["fractal"]["q_max"],
        "q_n": cfg["fractal"]["q_n"],
        "q_construction": "np.linspace(q_min, q_max, q_n); sorted unique; insert 0.0 if missing",
        "min_lag_formula": "max(16, floor(0.01 * N))",
        "max_lag_formula": "floor(0.10 * N)",
        "resolution_candidates": mfdfa_resolutions,
        "selection_rule": "first unique(logspace(...).astype(int)) filtered to [min_lag, max_lag], lag > 0, size >= 25",
        "fallback_resolution": 50,
        "order": cfg["fractal"]["mfdfa_order"],
        "descriptor_definitions": {
            "alpha_width": "max(alpha_curve) - min(alpha_curve) on sorted spectrum",
            "alpha_peak": "alpha at argmax f(alpha)",
            "W_L": "max(alpha_peak - alpha_min, 0)",
            "W_R": "max(alpha_max - alpha_peak, 0)",
            "B": "(W_L - W_R) / (W_L + W_R)",
            "R": "log((W_L + eps) / (W_R + eps))",
            "spectrum_skew": "(alpha_max + alpha_min - 2*alpha_peak) / alpha_width (0 if width <= 1e-12)",
            "delta_Hq": "H(q_min) - H(q_max) on sorted q grid",
        },
    },
    "example_fractal_params_N3000": example_params,
    "source_files": [{"path": str(p), "mtime": p.stat().st_mtime} for p in source_files],
}

(staging / "METHOD_PARAMETERS.json").write_text(json.dumps(method, indent=2) + "\n")
(staging / ".method_params_cache.json").write_text(json.dumps({
    "cfg": cfg,
    "dfa_resolutions": dfa_resolutions,
    "mfdfa_resolutions": mfdfa_resolutions,
    "example_params": example_params,
    "generated_at_utc": method["generated_at_utc"],
}, default=str) + "\n")
print("generated METHOD_PARAMETERS.json")
PY
}

generate_readme() {
  PROJECT="$PROJECT" STAGING="$STAGING" PKG="$PKG" RESULTS="$RESULTS" DATE="$DATE" \
    python - <<'PY'
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import yaml

project = Path(os.environ["PROJECT"])
staging = Path(os.environ["STAGING"])
results = Path(os.environ["RESULTS"])
date_stamp = os.environ["DATE"]

cache = json.loads((staging / ".method_params_cache.json").read_text())
cfg = cache["cfg"]
dfa_resolutions = cache["dfa_resolutions"]
mfdfa_resolutions = cache["mfdfa_resolutions"]
example_params = cache["example_params"]
generated_at = cache["generated_at_utc"]

def load_yaml(p: Path) -> dict:
    if p.is_file():
        with p.open() as f:
            return yaml.safe_load(f) or {}
    return {}

m1 = load_yaml(results / "run_manifest_stage1.yml")
m2 = load_yaml(results / "run_manifest_stage2.yml")

git_head = "unknown"
git_file = staging / "env/git_info.txt"
if git_file.is_file():
    for line in git_file.read_text().splitlines():
        if re.fullmatch(r"[0-9a-f]{40}", line.strip()):
            git_head = line.strip()
            break

qa_count = len(list((staging / "results/audio_melody_f0/qa").glob("*.png"))) if (staging / "results/audio_melody_f0/qa").is_dir() else 0
table_dir = staging / "results/audio_melody_f0/post_analysis/tables"
table_files = sorted(p.name for p in table_dir.glob("*.csv")) if table_dir.is_dir() else []
table_count = len(table_files)
bundle_files = sorted(str(p.relative_to(staging)) for p in staging.rglob("*") if p.is_file() and p.name != ".method_params_cache.json")
bundle_file_count = len(bundle_files)
models = cfg.get("models", {})
included_list = "\n".join(f"- `{p}`" for p in bundle_files)

readme = f"""# Audio-Melody F0 Reproducibility Bundle

## Provenance

- **Bundle created (UTC):** {generated_at}
- **Bundle date stamp:** {date_stamp}
- **Server project path:** `{project}`
- **Git HEAD:** `{git_head}`
- **Stage 1 run:** {m1.get('started_at', 'n/a')} → {m1.get('finished_at', 'n/a')} ({m1.get('elapsed_sec', 'n/a')} s)
- **Stage 2 run:** {m2.get('started_at', 'n/a')} → {m2.get('finished_at', 'n/a')} ({m2.get('elapsed_sec', 'n/a')} s)

### Rebuild this bundle

```bash
PROJECT=/path/to/fractal_analysis bash create_audio_melody_f0_repro_bundle.sh
```

The build script is included at `create_audio_melody_f0_repro_bundle.sh`.

## Server launch commands (completed full run)

```bash
export PROJECT={project}
export PKG=$PROJECT/server_handoff/billboard_audio_melody_f0
export AUDIO=$PROJECT/audio_data

bash $PKG/scripts/run_stage1_f0.sh \\
  --project-root $PROJECT --audio-root $AUDIO \\
  --models billboard suno_v4_5 yue --workers 128 --output-scope full

bash $PKG/scripts/run_stage2_fractal.sh \\
  --project-root $PROJECT --workers 128 --output-scope full
```

**CPU workers:** 128 (thread caps: OMP_NUM_THREADS=1, MKL_NUM_THREADS=1, etc.)

## Audio input roots (vocal stems)

| Source | Path under `$PROJECT/audio_data` | Expected |
|--------|-----------------------------------|----------|
| Billboard | `{models['billboard']['subpath']}/` | {models['billboard']['expected']} |
| Suno v4.5 | `{models['suno_v4_5']['subpath']}/` | {models['suno_v4_5']['expected']} |
| YuE | `{models['yue']['subpath']}/` | {models['yue']['expected']} |

## Annotations (redacted)

- **Included:** `data/annotations/billboard_annotations_redacted.csv` (columns: title, artist, year, position, mood_tone, instrumentation, genre)
- **Excluded:** `data/annotations/billboard_annotations.csv` (contains generated prompt **lyrics**; not for redistribution)
- **Audit use:** redacted file supports methodology audit and track metadata review in the dissertation bundle
- **Re-run note:** manifest join uses only `year`, `position`, `artist`, `title` from annotations (`manifest.py`); redacted CSV is sufficient for manifest rebuild. Exact historical server state used the full private CSV; keep original locally if needed for other workflows

## F0 extraction

- **Method:** `librosa.load(..., sr={cfg['f0']['sr']}, mono=True)` → `librosa.pyin(...)`
- **Sample rate:** {cfg['f0']['sr']} Hz
- **Frame length:** {cfg['f0']['frame_length']}
- **Hop length:** {cfg['f0']['hop_length']} (frame duration = {cfg['f0']['hop_length'] / cfg['f0']['sr']:.5f} s)
- **fmin / fmax:** {cfg['f0']['fmin_hz']} / {cfg['f0']['fmax_hz']} Hz
- **Voiced handling:** raw mask = pyin `voiced_flag` AND `f0 > 0` AND finite; `voiced_probs` summarized as median over raw voiced frames in selected region

## Contour cleaning

- **Conversion:** Hz → semitones via `12*log2(f0/440)`; median-center voiced semitones in selected region
- **Gap fill:** linear interpolation for unvoiced gaps ≤ {cfg['f0']['max_gap_fill_sec']} s
- **Region selection:** longest voiced region with duration ≥ {cfg['f0']['min_region_sec']} s and raw voiced coverage ≥ {cfg['f0']['min_region_voiced_coverage']}
- **Jump rate:** fraction of consecutive voiced-frame semitone diffs with `|diff| > 1.0`
- **Octave jump rate:** fraction with `|diff| > 9.0`
- **Server skip reasons:** `no_valid_region`, `too_short`, `low_region_voiced_coverage`

## Server acceptance vs local robustness filters

| Layer | Where | Criteria | Effect |
|-------|-------|----------|--------|
| Server Stage 1 acceptance | `contour_clean.py` | Valid region; duration ≥ {cfg['f0']['min_region_sec']} s; coverage ≥ {cfg['f0']['min_region_voiced_coverage']} | `f0_quality.csv` status=success; clean contour NPZ on server (not bundled) |
| Server Stage 1 skip | same | fails gates above | status=skipped + reason |
| Server Stage 2 acceptance | `stage2.py` | Stage 1 success; ≥ 32 finite samples after NaN interp; finite `alpha_dfa` | row in `f0_fractal_descriptors.csv` |
| Local robustness filters | `analysis/audio_melody_f0_post_analysis.py` | on accepted rows: coverage ≥ 0.70, median_voiced_prob ≥ 0.20, jump_rate ≤ 0.10, octave_jump_rate ≤ 0.01 | sensitivity tables only; **does not change server CSV statuses** |

## DFA settings

- **Input:** median-centered semitone contour
- **Normalization / detrending:** integrate `cumsum(x - mean(x))`; polynomial detrend order {cfg['fractal']['dfa_order']} per window (`nolds.dfa`, overlap=True)
- **Scale range (SAFE, per signal length N):**
  - `n_min = max(16, floor(0.01 * N))`
  - `n_max = floor(0.10 * N)`
  - Try resolutions {dfa_resolutions}; take first `unique(logspace(log10(n_min), log10(n_max), resolution).astype(int))` within `[n_min, n_max]` with **size ≥ 20**; fallback resolution **30**
  - Pre-fit filter: unique, keep `nvals > 1`
- **Example (N=3000):** min_scale={example_params['min_scale']}, max_scale={example_params['max_scale']}, number_of_scales={example_params['number_of_scales']}
- Per-track scale count is **N-dependent**; see `METHOD_PARAMETERS.json`

## MFDFA settings

- **q values:** linspace({cfg['fractal']['q_min']}, {cfg['fractal']['q_max']}, {cfg['fractal']['q_n']}); sorted unique; insert 0.0 if missing
- **Lag range (SAFE, per N):**
  - `min_lag = max(16, floor(0.01 * N))`
  - `max_lag = floor(0.10 * N)`
  - Try resolutions {mfdfa_resolutions}; first array with **size ≥ 25**; fallback resolution **50**
- **Polynomial order:** {cfg['fractal']['mfdfa_order']} (MFDFA package)
- **Descriptors:** alpha_width, alpha_peak, W_L, W_R, B, R, spectrum_skew, delta_Hq — definitions in `METHOD_PARAMETERS.json`

## Run outcomes (from run manifests)

- **Stage 1:** total={m1.get('total_tracks', 'n/a')}, success={m1.get('success_count', 'n/a')}, skipped={m1.get('skipped_count', 'n/a')}, failed={m1.get('failed_count', 'n/a')}, workers={m1.get('workers', 'n/a')}
- **Stage 2:** accepted={m2.get('accepted_count', 'n/a')}, skipped={m2.get('skipped_count', 'n/a')}, failed={m2.get('failed_count', 'n/a')}, workers={m2.get('workers', 'n/a')}

## Known caveats

- F0 contours are audio-derived audits, not symbolic melody transcriptions
- Layered vocals/harmonies can affect pYIN tracking
- BiMMuDa symbolic melodies are not directly compared against AI auto-transcriptions
- Suno v4.5 is treated as a fixed historical model snapshot
- `manifest.csv` may retain pre-run placeholder statuses; treat `f0_quality.csv` and `f0_fractal_descriptors.csv` as authoritative

## Bundle inventory

- **Total files:** {bundle_file_count}
- **QA PNGs:** {qa_count}
- **Post-analysis tables:** {table_count} ({', '.join(table_files) if table_files else 'none'})

### Included files

{included_list}

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
"""

(staging / "README_AUDIO_MELODY_F0_REPRO.md").write_text(readme)
print("generated README_AUDIO_MELODY_F0_REPRO.md")
PY
}

generate_metadata_and_readme() {
  generate_method_parameters
}

# --- main ---
log "project=$PROJECT date=$DATE"
log "staging=$STAGING"
log "output=$OUTPUT"

[[ -d "$PKG" ]] || die "package not found: $PKG"

if find "$PKG" -type l -print -quit | grep -q .; then
  echo "ERROR: symlink found in source package; review before bundling" >&2
  find "$PKG" -type l -print >&2
  exit 1
fi

rm -rf "$STAGING"
mkdir -p "$STAGING/pipeline" "$STAGING/analysis" "$STAGING/data" "$STAGING/results/audio_melody_f0"

cp -R "$PKG" "${STAGING}/pipeline/billboard_audio_melody_f0"
copy_file "${PROJECT}/requirements.txt" "${STAGING}/requirements.txt"
copy_file "${PROJECT}/analysis/audio_melody_f0_post_analysis.py" "${STAGING}/analysis/audio_melody_f0_post_analysis.py"
cp "$SCRIPT_PATH" "${STAGING}/create_audio_melody_f0_repro_bundle.sh"
chmod +x "${STAGING}/create_audio_melody_f0_repro_bundle.sh"

generate_redacted_annotations

for rel in \
  run_manifest_stage1.yml \
  run_manifest_stage2.yml \
  manifest.csv \
  f0_quality.csv \
  f0_fractal_descriptors.csv \
  group_summary.csv; do
  check_required "results/audio_melody_f0/${rel}"
  copy_file "${RESULTS}/${rel}" "${STAGING}/results/audio_melody_f0/${rel}"
done

check_required "results/audio_melody_f0/post_analysis/post_analysis_summary.md"
copy_file "${RESULTS}/post_analysis/post_analysis_summary.md" \
  "${STAGING}/results/audio_melody_f0/post_analysis/post_analysis_summary.md"

mkdir -p "${STAGING}/results/audio_melody_f0/post_analysis/tables"
if copy_glob "${RESULTS}/post_analysis/tables/*.csv" "${STAGING}/results/audio_melody_f0/post_analysis/tables/"; then
  :
else
  MISSING+=("results/audio_melody_f0/post_analysis/tables/*.csv")
fi

mkdir -p "${STAGING}/data/results/audio_melody_f0"
for rel in f0_fractal_summary.csv f0_quality_summary.csv README.md; do
  if [[ -f "${DISS}/${rel}" ]]; then
    cp "${DISS}/${rel}" "${STAGING}/data/results/audio_melody_f0/${rel}"
  else
    MISSING+=("data/results/audio_melody_f0/${rel}")
  fi
done

mkdir -p "${STAGING}/results/audio_melody_f0/smoke/benchmark"
for rel in benchmark_manifest.csv benchmark_results.csv; do
  src="${RESULTS}/smoke/benchmark/${rel}"
  if [[ -f "$src" ]]; then
    cp "$src" "${STAGING}/results/audio_melody_f0/smoke/benchmark/${rel}"
  else
    MISSING+=("results/audio_melody_f0/smoke/benchmark/${rel}")
  fi
done

mkdir -p "${STAGING}/results/audio_melody_f0/qa"
if copy_glob "${RESULTS}/qa/*.png" "${STAGING}/results/audio_melody_f0/qa/"; then
  :
else
  MISSING+=("results/audio_melody_f0/qa/*.png")
fi

write_env_snapshots
maybe_copy_logs

generate_metadata_and_readme

validate_staging

generate_readme

(
  cd "$STAGING"
  find . -type f ! -name SHA256SUMS.txt ! -name '.method_params_cache.json' -print0 \
    | sort -z \
    | xargs -0 sha256sum > SHA256SUMS.txt
)
CHECKSUM_COUNT=$(wc -l < "${STAGING}/SHA256SUMS.txt")

generate_readme

rm -f "${STAGING}/.method_params_cache.json"

(
  cd "$STAGING"
  find . -type f ! -name SHA256SUMS.txt -print0 \
    | sort -z \
    | xargs -0 sha256sum > SHA256SUMS.txt
)
CHECKSUM_COUNT=$(wc -l < "${STAGING}/SHA256SUMS.txt")

tar -czf "$OUTPUT" -C "$(dirname "$STAGING")" "$(basename "$STAGING")"

UNCOMPRESSED=$(du -sh "$STAGING" | awk '{print $1}')
COMPRESSED=$(ls -lh "$OUTPUT" | awk '{print $5}')
BUNDLE_FILE_COUNT=$(find "$STAGING" -type f | wc -l)
QA_COUNT=$(find "${STAGING}/results/audio_melody_f0/qa" -name '*.png' 2>/dev/null | wc -l)
TABLE_COUNT=$(find "${STAGING}/results/audio_melody_f0/post_analysis/tables" -name '*.csv' 2>/dev/null | wc -l)

log "=== FINAL REPORT ==="
echo "Bundle path:     $OUTPUT"
echo "Compressed:      $COMPRESSED"
echo "Uncompressed:    $UNCOMPRESSED"
echo "Files included:  $BUNDLE_FILE_COUNT"
echo "QA PNGs:         $QA_COUNT"
echo "Post-analysis tables: $TABLE_COUNT"
echo "SHA256SUMS:      ${STAGING}/SHA256SUMS.txt ($CHECKSUM_COUNT entries)"
echo "git_info.txt:    included=$GIT_INCLUDED"
echo "logs/:           included=$LOGS_INCLUDED"
echo "Redacted annotations: yes (lyrics column absent)"
echo "Original billboard_annotations.csv: excluded"
echo "Validation:      no forbidden extensions, no audio_data paths, no symlinks"
if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo "Missing expected files:"
  printf '  - %s\n' "${MISSING[@]}"
else
  echo "Missing expected files: none"
fi
echo "Audio/NPZ check: no .mp3/.wav/.npz/.npy files in bundle (confirmed)"
log "done"
