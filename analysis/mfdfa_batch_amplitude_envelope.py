import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from scipy.signal import hilbert, resample
from scipy.ndimage import uniform_filter1d
from pydub import AudioSegment
from MFDFA import MFDFA
import json
from pathlib import Path

# === CONFIG ===
REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIO_ROOTS = {
    "billboard": str(REPO_ROOT / "audio_data" / "billboard" / "non_separated" / "full_duration"),
    "diffrhythm": str(REPO_ROOT / "audio_data" / "diffrhythm"),
    "suno_batch_1": str(REPO_ROOT / "audio_data" / "suno_v4_5" / "full" / "non_separated"),
    "yue": str(REPO_ROOT / "audio_data" / "YuE" / "non_separated"),
}
OUTPUT_DIR = REPO_ROOT / "results" / "amplitude_envelope" / "mfdfa"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

QVALS = np.linspace(-10, 10, 42) #includes 0


def compute_smoothed_envelope_resampled(
    filepath,
    original_sr=22050,
    target_sr=150,
    smooth_ms=25
):
    audio = AudioSegment.from_mp3(filepath).set_channels(1).set_frame_rate(original_sr)
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    samples /= np.iinfo(audio.array_type).max

    analytic = hilbert(samples)
    envelope = np.abs(analytic)

    smooth_len = int((smooth_ms / 1000) * original_sr)
    envelope_smooth = uniform_filter1d(envelope, size=smooth_len)

    num_samples = int(len(envelope_smooth) * (target_sr / original_sr))
    envelope_ds = resample(envelope_smooth, num_samples)

    return envelope_ds


def compute_mfdfa_summary(filepath, model):
    try:
        filename = os.path.basename(filepath)
        year = filename.split("_")[0]
        position = filename.split("_")[1]
        artist = filename.split("_")[2]
        title = filename.split("_")[3].replace(".mp3", "")

        env = compute_smoothed_envelope_resampled(filepath)

        lag = np.unique(np.logspace(0.5, 3, 50).astype(int))
        order = 2

        lag_used, Fq = MFDFA(env, lag=lag, q=QVALS, order=order)

        log_lag = np.log(lag_used)
        
        epsilon = 1e-10
        H_q = np.array([
            np.polyfit(log_lag, np.log(Fq[:, i] + epsilon), 1)[0]
            for i in range(len(QVALS))
        ])

        dq = QVALS[1] - QVALS[0]
        tq = H_q * QVALS - 1
        hq = np.gradient(tq, dq)
        Dq = QVALS * hq - tq

        alpha_width = np.max(hq) - np.min(hq)
        alpha_peak = hq[np.argmax(Dq)]
        skew = (np.max(hq) + np.min(hq) - 2 * alpha_peak) / alpha_width if alpha_width > 0 else 0
        truncation = "left" if skew > 0.05 else "right" if skew < -0.05 else "none"

        sorted_indices = np.argsort(hq)
        hq_sorted = np.array(hq)[sorted_indices]
        Dq_sorted = np.array(Dq)[sorted_indices]

        return {
            "year": year,
            "position": position,
            "artist": artist,
            "title": title,
            "alpha": json.dumps(hq_sorted.tolist()),
            "f_alpha": json.dumps(Dq_sorted.tolist()),
            "alpha_width": alpha_width,
            "alpha_peak": alpha_peak,
            "spectrum_skew": skew,
            "truncation": truncation,
            "H_q": json.dumps(H_q.tolist()),
        }
    except Exception:
        return None


# === BATCH FUNCTION ===
def _worker(args):
    return compute_mfdfa_summary(*args)


def process_model(model, path):
    print(f"🎧 Processing model: {model}")
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".mp3")]
    tasks = [(f, model) for f in files]

    with Pool(cpu_count()) as pool:
        results = list(tqdm(pool.imap_unordered(_worker, tasks), total=len(tasks)))

    df = pd.DataFrame([r for r in results if r])
    df = df.sort_values(by=["year", "position"])
    out_path = OUTPUT_DIR / f"{model}_mfdfa_summary.csv"
    df.to_csv(out_path, index=False)
    print(f"✅ Saved {len(df)} results to {out_path}")


# === RUN ALL MODELS ===
if __name__ == "__main__":
    for model, path in AUDIO_ROOTS.items():
        process_model(model, path)