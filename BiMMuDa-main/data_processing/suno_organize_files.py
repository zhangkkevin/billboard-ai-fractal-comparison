import os

# Directory to check
directory = "/home/data/kevinzhang/research/BiMMuDa-main/audio_data/diffrhythm/instrumental"  # replace with your actual path

# Collect files with .mp3.wav extension
bad_files = []
for filename in os.listdir(directory):
    if filename.endswith(".mp3.wav"):
        try:
            year = int(filename.split("_")[0])
            corrected = filename.replace(".mp3.wav", ".wav")
            bad_files.append((year, filename, corrected))
        except ValueError:
            print(f"⚠️ Skipping malformed filename: {filename}")

# Sort files by year
bad_files.sort(key=lambda x: x[0])

# Print sorted results
for year, original, corrected in bad_files:
    print(f"{year} | ⚠️ {original} → ✅ {corrected}")