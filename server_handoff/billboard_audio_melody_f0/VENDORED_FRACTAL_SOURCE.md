# Vendored Fractal Source

Copied from: `/home/data/kevinzhang/research/fractal_analysis/scripts/fractal/`

Original lineage: `fractal-music-control-space/fractal` (local research repo).

## Files

- `__init__.py`
- `dfa.py` — DFA with SAFE scale policy via `nolds`
- `mfdfa.py` — MFDFA spectrum via `MFDFA` package
- `shape.py` — multifractal spectrum shape descriptors
- `summary.py` — `compute_fractal_descriptors_1d()` entry point

## Settings (SAFE policy)

- `qvals = np.linspace(-5, 5, 21)`
- DFA order 1, MFDFA order 1
- `min_scale = max(16, floor(0.01 * N))`, `max_scale = floor(0.10 * N)`, log-spaced scales

## Adapter

Stage 2 imports `compute_fractal_descriptors_1d` from this vendored copy via `PYTHONPATH`.
