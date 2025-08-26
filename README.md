# Multifractal Comparison of Billboard and AI-Generated Music

<p align="center">
    <a href="https://doi.org/placeholder-link">📑 Paper</a> &nbsp;|&nbsp; 🎵 <a href="https://zhangkkevin.github.io/billboard-ai-fractal-comparison/">Demo</a>
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)](https://jupyter.org/)

This repository contains code and data for performing fractal analysis (DFA and MFDFA) on Billboard music and AI-generated music.

This project analyzes the fractal properties of music amplitude envelopes using advanced time series analysis techniques:
- **Detrended Fluctuation Analysis (DFA)** - Measures long-range correlations in music amplitude envelopes
- **Multifractal Detrended Fluctuation Analysis (MFDFA)** - Analyzes complex scaling behavior across different fluctuation magnitudes

The analysis compares:
- **Billboard Top 5 songs** (1950-2024) - Human-created music
- **AI-generated music** from multiple models:
  - **[Suno v4.5](https://suno.com/)** - Latest AI music generation model
  - **[DiffRhythm](https://github.com/ASLP-lab/DiffRhythm)** - Diffusion-based music generation
  - **[YuE](https://github.com/multimodal-art-projection/YuE)** - Neural music synthesis model

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Conda or pip package manager
- FFmpeg (for audio processing)

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

## 📦 Installation

### Option 1: Using requirements.txt (Recommended)

```bash
pip install -r requirements.txt
```

### Option 2: Manual installation

```bash
pip install numpy pandas scipy matplotlib seaborn nolds MFDFA tqdm pydub scikit-learn librosa tinytag
```

### System Dependencies

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

## 🔧 Usage

### Running Analysis Scripts

#### 1. DFA Analysis
```bash
python analysis/dfa_batch_amplitude_envelope_clean.py
```

#### 2. MFDFA Analysis
```bash
python analysis/mfdfa_batch_amplitude_envelope_clean.py
```

### Jupyter Notebooks

For interactive analysis and visualization:

```bash
jupyter lab
# or
jupyter notebook
```

Available notebooks:
- `notebooks/dfa_music_structure.ipynb` - DFA analysis and visualization
- `notebooks/mfdfa_music_structure.ipynb` - MFDFA analysis and visualization

## 📁 Data Structure

### Required Directory Structure

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

### Data Access

Due to copyright restrictions, Billboard audio files are not included in this repository. AI-generated audio samples are available on Zenodo: [Link to be added]

## ⚙️ Analysis Parameters

### DFA Parameters
- **Smoothing window**: 25ms
- **Target sample rate**: 150 Hz
- **Original sample rate**: 22050 Hz
- **DFA order**: 1 (linear detrending)
- **Overlap**: True
- **Fit trend**: Polynomial

### MFDFA Parameters
- **Smoothing window**: 25ms
- **Target sample rate**: 150 Hz
- **Q-values**: -10 to 10 (42 points)
- **MFDFA order**: 2 (quadratic detrending)
- **Lag range**: 10 to 3162 (logarithmically spaced)
- **Spectrum calculation**: Legendre transform

### Reference Data

Pre-computed results are available in `reference_data/` for:
- **DFA results**: Alpha values, intercepts, and fit statistics
- **MFDFA results**: Alpha width, alpha peak, spectrum skew, and H(q) values

## 📚 Citation

If you use this code in your research, please cite:

```bibtex
@article{zhang2025multifractal,
  title={Multifractal Comparison of Billboard and AI-Generated Music},
  author={Zhang, Kevin Kailun},
  journal={ACM Multimedia Brave New Ideas},
  year={2025},
  note={Submitted}
}
```

## 📞 Contact

- **Author**: Kevin Kailun Zhang
- **Email**: kkzhang825@connect.hkust-gz.edu.cn

---

**Note**: This research is part of ongoing work on understanding the fractal properties of music and comparing human-created vs AI-generated compositions.