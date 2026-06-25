from __future__ import annotations

from typing import Any, Dict, Tuple

import librosa
import numpy as np


def extract_f0(audio_path: str, f0_cfg: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    sr = int(f0_cfg["sr"])
    frame_length = int(f0_cfg["frame_length"])
    hop_length = int(f0_cfg["hop_length"])
    fmin = float(f0_cfg["fmin_hz"])
    fmax = float(f0_cfg["fmax_hz"])

    y, sr_loaded = librosa.load(audio_path, sr=sr, mono=True)
    if y.size == 0:
        raise ValueError("empty_audio")

    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        sr=sr_loaded,
        fmin=fmin,
        fmax=fmax,
        frame_length=frame_length,
        hop_length=hop_length,
    )

    meta = {
        "sr": sr_loaded,
        "hop_length": hop_length,
        "frame_length": frame_length,
        "audio_path": audio_path,
        "duration_sec": float(len(y) / sr_loaded),
    }
    return f0, voiced_flag, voiced_probs, meta
