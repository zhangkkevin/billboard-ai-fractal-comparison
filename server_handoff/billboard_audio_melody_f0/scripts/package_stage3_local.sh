#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-root)
      PROJECT_ROOT="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

if [[ -z "${PROJECT_ROOT}" ]]; then
  echo "Usage: $0 --project-root /path/to/fractal_analysis" >&2
  exit 1
fi

RESULTS="${PROJECT_ROOT}/results/audio_melody_f0"
DISS="${PROJECT_ROOT}/data/results/audio_melody_f0"
OUT="${RESULTS}/local_post_analysis_bundle.tar.gz"

TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

mkdir -p "${TMP}/results/audio_melody_f0" "${TMP}/data/results/audio_melody_f0"

for f in manifest.csv f0_quality.csv f0_fractal_descriptors.csv group_summary.csv run_manifest_stage1.yml run_manifest_stage2.yml; do
  if [[ -f "${RESULTS}/${f}" ]]; then
    cp "${RESULTS}/${f}" "${TMP}/results/audio_melody_f0/"
  fi
done

if [[ -d "${DISS}" ]]; then
  cp -r "${DISS}/." "${TMP}/data/results/audio_melody_f0/"
fi

if [[ -d "${RESULTS}/qa" ]]; then
  mkdir -p "${TMP}/results/audio_melody_f0/qa"
  cp -r "${RESULTS}/qa/." "${TMP}/results/audio_melody_f0/qa/"
fi

tar -czf "${OUT}" -C "${TMP}" results data
echo "Created ${OUT}"
ls -lh "${OUT}"
