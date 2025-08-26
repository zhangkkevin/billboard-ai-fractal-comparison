import os
import subprocess
import shutil
import csv

# Required directories and paths
billboard_dir = "/home/data/kevinzhang/research/BiMMuDa-main/billboard_audio_mp3"
output_dir = "/home/data/kevinzhang/research/BiMMuDa-main/diffrhythm"
diff_rhythm_script = "infer/infer.py"  # Relative to new CWD below
diff_rhythm_dir = "/home/data/kevinzhang/research/mgs/DiffRhythm"  # <- Your required CWD
fail_log_path = "/home/data/kevinzhang/research/BiMMuDa-main/logs/diffrhythm_generation_failures.csv"

# Ensure output and log directories exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(os.path.dirname(fail_log_path), exist_ok=True)

# Write header if needed
if not os.path.exists(fail_log_path):
    with open(fail_log_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "reason"])

# Loop through songs
for filename in os.listdir(billboard_dir):
    if not filename.endswith(".mp3"):
        continue

    input_path = os.path.join(billboard_dir, filename)
    base_name = os.path.splitext(filename)[0]
    output_target_path = os.path.join(output_dir, base_name + ".wav")
    default_output_path = os.path.join(output_dir, "output.wav")

    if os.path.exists(output_target_path):
        print(f"✅ Skipping {filename} (already generated)")
        continue

    print(f"🎵 Generating: {filename}")

    command = [
        "python3", diff_rhythm_script,
        "--ref-audio-path", input_path,
        "--audio-length", "95",
        "--repo_id", "ASLP-lab/DiffRhythm-full",
        "--output-dir", output_dir,
        "--chunked"
    ]

    try:
        subprocess.run(command, check=True, cwd=diff_rhythm_dir)

        if os.path.exists(default_output_path):
            shutil.move(default_output_path, output_target_path)
            print(f"✅ Saved as {output_target_path}")
        else:
            raise FileNotFoundError("output.wav not found")

    except Exception as e:
        print(f"❌ Generation failed for {filename}: {e}")
        with open(fail_log_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([filename, str(e)])