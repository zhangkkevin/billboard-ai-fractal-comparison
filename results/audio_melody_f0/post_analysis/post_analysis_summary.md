# Audio-Melody F0 Post-Analysis Summary

This local post-analysis reads the server outputs in `results/audio_melody_f0/`.
`f0_quality.csv` and `f0_fractal_descriptors.csv` are treated as the source of truth; `manifest.csv` may contain pre-run placeholder statuses.

## Acceptance

- Billboard: 255/381 accepted (66.9%).
- Suno v4.5: 292/381 accepted (76.6%).
- YuE: 153/347 accepted (44.1%).

## Fractal Descriptors

Accepted-set means:
- Billboard: alpha_dfa=1.102, alpha_width=10.15, n=255.
- Suno v4.5: alpha_dfa=1.162, alpha_width=9.30, n=292.
- YuE: alpha_dfa=1.139, alpha_width=8.29, n=153.

Strict quality-filter means (`coverage >= .70`, `median_voiced_prob >= .20`, `jump_rate <= .10`, `octave_jump_rate <= .01`):
- Billboard: alpha_dfa=1.140, alpha_width=10.02, n=114.
- Suno v4.5: alpha_dfa=1.154, alpha_width=9.71, n=244.
- YuE: alpha_dfa=1.152, alpha_width=8.77, n=118.

## Robustness Interpretation

The accepted-set comparison shows source differences, but under the strict combined quality filter the global alpha_dfa Kruskal-Wallis p-value is 0.808. This supports a cautious framing: the strongest result is about contour recoverability and F0 reliability, while fractal descriptor differences should be presented as quality-sensitive rather than definitive melodic differences.

## Output Files

- `tables/acceptance_by_source.csv`
- `tables/acceptance_by_decade.csv`
- `tables/skip_reasons_by_source.csv`
- `tables/quality_summary_by_source.csv`
- `tables/descriptor_summary_by_source.csv`
- `tables/robustness_filter_summary.csv`
- `tables/statistical_tests_by_filter.csv`
- `figures/*.png` and `figures/*.pdf`

Source results root: `results/audio_melody_f0`
