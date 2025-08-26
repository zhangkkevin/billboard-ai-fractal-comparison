import os
import re
import subprocess
import csv

# Function to count lyric segments
def count_segments(filepath):
    try:
        with open(filepath, "r") as f:
            text = f.read()
            return len(re.findall(r"\[\s*(verse|chorus|bridge|intro|outro|pre-chorus)\s*\]", text, re.IGNORECASE))
    except:
        return 2  # Default fallback
    
def log_result(csv_path, row):
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        if os.stat(csv_path).st_size == 0:
            writer.writerow(["song_id", "reason"])
        writer.writerow(row)

# Working directory where YuE is installed
infer_dir = "/home/data/kevinzhang/research/mgs/YuE/inference"
os.chdir(infer_dir)

# Directories
lyrics_dir = "/home/data/kevinzhang/research/BiMMuDa-main/metadata/yue_prompts/lyrics"
genre_dir = "/home/data/kevinzhang/research/BiMMuDa-main/metadata/yue_prompts/genre"
vocal_dir = "/home/data/kevinzhang/research/BiMMuDa-main/audio_data/billboard/vocals/50s_80s"
instrumental_dir = "/home/data/kevinzhang/research/BiMMuDa-main/audio_data/billboard/instrumental/50s_80s"
output_dir = "/home/data/kevinzhang/research/BiMMuDa-main/audio_data/YuE"
infer_script_path = os.path.join(infer_dir, "infer.py")

# YuE config
stage1_model = "m-a-p/YuE-s1-7B-anneal-en-icl"
stage2_model = "m-a-p/YuE-s2-1B-general"
cuda_idx = 5
start_time = 0
end_time = 30
max_new_tokens = 3000

# Logging setup
fail_log_path = "/home/data/kevinzhang/research/BiMMuDa-main/logs/yue_generation_failures.csv"
success_log_path = "/home/data/kevinzhang/research/BiMMuDa-main/logs/yue_generation_successes.csv"

# Iterate through lyric files
i = 0
for filename in os.listdir(lyrics_dir):
    if not filename.endswith(".txt"):
        continue

    song_id = filename.replace("_lyrics.txt", "")
    lyrics_path = os.path.join(lyrics_dir, f"{song_id}_lyrics.txt")
    genre_path = os.path.join(genre_dir, f"{song_id}_genre.txt")
    vocal_path = os.path.join(vocal_dir, f"{song_id}_vocals.mp3")
    instrumental_path = os.path.join(instrumental_dir, f"{song_id}_instrumental.mp3")

    if not all(os.path.exists(p) for p in [lyrics_path, genre_path, vocal_path, instrumental_path]):
        log_result(fail_log_path, [song_id, "Missing required input files"])
        print(f"⚠️ Skipping {song_id}: Missing file(s)")
        continue

    n_segments = count_segments(lyrics_path)

    command = [
        "python", infer_script_path,
        "--cuda_idx", str(cuda_idx),
        "--stage1_model", stage1_model,
        "--stage2_model", stage2_model,
        "--genre_txt", genre_path,
        "--lyrics_txt", lyrics_path,
        "--run_n_segments", str(n_segments),
        # "--run_n_segments", "2",
        "--stage2_batch_size", "4",
        "--output_dir", output_dir,
        "--max_new_tokens", str(max_new_tokens),
        "--repetition_penalty", "1.1",
        "--use_dual_tracks_prompt",
        "--vocal_track_prompt_path", vocal_path,
        "--instrumental_track_prompt_path", instrumental_path,
        "--prompt_start_time", str(start_time),
        "--prompt_end_time", str(end_time)
    ]

    print(f"\n🎵 Generating: {song_id} | Segments: {n_segments}")

    try:
        result = subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        # Convert the command's error output to string only if needed
        error_type = "CUDA OutOfMemoryError" if "OutOfMemoryError" in str(e) else "RuntimeError"
        log_result(fail_log_path, [song_id, f"Generation failed: {error_type}"])
        print(f"❌ Generation failed for {song_id} ({error_type})")
        
    if i == 1:
        break
    i += 1