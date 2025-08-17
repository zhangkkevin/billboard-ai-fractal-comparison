import os
import json
import numpy as np
import pandas as pd
from pydub import AudioSegment
from scipy import signal
from tqdm import tqdm
import nolds
from scipy.stats import linregress
from scipy.signal import resample
from multiprocessing import Pool, cpu_count
from pathlib import Path

# === CONFIGURABLE ===
smoothing_windows_ms = [25]
target_sr = 150
orig_sr = 22050

# Make output directory repo-relative
REPO_ROOT = Path(__file__).resolve().parents[1]
base_output_dir = str(REPO_ROOT / "results" / "amplitude_envelope" / "dfa")

# Repo-relative input folders
AUDIO_ROOTS = {
    # "billboard": str(REPO_ROOT / "audio_data" / "billboard" / "non_separated" / "full_duration"),
    "diffrhythm": str(REPO_ROOT / "audio_data" / "diffrhythm"),
    "suno_batch_1": str(REPO_ROOT / "audio_data" / "suno_v4_5" / "full" / "non_separated"),
    "yue": str(REPO_ROOT / "audio_data" / "YuE" / "non_separated"),
}

# === FUNCTION DEFINITIONS ===
def parse_filename(filename):
    base = os.path.splitext(filename)[0]
    parts = base.split('_', 3)
    if len(parts) < 4:
        return None
    year = int(parts[0])
    position = parts[1]
    artist = parts[2]
    title = parts[3].replace(".mp3", "")
    return {
        "year": year,
        "position": position,
        "artist": artist,
        "title": title
    }

def compute_amplitude_envelope(filepath, target_sr=150, orig_sr=22050, smooth_ms=50):
    # Load MP3 audio and set original sample rate (e.g., 22050 Hz)
    audio = AudioSegment.from_mp3(filepath).set_channels(1).set_frame_rate(orig_sr)
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    samples /= np.iinfo(audio.array_type).max  # Normalize to [-1, 1]

    # Compute amplitude envelope using Hilbert transform
    analytic_signal = signal.hilbert(samples)
    envelope = np.abs(analytic_signal)

    # Apply smoothing BEFORE downsampling
    smooth_samples = int((smooth_ms / 1000) * orig_sr)
    if smooth_samples > 1:
        kernel = np.ones(smooth_samples) / smooth_samples
        envelope = np.convolve(envelope, kernel, mode='same')

    # Downsample the smoothed envelope to target_sr
    n_samples = int(len(envelope) * (target_sr / orig_sr))
    envelope = resample(envelope, n_samples)

    return envelope

def compute_dfa_nolds(signal, nvals=None, overlap=True, order=1, fit_trend='poly', fit_exp='poly'):
    # Run DFA with debugging enabled to access log(n), log(F(n)), and fit coefficients
    alpha, (log_n, log_fn, poly) = nolds.dfa(
        signal,
        nvals=nvals,
        overlap=overlap,
        order=order,
        fit_trend=fit_trend,
        fit_exp=fit_exp,
        debug_data=True
    )

    # Use the exact log-log points nolds used for fitting
    slope, intercept = poly
    r_squared = linregress(log_n, log_fn).rvalue ** 2

    return {
        "alpha": alpha,
        "log_n": json.dumps(log_n.tolist()),      # Save as clean JSON
        "log_fn": json.dumps(log_fn.tolist()),
        "intercept": intercept,
        "r_squared": r_squared
    }

def process_file(args):
    filepath, target_sr, orig_sr, smooth_ms = args
    try:
        meta = parse_filename(os.path.basename(filepath))
        if not meta:
            return None

        amp_env = compute_amplitude_envelope(filepath, target_sr=target_sr, orig_sr=orig_sr, smooth_ms=smooth_ms)
        dfa_data = compute_dfa_nolds(amp_env)

        return {
            **meta,
            "signal_length": len(amp_env),
            "alpha": dfa_data["alpha"],
            "intercept": dfa_data["intercept"],
            "r_squared": dfa_data["r_squared"],
            "log_n": dfa_data["log_n"],
            "log_fn": dfa_data["log_fn"],
        }
    except Exception as e:
        return {"filename": os.path.basename(filepath), "status": f"error: {str(e)}"}

def run_dfa_batch(input_folder, output_csv, target_sr, orig_sr, smooth_ms):
    files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".mp3")]
    print(f"🎵 Processing {len(files)} files using {cpu_count()} CPU cores...")

    results = []
    with Pool(processes=cpu_count()) as pool:
        file_args = [(f, target_sr, orig_sr, smooth_ms) for f in files]
        for result in tqdm(pool.imap_unordered(process_file, file_args), total=len(files)):
            if result:
                results.append(result)

    df = pd.DataFrame(results)
    df = df.sort_values(by=["year", "position"])
    df.to_csv(output_csv, index=False)
    print(f"✅ Saved results to {output_csv}")

# === MAIN LOOP ===
if __name__ == "__main__":
    for smooth_ms in smoothing_windows_ms:
        output_dir = os.path.join(base_output_dir, f"smooth_ms_{smooth_ms}_downsample_{target_sr}_hz")
        os.makedirs(output_dir, exist_ok=True)
        
        for model, input_dir in input_folders.items():
            # if model == "billboard":
            #     continue
            output_csv = os.path.join(output_dir, f"{model}_full.csv")
            run_dfa_batch(input_dir, output_csv, target_sr, orig_sr, smooth_ms)