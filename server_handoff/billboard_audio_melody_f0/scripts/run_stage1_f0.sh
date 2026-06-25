#!/usr/bin/env bash
set -euo pipefail

PKG_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate fractal_analysis
export PYTHONPATH="${PKG_ROOT}/src:${PKG_ROOT}/third_party"

python -m billboard_audio_melody_f0 stage1-f0 "$@"
