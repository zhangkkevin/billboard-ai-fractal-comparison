# Audio-Melody F0 Dissertation Extension

Status date: 2026-06-25

This note documents the dissertation extension that analyzes audio-derived
vocal F0 contours for Billboard, Suno v4.5, and YuE. It is an audit layer that
complements the published amplitude-envelope DFA/MFDFA paper; it is not a
symbolic-melody replacement for the original analysis.

## What Is Analyzed

- Sources: Billboard, Suno v4.5, and YuE.
- Audio layer: vocal stems only.
- Alignment key: `year` and `position`.
- Unit of analysis: one cleaned F0 contour per accepted vocal stem.
- Fractal descriptors: DFA alpha plus MFDFA descriptors computed on
  median-centered semitone contours.
- Exclusions: DiffRhythm is not included in this F0 audit; BiMMuDa symbolic
  melody annotations are not compared directly with AI auto-extracted contours.

Suno v4.5 is treated as a fixed historical model snapshot. No Suno outputs were
regenerated for this extension.

## Pipeline

Stage 1 runs on the server:

1. Load each vocal stem with `librosa.load(..., sr=22050, mono=True)`.
2. Extract F0 with `librosa.pyin` using frame length 2048, hop length 512,
   `fmin=65.41 Hz`, and `fmax=2093.0 Hz`.
3. Convert voiced F0 from Hz to semitones relative to A4=440 Hz.
4. Select the longest valid region with duration at least 30 seconds and raw
   voiced coverage at least 0.30.
5. Fill short unvoiced gaps up to 0.5 seconds by linear interpolation.
6. Record QA metrics including selected duration, voiced coverage, median
   voiced probability, jump rate, and octave-jump rate.

Stage 2 runs on the server:

1. Compute DFA alpha with the SAFE scale policy and linear detrending.
2. Compute MFDFA descriptors with `q = linspace(-5, 5, 21)` and polynomial
   order 1.
3. Export accepted rows to `results/audio_melody_f0/f0_fractal_descriptors.csv`.

Stage 3 runs locally:

1. Read only the server CSV outputs.
2. Produce acceptance, quality, descriptor, robustness, matched complete-case,
   and decade tables.
3. Export deterministic dissertation-facing figures as PNG and PDF.

Local command:

```bash
python analysis/audio_melody_f0_post_analysis.py --results-root results/audio_melody_f0
```

## Server Run Outcome

- Total vocal stems evaluated: 1109.
- Stage 1 accepted F0 contours: 700.
- Stage 1 skipped contours: 409.
- Stage 2 accepted fractal rows: 700.
- Stage 2 failures: 0.

Accepted contour counts:

- Billboard: 255/381 accepted (66.9%).
- Suno v4.5: 292/381 accepted (76.6%).
- YuE: 153/347 accepted (44.1%).

The acceptance-rate difference is a substantive result in itself: the extension
shows that recoverable vocal-F0 structure differs strongly by source, especially
for YuE.

## Robustness And Complete-Case Sensitivity

Local robustness filters are applied after server acceptance; they do not change
the server result CSVs.

Strict local filter:

- selected voiced coverage >= 0.70
- median pYIN voiced probability >= 0.20
- jump rate <= 0.10
- octave-jump rate <= 0.01

Strict retained rows:

- Billboard: n=114, mean DFA alpha=1.140.
- Suno v4.5: n=244, mean DFA alpha=1.154.
- YuE: n=118, mean DFA alpha=1.152.

The strict-filter global Kruskal-Wallis test for DFA alpha has p=0.808. This
supports a cautious interpretation: source differences in fractal F0 descriptors
are quality-sensitive and should not be treated as definitive melodic-complexity
differences.

Matched complete-case subsets align all sources by year-position:

- Matched accepted subset: 105 triples.
- Matched strict subset: 40 triples.

In the strict matched subset, the paired Friedman test for DFA alpha has
p=0.509. This reinforces the same conclusion: the most robust F0 finding is
about contour recoverability and extraction reliability, not a stable rank
ordering of melodic fractal structure across sources.

## Dissertation Interpretation

Use this extension to make the chapter more complete by showing that the paper's
amplitude-envelope evidence was checked against a second audio-derived layer.
The chapter should frame the F0 analysis as a triangulation and limitation audit:

- Amplitude-envelope DFA/MFDFA remains the primary published analysis.
- F0 contours audit vocal/melodic phrasing only where a reliable contour can be
  extracted.
- Layered vocals, harmonies, separation artifacts, and instrumental sections can
  affect pYIN tracking.
- Low-quality or non-recoverable contours are treated as attrition, not repaired
  with symbolic transcription.

Recommended chapter claim:

> The audio-derived F0 audit does not provide strong evidence for stable
> source-level differences in vocal-contour fractal descriptors after strict
> quality and matched complete-case filtering. Instead, it shows that
> recoverable vocal-F0 structure itself differs by source, and that melodic
> fractal comparisons should be interpreted cautiously.

## Reproducibility Surface

- Server runbook: `server_handoff/billboard_audio_melody_f0/README_CURSOR.md`
- Method parameters: `server_handoff/audio_melody_f0_METHOD_PARAMETERS.json`
- Environment metadata: `server_handoff/audio_melody_f0_env/`
- Redacted annotations: `data/annotations/billboard_annotations_redacted.csv`
- Full server CSV outputs: `results/audio_melody_f0/`
- Portable summaries: `data/results/audio_melody_f0/`
- Local post-analysis script: `analysis/audio_melody_f0_post_analysis.py`
- Local tables and figures: `results/audio_melody_f0/post_analysis/`

Excluded from Git: copyrighted audio, F0/cache `.npz` arrays, and private
lyrics-bearing annotation files.
