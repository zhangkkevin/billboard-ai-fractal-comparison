import os
import pandas as pd
import yt_dlp
import mido
from mutagen.wave import WAVE

# Load full metadata with top5_rank (e.g., '2a') and numeric_rank (e.g., 2)
df = pd.read_csv("/home/data/kevinzhang/research/BiMMuDa-main/metadata/bimmuda_per_song_metadata.csv")

# Output directory
output_dir = "/home/data/kevinzhang/research/BiMMuDa-main/billboard_audio"
os.makedirs(output_dir, exist_ok=True)

# Function to load MIDI duration using numeric rank
def get_midi_duration(year, rank):
    try:
        midi_path = f"/home/data/kevinzhang/research/BiMMuDa-main/bimmuda_dataset/{year}/{rank}/{year}_0{rank}_full.mid"
        mid = mido.MidiFile(midi_path)
        return mid.length
    except Exception as e:
        print(f"⚠️ MIDI not found or unreadable for {year}_{rank}: {e}")
        return None

# YT-DLP base options
base_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'outtmpl': os.path.join(output_dir, 'temp.%(ext)s'),
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192',
    }]
}

# Failure log
fail_log = []

# Download loop
for i, row in df.iterrows():
    title, artist, year = row['Title'], row['Artist'], row['Year']
    top5_rank = row['Position']
    target_filename = f"{year}_{top5_rank}_{artist}_{title}.wav"
    query = f"{title} {artist} {year} audio"

    print(f"🔍 Searching YouTube: {query}")

    midi_duration = get_midi_duration(year, top5_rank)
    print(f"🎵 MIDI duration: {round(midi_duration)}s")
    if midi_duration is None:
        fail_log.append((title, artist, year, top5_rank, "Missing MIDI"))
        continue

    try:
        with yt_dlp.YoutubeDL(base_opts) as ydl:
            ydl.download([f"ytsearch1:{query}"])

        downloaded_path = os.path.join(output_dir, "temp.wav")
        final_path = os.path.join(output_dir, target_filename)

        if os.path.exists(downloaded_path):
            audio = WAVE(downloaded_path)
            duration = audio.info.length

            tolerance = 0.4  # 40% tolerance
            lower_bound = midi_duration * (1 - tolerance)
            upper_bound = midi_duration * (1 + tolerance)

            if lower_bound < duration < upper_bound:
                os.rename(downloaded_path, final_path)
                print(f"✅ Saved: {target_filename} ({round(duration)}s, MIDI ≈ {round(midi_duration)}s)")
            else:
                print(f"❌ Duration mismatch: {round(duration)}s vs MIDI {round(midi_duration)}s")
                fail_log.append((title, artist, year, top5_rank, f"Mismatch: {round(duration)}s"))
                os.remove(downloaded_path)
        else:
            fail_log.append((title, artist, year, top5_rank, "Missing temp.wav"))

    except Exception as e:
        print(f"❌ Download failed for {title}: {e}")
        fail_log.append((title, artist, year, top5_rank, str(e)))
    
    break

# Save failure log
fail_df = pd.DataFrame(fail_log, columns=["title", "artist", "year", "top5_rank", "error"])
fail_df.to_csv("/home/data/kevinzhang/research/BiMMuDa-main/youtube_download_failures.csv", index=False)
print("\\n📄 Failure log saved to youtube_download_failures.csv")