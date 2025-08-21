# Billboard AI Fractal Comparison

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

This repository contains code and data for performing fractal analysis (DFA and MFDFA) on Billboard music and AI-generated music, as described in the paper:

**"Multifractal Comparison of Billboard and AI-Generated Music"**  
*(Submitted to ACM Multimedia Brave New Ideas 2025)*

## 🎵 [Live Demo: Audio Samples from Analysis Results](https://zhangkkevin.github.io/billboard-ai-fractal-comparison/)

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Data Structure](#data-structure)
- [Analysis Parameters](#analysis-parameters)
- [Results](#results)
- [Citation](#citation)

## 🎯 Overview

This project analyzes the fractal properties of music amplitude envelopes using:

- **Detrended Fluctuation Analysis (DFA)** - Measures long-range correlations in time series
- **Multifractal Detrended Fluctuation Analysis (MFDFA)** - Analyzes scaling behavior across different fluctuation magnitudes

### Analysis Comparison

| Dataset | Description | Time Period |
|---------|-------------|-------------|
| **Billboard Top 5** | Human-created music | 1950-2024 |
| **Suno v4.5** | AI-generated music | - |
| **DiffRhythm** | AI-generated music | - |
| **YuE** | AI-generated music | - |

### Key Findings

- **DFA Analysis**: Identifies songs with α values closest to 1.0 (random walk), minimum α (anti-persistent), and maximum α (persistent)
- **MFDFA Analysis**: Reveals complex scaling behavior through α-width, spectrum skew, and truncation patterns
- **JSD Comparison**: Quantifies similarity between AI-generated and Billboard music patterns

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- FFmpeg (for audio processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/zhangkkevin/billboard-ai-fractal-comparison.git
   cd billboard-ai-fractal-comparison
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Using conda (recommended)
   conda create -n fractal_analysis python=3.10
   conda activate fractal_analysis
   
   # Or using venv
   python -m venv fractal_analysis
   source fractal_analysis/bin/activate  # On Windows: fractal_analysis\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 📊 Usage

### Running Analysis Scripts

#### DFA Analysis
```bash
python analysis/dfa_batch_amplitude_envelope.py
```

#### MFDFA Analysis
```bash
python analysis/mfdfa_batch_amplitude_envelope.py
```

### Jupyter Notebooks

For detailed analysis and visualization:

```bash
jupyter notebook notebooks/
```

- `dfa_music_structure.ipynb` - DFA analysis and visualization
- `mfdfa_music_structure.ipynb` - MFDFA analysis and visualization

## 📁 Data Structure

### Audio Files Organization

```
audio_data/
├── billboard/
│   └── non_separated/
│       └── full_duration/
│           └── YYYY_POSITION_ARTIST_TITLE.mp3
├── suno_v4_5/
│   └── full/
│       └── non_separated/
├── diffrhythm/
└── YuE/
    └── non_separated/
```

### File Naming Convention

Audio files should follow the pattern: `YYYY_POSITION_ARTIST_TITLE.mp3`

**Example**: `2020_01_Taylor Swift_Cardigan.mp3`

### Output Structure

```
results/
├── amplitude_envelope/
│   ├── dfa/
│   │   └── smooth_ms_25_downsample_150_hz/
│   │       ├── billboard_full.csv
│   │       ├── suno_batch_1_full.csv
│   │       ├── diffrhythm_full.csv
│   │       └── yue_full.csv
│   └── mfdfa/
│       ├── billboard_mfdfa_summary.csv
│       ├── suno_batch_1_mfdfa_summary.csv
│       ├── diffrhythm_mfdfa_summary.csv
│       └── yue_mfdfa_summary.csv
```

## ⚙️ Analysis Parameters

### DFA Parameters
| Parameter | Value | Description |
|-----------|-------|-------------|
| Smoothing window | 25ms | Temporal smoothing of amplitude envelope |
| Target sample rate | 150 Hz | Downsampled rate for analysis |
| Original sample rate | 22050 Hz | Input audio sample rate |
| DFA order | 1 | Linear detrending |

### MFDFA Parameters
| Parameter | Value | Description |
|-----------|-------|-------------|
| Smoothing window | 25ms | Temporal smoothing of amplitude envelope |
| Target sample rate | 150 Hz | Downsampled rate for analysis |
| Q-values | -10 to 10 (42 points) | Multifractal moment orders |
| MFDFA order | 2 | Quadratic detrending |
| Lag range | 10 to 3162 | Logarithmically spaced scales |

## 📈 Results

### DFA Output Format

Each CSV contains:
- `year`, `position`, `artist`, `title` - Song metadata
- `alpha` - DFA scaling exponent
- `intercept` - Linear fit intercept
- `r_squared` - Goodness of fit
- `log_n`, `log_fn` - DFA fluctuation data (JSON format)

### MFDFA Output Format

Each CSV contains:
- `year`, `position`, `artist`, `title` - Song metadata
- `alpha_width` - Width of multifractal spectrum
- `alpha_peak` - Peak of multifractal spectrum
- `spectrum_skew` - Asymmetry of spectrum
- `truncation` - Spectrum truncation type
- `alpha`, `f_alpha`, `H_q` - Full spectra (JSON format)

### Key Metrics Explained

- **α (Alpha)**: Scaling exponent indicating persistence (α > 1) or anti-persistence (α < 1)
- **α-width**: Range of scaling exponents, indicating multifractal complexity
- **Spectrum Skew**: Asymmetry of the multifractal spectrum
- **Truncation**: Indicates leveling of scaling behavior at extreme q-values

## 🔗 Data Access

### Audio Files
Due to copyright restrictions, Billboard audio files are not included. AI-generated audio samples are available on Zenodo (link to be added).

### Reference Data
Pre-computed results are available in `reference_data/` for:
- DFA results: Alpha values, intercepts, and fit statistics
- MFDFA results: Alpha width, alpha peak, spectrum skew, and H(q) values

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Audio processing libraries: `pydub`, `librosa`
- Fractal analysis: `nolds`, `MFDFA`
- Scientific computing: `numpy`, `scipy`, `pandas`
- Visualization: `matplotlib`, `seaborn`

