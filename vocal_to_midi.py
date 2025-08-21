import librosa
import numpy as np
from midiutil import MIDIFile
import os

def vocal_to_midi(input_file, output_file, threshold=0.05):
    # Load the audio file
    y, sr = librosa.load(input_file)
    
    # Extract pitch using PYIN (more accurate for vocals than piptrack)
    f0, voiced_flag, voiced_probs = librosa.pyin(y, 
                                                sr=sr, 
                                                fmin=librosa.note_to_hz('C2'), 
                                                fmax=librosa.note_to_hz('C7'))
    
    # Create a MIDI file with one track
    midi = MIDIFile(1)
    track = 0
    time = 0
    midi.addTrackName(track, time, "Vocal Track")
    midi.addTempo(track, time, 120)
    
    # Set channel and volume
    channel = 0
    volume = 100
    
    # Process pitch information
    last_note = None
    start_time = 0
    hop_length = 512  # Default hop length in librosa
    
    # Convert time frames to seconds
    times = librosa.times_like(f0, sr=sr, hop_length=hop_length)
    
    for t, pitch, voiced in zip(times, f0, voiced_flag):
        # Check if the frame has a valid pitch and is voiced
        if voiced and not np.isnan(pitch):
            midi_note = int(round(librosa.hz_to_midi(pitch)))
            
            # If this is a new note or first note
            if midi_note != last_note:
                # If there was a previous note, end it
                if last_note is not None:
                    duration = t - start_time
                    if duration > 0.1:  # Minimum duration to avoid very short notes
                        midi.addNote(track, channel, last_note, start_time, duration, volume)
                
                # Start a new note
                last_note = midi_note
                start_time = t
        elif last_note is not None:
            # End the current note on unvoiced frame
            duration = t - start_time
            if duration > 0.1:
                midi.addNote(track, channel, last_note, start_time, duration, volume)
            last_note = None
        
    # End the last note if there was one
    if last_note is not None:
        duration = times[-1] - start_time
        if duration > 0.1:
            midi.addNote(track, channel, last_note, start_time, duration, volume)
    
    # Write the MIDI file
    with open(output_file, "wb") as f:
        midi.writeFile(f)

# Process all vocal tracks in your directory
vocal_dir = "/home/data/kevinzhang/research/fractal_analysis/BiMMuDa-main/audio_data/billboard/vocals/full_duration"
output_dir = "/home/data/kevinzhang/research/fractal_analysis/BiMMuDa-main/audio_data/billboard/vocals/midi"  # Create this directory if it doesn't exist

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Process each vocal track
for filename in os.listdir(vocal_dir):
    if filename.endswith(".mp3"):
        input_path = os.path.join(vocal_dir, filename)
        output_path = os.path.join(output_dir, filename.replace(".mp3", ".mid"))
        print(f"Converting {input_path} to {output_path}")
        vocal_to_midi(input_path, output_path)
        # test for one song only
        break