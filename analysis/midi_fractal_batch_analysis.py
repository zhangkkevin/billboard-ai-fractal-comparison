import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import mido
import nolds
from MFDFA import MFDFA
import json

# === CONFIG ===
MIDI_ROOT = "/home/data/kevinzhang/research/fractal_analysis/BiMMuDa-main/bimmuda_dataset"
METADATA_CSV = "/home/data/kevinzhang/research/fractal_analysis/BiMMuDa-main/metadata/bimmuda_per_song_metadata.csv"
DFA_OUT_NOTES = "/home/data/kevinzhang/research/fractal_analysis/results/midi/dfa_midi_notes.csv"
MFDFA_OUT_NOTES = "/home/data/kevinzhang/research/fractal_analysis/results/midi/mfdfa_midi_notes.csv"

QVALS = np.linspace(-5, 5, 21)

# === LOAD METADATA ===
meta_df = pd.read_csv(METADATA_CSV)
meta_df['Position'] = meta_df['Position'].astype(str)
meta_lookup = {}
for _, row in meta_df.iterrows():
    key = (str(row['Year']), str(row['Position']))
    meta_lookup[key] = {
        'artist': row['Artist'],
        'title': row['Title'],
        'year': row['Year'],
        'position': row['Position']
    }

def midi_to_timeseries(midi_path):
    mid = mido.MidiFile(midi_path)
    # Collect all note-on and note-off events with absolute tick times
    events = []
    abs_time = 0
    for track in mid.tracks:
        abs_time = 0
        note_on_dict = {}
        for msg in track:
            abs_time += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                note_on_dict[msg.note] = abs_time
            elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in note_on_dict:
                    start = note_on_dict[msg.note]
                    duration = abs_time - start
                    events.append((start, abs_time, msg.note, duration))
                    del note_on_dict[msg.note]
    # Sort by start time
    events.sort()
    # Find shortest nonzero duration
    durations = [e[3] for e in events if e[3] > 0]
    if not durations:
        return np.array([])
    min_dur = min(durations)
    # Expand each note according to its duration in ticks
    expanded = []
    for start, end, note, duration in events:
        n_repeats = int(round(duration / min_dur))
        expanded.extend([note] * n_repeats)
    return np.array(expanded)

def compute_dfa_nolds(signal):
    alpha, (log_n, log_fn, poly) = nolds.dfa(
        signal,
        debug_data=True
    )
    intercept = poly[1]
    return {
        'alpha': alpha,
        'intercept': intercept,
        'log_n': json.dumps(log_n.tolist()),
        'log_fn': json.dumps(log_fn.tolist())
    }

def compute_mfdfa(signal, qvals=QVALS):
    lag = np.unique(np.logspace(0.5, 3, 50).astype(int))
    order = 2
    lag_used, Fq = MFDFA(signal, lag=lag, q=qvals, order=order)
    log_lag = np.log(lag_used)
    epsilon = 1e-10
    # Use the actual q values used by Fq
    qvals_used = qvals
    if Fq.shape[1] != len(qvals):
        # Assume q=0 was dropped, so remove it from qvals
        qvals_used = np.array([q for q in qvals if q != 0])
    H_q = np.array([
        np.polyfit(log_lag, np.log(Fq[:, i] + epsilon), 1)[0]
        for i in range(Fq.shape[1])
    ])
    dq = qvals_used[1] - qvals_used[0]
    tq = H_q * qvals_used - 1
    hq = np.gradient(tq, dq)
    Dq = qvals_used * hq - tq
    alpha_width = np.max(hq) - np.min(hq)
    alpha_peak = hq[np.argmax(Dq)]
    skew = (np.max(hq) + np.min(hq) - 2 * alpha_peak) / alpha_width if alpha_width > 0 else 0
    truncation = 'left' if skew > 0.05 else 'right' if skew < -0.05 else 'none'
    sorted_indices = np.argsort(hq)
    hq_sorted = np.array(hq)[sorted_indices]
    Dq_sorted = np.array(Dq)[sorted_indices]
    return {
        'alpha': json.dumps(hq_sorted.tolist()),
        'f_alpha': json.dumps(Dq_sorted.tolist()),
        'alpha_width': alpha_width,
        'alpha_peak': alpha_peak,
        'skew': skew,
        'truncation': truncation,
        'H_q': json.dumps(H_q.tolist())
    }

def parse_midi_filename(midi_path):
    # Example: .../1981/4/1981_04_full.mid
    base = os.path.basename(midi_path)
    parts = base.split('_')
    if len(parts) < 3:
        return None
    year = parts[0]
    rank = parts[1].lstrip('0')  # Remove leading zero for rank
    if rank == '':
        rank = '0'
    # Try both with and without leading zero, and with/without letter
    return year, rank

# Helper to trim leading/trailing zeros
def trim_leading_trailing_zeros(ts):
    nonzero = np.flatnonzero(ts)
    if len(nonzero) == 0:
        return np.array([])
    return ts[nonzero[0]:nonzero[-1]+1]

SMALL_VALUE = 1e-6  # Value to replace zeros for DFA/MFDFA on contour

def process_file(midi_path, debug_counter=[0]):
    try:
        year, rank = parse_midi_filename(midi_path)
        meta = meta_lookup.get((year, rank))
        if not meta:
            meta = meta_lookup.get((year, '0'+rank))
        if not meta:
            return None
        ts = midi_to_timeseries(midi_path)
        ts_notes = ts[ts > 0]
        # Debug print for first 5 files
        if debug_counter[0] < 5:
            print(f"File: {os.path.basename(midi_path)} | Length: {len(ts_notes)} | Unique: {np.unique(ts_notes)}")
            debug_counter[0] += 1
        # Lower threshold to 2
        if len(ts_notes) < 2:
            return {'skip_reason': 'too_short', 'file': midi_path, 'length': len(ts_notes), 'unique': np.unique(ts_notes)}
        if np.all(ts_notes == ts_notes[0]):
            return {'skip_reason': 'constant', 'file': midi_path, 'length': len(ts_notes), 'unique': np.unique(ts_notes)}
        dfa_notes = compute_dfa_nolds(ts_notes)
        mfdfa_notes = compute_mfdfa(ts_notes)
        dfa_row_notes = { 'year': meta['year'], 'position': meta['position'], 'artist': meta['artist'], 'title': meta['title'], **dfa_notes }
        mfdfa_row_notes = { 'year': meta['year'], 'position': meta['position'], 'artist': meta['artist'], 'title': meta['title'], **mfdfa_notes }
        return dfa_row_notes, mfdfa_row_notes
    except Exception as e:
        return {'skip_reason': f'error: {e}', 'file': midi_path}

def find_all_midi_files(root):
    midi_files = []
    for year in os.listdir(root):
        year_dir = os.path.join(root, year)
        if not os.path.isdir(year_dir):
            continue
        for rank in os.listdir(year_dir):
            rank_dir = os.path.join(year_dir, rank)
            if not os.path.isdir(rank_dir):
                continue
            for fname in os.listdir(rank_dir):
                if fname.endswith('_full.mid'):
                    midi_files.append(os.path.join(rank_dir, fname))
    return midi_files

if __name__ == "__main__":
    midi_files = find_all_midi_files(MIDI_ROOT)
    print(f"Found {len(midi_files)} MIDI files.")
    # For testing: only analyze the first 10 files
    midi_files = midi_files[:10]
    dfa_results_notes = []
    mfdfa_results_notes = []
    skipped = []
    with Pool(cpu_count()) as pool:
        for result in tqdm(pool.imap_unordered(process_file, midi_files), total=len(midi_files)):
            if isinstance(result, dict) and 'skip_reason' in result:
                skipped.append(result)
            elif result:
                dfa_row_notes, mfdfa_row_notes = result
                dfa_results_notes.append(dfa_row_notes)
                mfdfa_results_notes.append(mfdfa_row_notes)
    pd.DataFrame(dfa_results_notes).to_csv(DFA_OUT_NOTES, index=False)
    pd.DataFrame(mfdfa_results_notes).to_csv(MFDFA_OUT_NOTES, index=False)
    print(f"Saved DFA/MFDFA results for note-only (no zeros) representation.")
    print(f"Skipped {len(skipped)} files. Example skips:")
    for s in skipped[:10]:
        print(s)

# Representation notes:
# - *_notes.csv: DFA/MFDFA on the note sequence expanded by MIDI tick duration (each note is repeated according to its duration in ticks, using the shortest note as the unit) 