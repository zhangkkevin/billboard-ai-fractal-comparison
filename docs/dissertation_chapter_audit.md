# Dissertation Chapter Audit

Initial audit date: 2026-06-21  
Audio-melody F0 update: 2026-06-25

This note summarizes the local repository state for turning the completed
Billboard/AI paper into a dissertation-ready chapter. It is intentionally
focused on reproducibility and on a narrow possible extension using
audio-derived F0 contours.

## 2026-06-25 Audio-Melody F0 Update

The narrow F0 extension has now been executed on the server and promoted into a
repo-facing reproducibility packet. The repo now includes:

- `server_handoff/billboard_audio_melody_f0/`: server runbook, package code,
  scripts, config, and vendored fractal helpers used for F0 DFA/MFDFA.
- `server_handoff/audio_melody_f0_METHOD_PARAMETERS.json`: complete method
  parameters exported from the server bundle.
- `server_handoff/audio_melody_f0_env/`: server Git, Python, package, and system
  metadata.
- `data/annotations/billboard_annotations_redacted.csv`: metadata without the
  lyrics-bearing annotation column.
- `results/audio_melody_f0/`: server CSV outputs, run manifests, QA PNGs, and
  local post-analysis tables/figures.
- `data/results/audio_melody_f0/`: portable summary CSVs for dissertation use.
- `analysis/audio_melody_f0_post_analysis.py`: local post-analysis script for
  robustness, matched complete-case sensitivity, and stable figures.
- `docs/audio_melody_f0_reproducibility.md`: verified server bundle provenance.
- `docs/audio_melody_f0_dissertation_extension.md`: chapter-facing methodology
  and interpretation note.

The raw server bundle was verified by SHA-256 checksum before promotion. The
repo-facing copy intentionally excludes audio, contour/cache arrays, `.pyc`
files, and private lyrics-bearing annotations.

## Source Roles

- Code and reproducible analysis source: this repository.
- Manuscript source: Prism/OpenAI dissertation manuscript.
- Planning and source indexing: Obsidian vault.
- Large audio data: external Google Drive path supplied in the chapter thread.

Do not copy the large audio corpus into this repository or the Obsidian vault.

## Current Repository Layout

- `analysis/`
  - `dfa_batch_amplitude_envelope.py`: batch DFA over amplitude envelopes.
  - `mfdfa_batch_amplitude_envelope.py`: batch MFDFA over amplitude envelopes.
- `data/annotations/`
  - `billboard_annotations_redacted.csv`: clone-safe metadata for Billboard
    target songs, excluding lyrics.
  - `billboard_annotations.csv`: private/local prompt metadata with lyrics;
    excluded from new reproducibility bundles and ignored going forward.
- `data/results/`
  - `dfa/`: precomputed DFA CSVs for Billboard, Suno, DiffRhythm, and YuE.
  - `mfdfa/`: precomputed MFDFA CSVs for the same sources.
- `notebooks/`
  - `dfa_music_structure.ipynb`: analysis and plotting for DFA results.
  - `mfdfa_music_structure.ipynb`: analysis and plotting for MFDFA, JSD,
    descriptor summaries, and RMSE-style comparisons.
- `docs/`
  - GitHub Pages listening-demo site with selected AI MP3 examples and
    Spotify embeds for selected Billboard tracks.
- `assets/images/`
  - ACM logo only. There is no dedicated exported figure directory.

## Checked-In Result Counts

- DFA: Billboard 381, Suno 381, DiffRhythm 381, YuE 347 rows.
- MFDFA: Billboard 381, Suno 381, DiffRhythm 381, YuE 347 rows.
- Billboard annotations: 381 rows.

The YuE result count matches the available YuE full-mix corpus count. Suno has
complete year-position coverage but some title/artist strings differ from
Billboard because punctuation and separators were normalized differently.

## External Audio Layout Observed

The external audio corpus is organized more richly than the README sketch:

- `audio_data/full_only/billboard`: 381 full-mix MP3 files.
- `audio_data/full_only/suno_v4_5`: 381 full-mix MP3 files.
- `audio_data/full_only/diffrhythm`: 381 full-mix MP3 files.
- `audio_data/full_only/YuE`: 347 full-mix MP3 files.
- `audio_data/billboard/vocals/full_duration`: 381 vocal-stem MP3 files.
- `audio_data/suno_v4_5/vocals/batch_1`: 381 vocal-stem MP3 files.
- `audio_data/suno_v4_5/vocals/batch_2`: 381 vocal-stem MP3 files.
- `audio_data/YuE/vocals`: 347 vocal-stem MP3 files.

The corpus appears to contain audio only. No F0 arrays, MIDI files, pitch
contours, or tabular melody results were found in the external data folder.

## Existing Analysis Support

The original public analysis supports amplitude-envelope DFA and MFDFA. The
2026-06-25 extension adds a supported audio-derived F0 audit for Billboard,
Suno v4.5, and YuE vocal stems. It is implemented as a server-side extraction
and fractal pipeline plus local post-analysis over the returned CSV outputs.

This extension uses `librosa.pyin`, not symbolic transcription. More complex
melody extraction models should still be avoided unless the audio-derived audit
fails to answer a specific dissertation need.

## Reproducibility Gaps

1. The local folder is not a Git worktree, so local commit provenance cannot be
   inspected from this copy.
2. The checked-in DFA script defines `AUDIO_ROOTS` but the main loop references
   `input_folders`, so it will not run as written.
3. Batch scripts expect `repo/audio_data/<model>` while the observed audio
   corpus lives externally and has nested `full_only`, `vocals`, and
   `instrumental` subfolders.
4. Scripts write to `results/amplitude_envelope/...`, while checked-in
   reusable CSVs live under `data/results/...`.
5. README describes a simplified audio layout and calls Suno v4.5 the latest
   model. The README now frames Suno v4.5 as a fixed historical model snapshot,
   but older paper-facing wording may still exist in slides or manuscript text.
6. Analysis figures are embedded in notebooks, not exported as manuscript-ready
   figure assets with stable filenames. The F0 extension now exports stable
   post-analysis figures under `results/audio_melody_f0/post_analysis/figures/`;
   the original amplitude-envelope notebook figures still need a manuscript
   export pass if they are used directly.
7. There is no run manifest recording the exact external audio root, stem choice,
   parameters, timestamp, or software environment used to create each result
   table. This is resolved for the F0 extension through server run manifests,
   method parameters, and environment metadata. It remains a gap for older
   amplitude-envelope outputs unless their provenance is documented elsewhere.
8. The public repo excludes prior pitch/MIDI experiments through `.gitignore`
   patterns. The supported F0 pipeline is now isolated under
   `server_handoff/billboard_audio_melody_f0/` and does not depend on the older
   MIDI/pitch experiments.
9. The Obsidian Source Index contains an older local audio-data path; the
   chapter thread supplied the currently observed Google Drive path.

## Narrow Dissertation Extension Plan

This plan has been executed as an audit, not a replacement for the published
paper.
The purpose is to test whether the amplitude-envelope conclusions remain
plausible when viewed against a simple, consistently extracted F0 contour layer.

Recommended scope:

1. Compare only Billboard, Suno v4.5, and YuE.
2. Treat Suno v4.5 as the fixed generated corpus already present in the audio
   data. Do not regenerate Suno audio with newer model versions.
3. Do not compare BiMMuDa symbolic melody annotations directly with
   auto-extracted AI melodies.
4. Use the same audio-derived F0 pipeline for all sources.
5. Start with vocal stems, because they exist for Billboard, Suno v4.5, and YuE
   and are closer to melody than full mixes. Report instrumental or low-voicing
   cases as attrition rather than forcing fragile transcription.
6. Align tracks by `year` and `position`; use title/artist only as labels,
   because punctuation normalization differs across sources.
7. Use complete-case comparisons across Billboard, Suno v4.5, and YuE after
   YuE missing tracks and low-F0-coverage tracks are removed.
8. Compute lightweight F0 audit metrics first:
   - voiced coverage
   - median F0
   - pitch range or interquartile range in semitones
   - contour roughness from first differences
   - DFA alpha on a normalized log-F0 contour only when coverage is sufficient
9. Add MFDFA on F0 only if the DFA/coverage audit is stable and interpretable.
10. Present the result as a limitation-sensitive triangulation: amplitude
    envelope captures energy dynamics, while F0 contour audits melodic/vocal
    phrasing where the audio permits it.

Suggested implementation surface:

- `analysis/f0_contour_batch.py`
- `data/results/f0_contour/manifest.csv`
- `data/results/f0_contour/f0_summary.csv`
- optional `data/results/f0_contour/dfa.csv`
- optional notebook `notebooks/f0_contour_audit.ipynb`

Minimum acceptance criteria:

- All paths are configurable from the external audio root.
- The manifest records source, year, position, file path, duration, voiced
  coverage, inclusion status, and exclusion reason.
- The extraction code never uses BiMMuDa symbolic annotations as a substitute
  for AI melody extraction.
- The chapter text explicitly states that F0 extraction is an audio-derived
  audit and not a perfect melody transcription.
- Any statistical comparison reports the complete-case sample size.
