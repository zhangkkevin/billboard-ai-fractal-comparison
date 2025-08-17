# Billboard AI Fractal Comparison

This repository contains code and data for performing fractal analysis (DFA and MFDFA) on Billboard music and AI-generated music, as described in the paper:

**"Multifractal Comparison of Billboard and AI-Generated Music"**  
*(submitted to ACM Multimedia Brave New Ideas 2025)*

## Overview

This project analyzes the fractal properties of music amplitude envelopes using:
- **Detrended Fluctuation Analysis (DFA)** - Measures long-range correlations
- **Multifractal Detrended Fluctuation Analysis (MFDFA)** - Analyzes scaling behavior across different fluctuation magnitudes

The analysis compares:
- **Billboard Top 5 songs** (1950-2024) - Human-created music
- **AI-generated music** from Suno, DiffRhythm, and YuE models

## Repository Structure

```
billboard-ai-fractal-comparison/
├── analysis/                          # Core analysis scripts
│   ├── dfa_batch_amplitude_envelope_clean.py
│   └── mfdfa_batch_amplitude_envelope_clean.py
├── reference_data/                    # Pre-computed results for reproducibility
│   ├── dfa/                          # DFA results
│   │   ├── billboard.csv
│   │   ├── suno.csv
│   │   ├── diffrhythm.csv
│   │   └── yue.csv
│   └── mfdfa/                        # MFDFA results
│       ├── billboard.csv
│       ├── suno.csv
│       ├── diffrhythm.csv
│       └── yue.csv
└── README.md
```

## Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone https://github.com/zhangkkevin/billboard-ai-fractal-comparison.git
cd billboard-ai-fractal-comparison

# Install required packages
pip install numpy pandas scipy matplotlib seaborn nolds MFDFA tqdm pydub
```

### 2. Run Analysis

#### DFA Analysis
```bash
python analysis/dfa_batch_amplitude_envelope_clean.py
```

#### MFDFA Analysis
```bash
python analysis/mfdfa_batch_amplitude_envelope_clean.py
```

### 3. Access Results

The analysis scripts will create timestamped output directories:
- DFA: `results/amplitude_envelope/dfa/smooth_ms_25_downsample_150_hz_YYYYMMDD_HHMMSS/`
- MFDFA: `results/amplitude_envelope/mfdfa/smooth_ms_25_downsample_150_hz_q-10_10_42_YYYYMMDD_HHMMSS/`

## Data Access

### Audio Files
Due to copyright restrictions, audio files are not included in this repository. To run the analysis on your own audio data:

1. **Organize your audio files** in the following structure:
   ```
   audio_data/
   ├── billboard/
   ├── suno/
   ├── diffrhythm/
   └── yue/
   ```

2. **Update paths** in the analysis scripts to point to your audio data directory

3. **File naming convention**: `YYYY_POSITION_ARTIST_TITLE.mp3`
   - Example: `2020_01_Taylor Swift_Cardigan.mp3`

### Reference Data
Pre-computed results are available in `reference_data/` for:
- **DFA results**: Alpha values, intercepts, and fit statistics
- **MFDFA results**: Alpha width, alpha peak, spectrum skew, and H(q) values

## Analysis Parameters

### DFA Parameters
- **Smoothing window**: 25ms
- **Target sample rate**: 150 Hz
- **Original sample rate**: 22050 Hz
- **DFA order**: 1 (linear detrending)

### MFDFA Parameters
- **Smoothing window**: 25ms
- **Target sample rate**: 150 Hz
- **Q-values**: -10 to 10 (42 points)
- **MFDFA order**: 2 (quadratic detrending)
- **Lag range**: 10 to 3162 (logarithmically spaced)

## Output Format

### DFA Results
Each CSV contains:
- `year`, `position`, `artist`, `title` - Song metadata
- `alpha` - DFA scaling exponent
- `intercept` - Linear fit intercept
- `r_squared` - Goodness of fit
- `log_n`, `log_fn` - DFA fluctuation data (JSON format)

### MFDFA Results
Each CSV contains:
- `year`, `position`, `artist`, `title` - Song metadata
- `alpha_width` - Width of multifractal spectrum
- `alpha_peak` - Peak of multifractal spectrum
- `spectrum_skew` - Asymmetry of spectrum
- `truncation` - Spectrum truncation type
- `alpha`, `f_alpha`, `H_q` - Full spectra (JSON format)

## Key Findings

### DFA Results
- **Billboard α evolution**: Declining trend from 1950s to 2000s, modest resurgence in 2010s
- **AI comparison**: YuE shows highest deviation from Billboard patterns
- **Decade analysis**: Systematic differences between human and AI-generated music

### MFDFA Results
- **Spectrum characteristics**: AI models show different multifractal properties
- **Complexity measures**: Alpha width and skew reveal structural differences
- **Model comparison**: Each AI model has distinct fractal signatures

## Citation

```bibtex
@article{zhang2025multifractal,
  title={Multifractal Comparison of Billboard and AI-Generated Music},
  author={Zhang, Kevin},
  journal={ACM Multimedia Brave New Ideas},
  year={2025},
  note={Submitted}
}
```

## Requirements

- Python 3.8+
- numpy
- pandas
- scipy
- matplotlib
- seaborn
- nolds
- MFDFA
- tqdm
- pydub

## License

This code is provided for research purposes. The BiMMuDa dataset MIDI files are included with appropriate permissions.

## Contact

For questions about this research, please refer to the author contact listed in the final version of the paper.

---

**Note**: This repository is currently under anonymous review. All content will be made publicly available upon acceptance and publication of the paper.
