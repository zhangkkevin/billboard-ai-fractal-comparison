<p align="center">
    <h1>Multifractal Comparison of Billboard and AI-Generated Music</h1>
</p>

<p align="center">
    <img src="./assets/images/acm.png" width="400" alt="ACM Logo"/>
</p>

<p align="center">
    <a href="https://dl.acm.org/doi/10.1145/3746027.3758168">📑 Paper</a> &nbsp;|&nbsp; 🎵 <a href="https://zhangkkevin.github.io/billboard-ai-fractal-comparison/">Listening Samples</a> &nbsp;|&nbsp; 📊 <a href="https://zenodo.org/placeholder">Dataset (coming soon)</a>
</p>

This repository contains code and data for performing fractal analysis (DFA and MFDFA) on Billboard music and AI-generated music, specifically,
- **Billboard Top 5 songs** (1950-2024) - Human-created music
- **AI-generated music** from multiple models:
  - **[Suno v4.5](https://suno.com/)** - Fixed historical model snapshot used for this study
  - **[DiffRhythm](https://github.com/ASLP-lab/DiffRhythm)** - Diffusion-based music generation
  - **[YuE](https://github.com/multimodal-art-projection/YuE)** - Neural music synthesis model

Pre-computed results are available in `data/results` for:
- **DFA results**: Alpha values, intercepts, and fit statistics
- **MFDFA results**: Alpha width, alpha peak, spectrum skew, and H(q) values
- **Audio-melody F0 audit summaries**: Vocal-stem F0 quality and fractal descriptors for Billboard, Suno v4.5, and YuE

Due to copyright restrictions, Billboard audio files are **NOT** included in the dataset.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Conda or pip package manager
- FFmpeg (for audio processing)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/zhangkkevin/billboard-ai-fractal-comparison.git
   cd billboard-ai-fractal-comparison
   ```

2. **Create and activate conda environment**
   ```bash
   conda create -n fractal_analysis python=3.10
   conda activate fractal_analysis
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🔬 Analysis Scripts and Notebooks

### Analysis Scripts
- **`analysis/dfa_batch_amplitude_envelope.py`** - Detrended Fluctuation Analysis on amplitude envelopes
- **`analysis/mfdfa_batch_amplitude_envelope.py`** - Multifractal Detrended Fluctuation Analysis on amplitude envelopes

### Jupyter Notebooks
- **`notebooks/dfa_music_structure.ipynb`** - DFA analysis and visualization
- **`notebooks/mfdfa_music_structure.ipynb`** - MFDFA analysis and visualization

### Usage
```bash
# Run DFA analysis
python analysis/dfa_batch_amplitude_envelope.py

# Run MFDFA analysis  
python analysis/mfdfa_batch_amplitude_envelope.py
```

**Note**: Server versions of scripts and notebooks (with `_server` suffix) contain copyrighted content and are excluded from this repository.

## Audio-Melody F0 Dissertation Extension

The dissertation extension adds an audio-derived melody-contour audit for
Billboard, Suno v4.5, and YuE vocal stems. It uses the same F0 extraction and
fractal settings across all three sources and does not compare BiMMuDa symbolic
melody annotations against auto-extracted AI melodies.

Server-side reproducibility files live in `server_handoff/billboard_audio_melody_f0/`.
The checked-in server outputs under `results/audio_melody_f0/` are enough to
recreate local dissertation tables and figures:

```bash
python analysis/audio_melody_f0_post_analysis.py --results-root results/audio_melody_f0
```

Main local outputs:
- `results/audio_melody_f0/post_analysis/post_analysis_summary.md`
- `results/audio_melody_f0/post_analysis/tables/`
- `results/audio_melody_f0/post_analysis/figures/`
- `docs/audio_melody_f0_reproducibility.md`
- `docs/audio_melody_f0_dissertation_extension.md`

The full Stage 1 F0 extraction requires the private vocal-stem audio corpus and
is intended to run on the server. The repository keeps the runbook, environment
metadata, redacted annotations, manifests, summary CSVs, and QA figures, while
excluding audio files and `.npz` contour caches.
   
## 📁 Data Structure

### Required Directory Structure for Batch Analysis

```
audio_data/
├── billboard/
│   └── audio_files/
├── suno_v4_5/
│   └── audio_files/
├── diffrhythm/
│   └── audio_files/
└── yue/
    └── audio_files/
```

### File Naming Convention

Audio files should follow this naming pattern:
```
YYYY_POSITION_ARTIST_TITLE.mp3
```

Examples:
- `2020_01_Taylor Swift_Cardigan.mp3`
- `1958_02_Elvis Presley_All Shook Up.mp3`

## 📚 Citation

If you use this code in your research, please cite:

```bibtex
@inproceedings{zhang2025multifractal,
  title={Multifractal Comparison of Billboard and AI-Generated Music},
  author={Zhang, Kevin Kailun and Sun, Ying and Xiong, Hui},
  booktitle={Proceedings of the 33rd ACM International Conference on Multimedia (MM '25)},
  pages={1--10},
  year={2025},
  organization={ACM},
  doi={10.1145/3746027.3758168},
  isbn={979-8-4007-2035-2/2025/10}
}
```

## 📞 Contact
If you are interested in this work and want to message us, feel free to leave a email to `kkzhang825@connect.hkust-gz.edu.cn`.
