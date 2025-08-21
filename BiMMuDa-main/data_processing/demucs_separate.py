import os
import shutil
import subprocess
from pathlib import Path
from pydub import AudioSegment

def separate_songs(input_dir: str, output_dir: str,
                    model: str = 'htdemucs', two_stems: str = 'vocals'):
    """
    Separates each song in input_dir into vocals and instrumental using Demucs,
    and converts the outputs to MP3 with specified audio settings.

    Args:
        input_dir: Path to directory containing audio files (mp3, wav, flac).
        output_dir: Path where separated stems will be saved. Within this, two folders
                    named 'vocals' and 'instrumental' will be created.
        model: Demucs model name (e.g., 'htdemucs', 'demucs', etc.).
        two_stems: Stem to isolate ('vocals' for vocals vs accompaniment).
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    vocals_dir = output_dir / 'vocals'
    instr_dir = output_dir / 'instrumental'
    vocals_dir.mkdir(parents=True, exist_ok=True)
    instr_dir.mkdir(parents=True, exist_ok=True)

    for audio_file in input_dir.iterdir():
        if audio_file.suffix.lower() not in {'.mp3', '.wav', '.flac'}:
            continue

        print(f"\nProcessing {audio_file.name}...")
        cmd = [
            'demucs',
            '--two-stems', two_stems,
            '-n', model,
            '-o', str(output_dir),
            str(audio_file)
        ]
        subprocess.run(cmd, check=True)

        session_folder = output_dir / model / audio_file.stem
        vocals_file = session_folder / f"{two_stems}.wav"
        instr_file = session_folder / f"no_{two_stems}.wav"

        vocals_out = vocals_dir / f"{audio_file.stem}_vocals.mp3"
        instr_out = instr_dir / f"{audio_file.stem}_instrumental.mp3"

        # Convert to MP3 with matching settings
        vocals_audio = AudioSegment.from_wav(vocals_file)
        vocals_audio.export(vocals_out, format="mp3", bitrate="128k", parameters=["-ar", "48000", "-ac", "2"])

        instr_audio = AudioSegment.from_wav(instr_file)
        instr_audio.export(instr_out, format="mp3", bitrate="128k", parameters=["-ar", "48000", "-ac", "2"])

        shutil.rmtree(output_dir / model)

    print("\nAll files processed. Vocals are in:", vocals_dir)
    print("Instrumental tracks are in:", instr_dir)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Separate songs into vocals and instrumental using Demucs.'
    )
    parser.add_argument(
        '--input_dir', type=str, required=True,
        help='Directory containing input audio files'
    )
    parser.add_argument(
        '--output_dir', type=str, required=True,
        help="Directory where 'vocals' and 'instrumental' folders will be created"
    )
    parser.add_argument(
        '--model', type=str, default='htdemucs',
        help='Demucs model name to use'
    )
    parser.add_argument(
        '--two_stems', type=str, default='vocals',
        help="Stem to isolate (e.g., 'vocals' will produce 'vocals' and 'no_vocals')"
    )

    args = parser.parse_args()
    separate_songs(args.input_dir, args.output_dir, args.model, args.two_stems)
