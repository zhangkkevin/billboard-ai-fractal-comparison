# Billboard AI Fractal Comparison

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)](https://jupyter.org/)

This repository contains code and data for performing fractal analysis (DFA and MFDFA) on Billboard music and AI-generated music, as described in the paper:

**"Multifractal Comparison of Billboard and AI-Generated Music"**  
*(Accepted to ACM Multimedia Brave New Ideas 2025)*

📄 **[Read the Paper](https://doi.org/placeholder-link)**

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
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This project analyzes the fractal properties of music amplitude envelopes using advanced time series analysis techniques:

- **Detrended Fluctuation Analysis (DFA)** - Measures long-range correlations in music amplitude envelopes
- **Multifractal Detrended Fluctuation Analysis (MFDFA)** - Analyzes complex scaling behavior across different fluctuation magnitudes

### Analysis Comparison

The analysis compares:
- **Billboard Top 5 songs** (1950-2024) - Human-created music
- **AI-generated music** from multiple models:
  - **Suno v4.5** - Latest AI music generation model
  - **DiffRhythm** - Diffusion-based music generation
  - **YuE** - Neural music synthesis model

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

### Configuration

Before running analysis, configure your audio data paths in the analysis scripts:

```python
AUDIO_ROOTS = {
    "billboard": "path/to/audio_data/billboard/audio_files",
    "suno_v4_5": "path/to/audio_data/suno_v4_5/audio_files", 
    "diffrhythm": "path/to/audio_data/diffrhythm/audio_files",
    "yue": "path/to/audio_data/yue/audio_files"
}
```

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

## 📊 Results

### Output Directories

Analysis scripts create timestamped output directories:

- **DFA**: `results/amplitude_envelope/dfa/smooth_ms_25_downsample_150_hz_YYYYMMDD_HHMMSS/`
- **MFDFA**: `results/amplitude_envelope/mfdfa/smooth_ms_25_downsample_150_hz_q-10_10_42_YYYYMMDD_HHMMSS/`

### DFA Results Format

Each CSV contains:
- `year`, `position`, `artist`, `title` - Song metadata
- `alpha` - DFA scaling exponent
- `intercept` - Linear fit intercept
- `r_squared` - Goodness of fit
- `log_n`, `log_fn` - DFA fluctuation data (JSON format)

### MFDFA Results Format

Each CSV contains:
- `year`, `position`, `artist`, `title` - Song metadata
- `alpha_width` - Width of multifractal spectrum
- `alpha_peak` - Peak of multifractal spectrum
- `spectrum_skew` - Asymmetry of spectrum
- `truncation` - Spectrum truncation type
- `alpha`, `f_alpha`, `H_q` - Full spectra (JSON format)

### Reference Data

Pre-computed results are available in `reference_data/` for:
- **DFA results**: Alpha values, intercepts, and fit statistics
- **MFDFA results**: Alpha width, alpha peak, spectrum skew, and H(q) values

## 🎵 Web Interface

The project includes a web interface for exploring results:

- **Main site**: [https://zhangkkevin.github.io/billboard-ai-fractal-comparison/](https://zhangkkevin.github.io/billboard-ai-fractal-comparison/)
- **Local development**: Serve `docs/` directory with any web server

### Features
- Interactive audio samples from analysis results
- Spotify embeds for Billboard songs
- Local audio files for AI-generated music
- Detailed analysis visualizations
- Responsive design for all devices

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

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Audio Processing**: FFmpeg, librosa, pydub
- **Fractal Analysis**: nolds, MFDFA
- **Data Analysis**: pandas, scipy, numpy
- **Visualization**: matplotlib, seaborn
- **Web Interface**: HTML5, CSS3, JavaScript

## 📞 Contact

- **Author**: Kevin Kailun Zhang
- **Email**: [Your email]
- **GitHub**: [@zhangkkevin](https://github.com/zhangkkevin)

---

**Note**: This research is part of ongoing work on understanding the fractal properties of music and comparing human-created vs AI-generated compositions.

