import os
from pydub import AudioSegment
from mutagen.mp3 import MP3

# Paths
input_dir = "/home/data/kevinzhang/research/BiMMuDa-main/audio_data/billboard/instrumental"
output_dir = "/home/data/kevinzhang/research/BiMMuDa-main/audio_data/billboard/instrumental/50s_80s"
os.makedirs(output_dir, exist_ok=True)

# Parameters
start_ms = 50 * 1000  # 50 seconds
end_ms = 80 * 1000    # 80 seconds

# Detect reference quality settings from the first MP3 file
for f in os.listdir(input_dir):
    if f.lower().endswith(".mp3"):
        ref_path = os.path.join(input_dir, f)
        audio = AudioSegment.from_file(ref_path)
        meta = MP3(ref_path)
        sample_rate = audio.frame_rate
        channels = audio.channels
        bitrate = f"{int(meta.info.bitrate / 1000)}k"
        print(f"🔍 Using quality: {sample_rate} Hz, {channels} channel(s), {bitrate}")
        break
else:
    raise RuntimeError("❌ No MP3 files found in input directory.")

# Process all MP3 files
for filename in os.listdir(input_dir):
    if not filename.lower().endswith(".mp3"):
        continue

    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, filename)

    # Skip if already exists
    if os.path.exists(output_path):
        print(f"⏩ Skipping (already exists): {filename}")
        continue

    try:
        audio = AudioSegment.from_file(input_path)
        if len(audio) >= end_ms:
            segment = audio[start_ms:end_ms]
            segment.export(
                output_path,
                format="mp3",
                parameters=[
                    "-ar", str(sample_rate),
                    "-ac", str(channels),
                    "-b:a", bitrate
                ]
            )
            print(f"✅ Extracted: {filename}")
        else:
            print(f"⚠️ Skipped (too short): {filename}")
    except Exception as e:
        print(f"❌ Failed to process {filename}: {e}")