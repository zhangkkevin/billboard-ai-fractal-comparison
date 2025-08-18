# Billboard AI Fractal Comparison

This repository contains code and data for performing fractal analysis (DFA and MFDFA) on Billboard music and AI-generated music, as described in the paper:

**"Multifractal Comparison of Billboard and AI-Generated Music"**  
*(submitted to ACM Multimedia Brave New Ideas 2025)*

## 🌐 Interactive Website

**🎵 [Explore the Analysis Results Online](https://zhangkkevin.github.io/billboard-ai-fractal-comparison/)**

Our interactive website showcases the fractal analysis results with:
- **Audio samples** from the analysis (YouTube embeds for Billboard, local files for AI-generated)
- **Interactive audio players** for all 34 songs from the study
- **Real-time audio playback** to hear the fractal differences

### Website Features
- **DFA Analysis**: Songs closest to α=1.0, minimum α, and maximum α values
- **MFDFA Analysis**: Maximum/minimum width and skew spectrum examples
- **JSD Comparison**: Best and worst Jensen-Shannon divergence scores
- **Copyright-compliant**: YouTube embeds for original music, local files for AI-generated

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
├── docs/                             # Interactive website
│   ├── index.html                    # Main website
│   ├── script.js                     # Website functionality
│   ├── styles.css                    # Website styling
│   ├── audio/                        # AI-generated audio files
│   ├── upload.html                   # Audio upload interface
│   └── audio_metadata.json           # Audio file metadata
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

### 2. Run the Interactive Website

**🌐 Public Website**: [https://zhangkkevin.github.io/billboard-ai-fractal-comparison/](https://zhangkkevin.github.io/billboard-ai-fractal-comparison/)

**Local Development**:
```bash
# Navigate to the docs directory
cd docs

# Start the local web server
python -m http.server 8000

# Open your browser and go to:
# http://localhost:8000/
```

The website will display:
- **34 songs** from your fractal analysis results
- **YouTube embeds** for Billboard songs (copyright-compliant)
- **Audio players** for AI-generated music
- **Interactive interface** to explore the results

### 3. Run Analysis

#### DFA Analysis
```bash
python analysis/dfa_batch_amplitude_envelope_clean.py
```

#### MFDFA Analysis
```bash
python analysis/mfdfa_batch_amplitude_envelope_clean.py
```

### 4. Access Results

The analysis scripts will create timestamped output directories:
- DFA: `results/amplitude_envelope/dfa/smooth_ms_25_downsample_150_hz_YYYYMMDD_HHMMSS/`
- MFDFA: `results/amplitude_envelope/mfdfa/smooth_ms_25_downsample_150_hz_q-10_10_42_YYYYMMDD_HHMMSS/`

## Website Features

### Audio Management
The website includes a comprehensive audio management system:

- **Upload Interface**: `http://localhost:8000/upload.html` - Manage audio files
- **Automatic Metadata**: Generates metadata for all uploaded audio files
- **File Organization**: Organizes files by model and analysis category
- **Copyright Compliance**: YouTube embeds for original music, local files for AI-generated

### Audio File Structure
The website expects audio files organized as:
```
audio_data/
├── billboard/                    # Original Billboard songs (YouTube embeds)
├── suno_v4_5/                   # Suno AI-generated music
│   └── non_separated/
├── diffrhythm/                  # DiffRhythm AI-generated music
│   └── non_separated/
└── YuE/                         # YuE AI-generated music
    └── non_separated/
```

## Data Access

### Audio Files
Due to copyright restrictions, original audio files are not included in this repository. The website uses:

1. **YouTube embeds** for Billboard songs (copyright-compliant)
2. **Local audio files** for AI-generated music (included in `docs/audio/`)

To run the analysis on your own audio data:

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

## Analysis Results Showcased on Website

The interactive website displays 34 carefully selected songs representing extreme cases from the fractal analysis:

### DFA Analysis (12 songs)
- **Closest to α=1.0**: Songs with scaling exponents closest to ideal fractal behavior
- **Minimum α**: Songs with the lowest long-range correlations
- **Maximum α**: Songs with the highest long-range correlations

### MFDFA Analysis (16 songs)
- **Maximum Width**: Songs with the broadest multifractal spectra
- **Minimum Width**: Songs with the narrowest multifractal spectra
- **Maximum Skew**: Songs with the most asymmetric spectra
- **Minimum Skew**: Songs with the most symmetric spectra

### JSD Comparison (6 songs)
- **Best JSD**: Songs with the lowest Jensen-Shannon divergence scores
- **Worst JSD**: Songs with the highest Jensen-Shannon divergence scores

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

## Website Development

The interactive website was built with:
- **HTML5/CSS3/JavaScript** - Modern web technologies
- **Responsive Design** - Works on desktop and mobile devices
- **Audio Integration** - YouTube embeds and local audio players
- **Metadata Management** - Automatic file organization and metadata generation

### Website Files
- `docs/index.html` - Main website interface
- `docs/script.js` - Interactive functionality and audio management
- `docs/styles.css` - Modern, responsive styling
- `docs/upload.html` - Audio file upload interface
- `docs/audio/` - AI-generated audio files
- `docs/audio_metadata.json` - Audio file metadata

## Contributing

We welcome contributions to improve the website and analysis:

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Test the website locally**
5. **Submit a pull request**

## License

This code is provided for research purposes. The BiMMuDa dataset MIDI files are included with appropriate permissions.

## Contact

For questions about this research, please refer to the author contact listed in the final version of the paper.

---

**Note**: This repository is currently under anonymous review. All content will be made publicly available upon acceptance and publication of the paper.
