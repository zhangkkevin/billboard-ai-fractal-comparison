import os
from pydub import AudioSegment

# Set paths
input_dir = "/home/data/kevinzhang/research/BiMMuDa-main/audio_data/diffrhythm/instrumental_wav"   # ← Replace with your WAV directory
output_dir = "/home/data/kevinzhang/research/BiMMuDa-main/audio_data/diffrhythm/instrumental_mp3" # ← Replace with desired MP3 output directory
os.makedirs(output_dir, exist_ok=True)

# Conversion settings
BITRATE = "128k"
SAMPLE_RATE = 44100
CHANNELS = 2

for filename in os.listdir(input_dir):
    if filename.lower().endswith(".wav"):
        wav_path = os.path.join(input_dir, filename)
        mp3_name = os.path.splitext(filename)[0] + ".mp3"
        mp3_path = os.path.join(output_dir, mp3_name)

        try:
            audio = AudioSegment.from_wav(wav_path)
            audio = audio.set_frame_rate(SAMPLE_RATE).set_channels(CHANNELS)
            audio.export(mp3_path, format="mp3", bitrate=BITRATE)
            print(f"✅ Converted: {filename} → {mp3_name}")
        except Exception as e:
            print(f"❌ Failed to convert {filename}: {e}")