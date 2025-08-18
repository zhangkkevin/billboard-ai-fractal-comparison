#!/usr/bin/env python3
"""
Upload Specific Songs Script for Billboard AI Fractal Comparison Website

This script uploads only the specific songs referenced in the analysis results
to the website's audio folder.
"""

import os
import shutil
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

# Songs from the analysis results
ANALYSIS_SONGS = [
    # DFA Analysis
    {"model": "billboard", "title": "Bad Day", "artist": "Daniel Powter", "year": 2006, "rank": 1},
    {"model": "suno_v4_5", "title": "Anti-Hero", "artist": "Taylor Swift", "year": 2023, "rank": 4},
    {"model": "diffrhythm", "title": "Claudette", "artist": "The Everly Brothers", "year": 1958, "rank": "2b"},
    {"model": "YuE", "title": "All Shook Up", "artist": "Elvis Presley", "year": 1957, "rank": 1},
    
    {"model": "billboard", "title": "Let Me Love You", "artist": "Mario", "year": 2005, "rank": 3},
    {"model": "suno_v4_5", "title": "Love's Theme", "artist": "Love Unlimited Orchestra", "year": 1974, "rank": 3},
    {"model": "diffrhythm", "title": "Hanging By A Moment", "artist": "Lifehouse", "year": 2001, "rank": 1},
    {"model": "YuE", "title": "Harlem Shake", "artist": "Baauer", "year": 2013, "rank": 4},
    
    {"model": "billboard", "title": "Rockstar", "artist": "DaBaby feat. Roddy Ricch", "year": 2020, "rank": 5},
    {"model": "suno_v4_5", "title": "You're Beautiful", "artist": "James Blunt", "year": 2006, "rank": 4},
    {"model": "diffrhythm", "title": "Mona Lisa", "artist": "Nat King Cole", "year": 1950, "rank": 2},
    {"model": "YuE", "title": "Blue Tango", "artist": "Leroy Anderson", "year": 1952, "rank": 1},
    
    # MFDFA Analysis
    {"model": "billboard", "title": "Sugar", "artist": "Maroon 5", "year": 2015, "rank": 5},
    {"model": "suno_v4_5", "title": "The Yellow Rose of Texas", "artist": "Mitch Miller", "year": 1955, "rank": 3},
    {"model": "diffrhythm", "title": "When I'm Gone", "artist": "3 Doors Down", "year": 2003, "rank": 5},
    {"model": "YuE", "title": "The Sweet Escape", "artist": "Gwen Stefani feat. Akon", "year": 2007, "rank": 3},
    
    {"model": "billboard", "title": "Dark Horse", "artist": "Katy Perry and Juicy J", "year": 2014, "rank": 2},
    {"model": "suno_v4_5", "title": "Hot in Herre", "artist": "Nelly", "year": 2002, "rank": 3},
    {"model": "diffrhythm", "title": "Auf Wiederseh'n Sweetheart", "artist": "Vera Lynn", "year": 1952, "rank": 5},
    {"model": "YuE", "title": "rockstar", "artist": "Post Malone feat. 21 Savage", "year": 2018, "rank": 5},
    
    {"model": "billboard", "title": "Auf Wiederseh'n Sweetheart", "artist": "Vera Lynn", "year": 1952, "rank": 5},
    {"model": "suno_v4_5", "title": "Good 4 U", "artist": "Olivia Rodrigo", "year": 2021, "rank": 5},
    {"model": "diffrhythm", "title": "Poker Face", "artist": "Lady Gaga", "year": 2009, "rank": 2},
    {"model": "YuE", "title": "Honey", "artist": "Bobby Goldsboro", "year": 1968, "rank": 3},
    
    {"model": "billboard", "title": "Low", "artist": "Flo Rida feat. T-Pain", "year": 2008, "rank": 1},
    {"model": "suno_v4_5", "title": "Hips Don't Lie", "artist": "Shakira feat. Wyclef Jean", "year": 2006, "rank": 5},
    {"model": "diffrhythm", "title": "Without Me", "artist": "Halsey", "year": 2019, "rank": 3},
    {"model": "YuE", "title": "Blue Tango", "artist": "Leroy Anderson", "year": 1952, "rank": 1},
    
    # JSD Analysis
    {"model": "suno_v4_5", "title": "End of the Road", "artist": "Boyz II Men", "year": 1992, "rank": 1},
    {"model": "diffrhythm", "title": "Bad Guy", "artist": "Billie Eilish", "year": 2019, "rank": 4},
    {"model": "YuE", "title": "Uptown Funk", "artist": "Mark Ronson feat. Bruno Mars", "year": 2015, "rank": 1},
    
    {"model": "suno_v4_5", "title": "Hot in Herre", "artist": "Nelly", "year": 2002, "rank": 3},
    {"model": "diffrhythm", "title": "Hanging By A Moment", "artist": "Lifehouse", "year": 2001, "rank": 1},
    {"model": "YuE", "title": "Straight Up", "artist": "Paula Abdul", "year": 1989, "rank": 4},
]

class SpecificSongUploader:
    def __init__(self, audio_data_dir: str = "audio_data", docs_dir: str = "docs"):
        self.audio_data_dir = Path(audio_data_dir)
        self.docs_dir = Path(docs_dir)
        self.audio_dir = self.docs_dir / "audio"
        self.metadata_file = self.docs_dir / "audio_metadata.json"
        
        # Create audio directory if it doesn't exist
        self.audio_dir.mkdir(exist_ok=True)
        
        # Load existing metadata
        self.metadata = self.load_metadata()
    
    def load_metadata(self) -> Dict:
        """Load existing metadata file."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"files": {}}
    
    def save_metadata(self):
        """Save metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def find_audio_file(self, song_info: Dict) -> Optional[Path]:
        """Find the audio file for a specific song."""
        model = song_info["model"]
        year = song_info["year"]
        rank = song_info["rank"]
        title = song_info["title"]
        artist = song_info["artist"]
        
        # Construct the expected filename
        expected_filename = f"{year}_{rank}_{artist}_{title}.mp3"
        
        # Look in different possible locations based on model structure
        possible_paths = []
        
        if model == "billboard":
            # Billboard structure: audio_data/billboard/non_separated/full_duration/
            possible_paths.append(self.audio_data_dir / model / "non_separated" / "full_duration" / expected_filename)
        else:
            # AI model structures
            # Try: audio_data/model/non_separated/
            possible_paths.append(self.audio_data_dir / model / "non_separated" / expected_filename)
            # Try: audio_data/model/
            possible_paths.append(self.audio_data_dir / model / expected_filename)
        
        # Check each possible path
        for path in possible_paths:
            if path.exists():
                return path
        
        # If not found, try to find by partial matching
        return self.find_by_partial_match(model, year, rank, title, artist)
    
    def find_by_partial_match(self, model: str, year: int, rank, title: str, artist: str) -> Optional[Path]:
        """Find audio file by partial matching of filename components."""
        if model == "billboard":
            search_dir = self.audio_data_dir / model / "non_separated" / "full_duration"
        else:
            search_dir = self.audio_data_dir / model / "non_separated"
            if not search_dir.exists():
                search_dir = self.audio_data_dir / model
        
        if not search_dir.exists():
            return None
        
        # Search for files containing the year and rank
        year_str = str(year)
        rank_str = str(rank)
        
        for audio_file in search_dir.glob("*.mp3"):
            filename = audio_file.name
            if year_str in filename and rank_str in filename:
                # Additional check for title/artist keywords
                title_words = title.lower().split()
                artist_words = artist.lower().split()
                
                filename_lower = filename.lower()
                title_match = any(word in filename_lower for word in title_words if len(word) > 2)
                artist_match = any(word in filename_lower for word in artist_words if len(word) > 2)
                
                if title_match or artist_match:
                    return audio_file
        
        return None
    
    def upload_song(self, song_info: Dict) -> bool:
        """Upload a specific song."""
        source_file = self.find_audio_file(song_info)
        
        if not source_file:
            print(f"  ❌ Not found: {song_info['title']} - {song_info['artist']}")
            return False
        
        # Create filename for the website
        model = song_info["model"]
        year = song_info["year"]
        rank = song_info["rank"]
        title = song_info["title"].replace(" ", "_").replace("'", "").replace('"', "").replace("&", "and")
        artist = song_info["artist"].replace(" ", "_").replace("'", "").replace('"', "").replace("&", "and")
        
        dest_filename = f"{model}_{year}_{rank}_{artist}_{title}.mp3"
        dest_path = self.audio_dir / dest_filename
        
        # Copy file
        shutil.copy2(source_file, dest_path)
        
        # Update metadata
        file_hash = self.calculate_file_hash(dest_path)
        self.metadata["files"][file_hash] = {
            "file": dest_filename,
            "song": f"{title} - {artist}",
            "year": year,
            "rank": rank,
            "model": model,
            "size": dest_path.stat().st_size
        }
        
        print(f"  ✓ Uploaded: {song_info['title']} - {song_info['artist']}")
        return True
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate hash of file for metadata."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return str(hash_md5.hexdigest())
    
    def upload_all_songs(self):
        """Upload all songs from the analysis results."""
        # Filter out Billboard songs (we'll use YouTube embeds for those)
        ai_songs = [song for song in ANALYSIS_SONGS if song["model"].lower() != "billboard"]
        
        print(f"Uploading {len(ai_songs)} AI-generated songs from analysis results...")
        print("(Billboard songs will use YouTube embeds for copyright compliance)")
        
        uploaded_count = 0
        for song_info in ai_songs:
            if self.upload_song(song_info):
                uploaded_count += 1
        
        # Save metadata
        self.save_metadata()
        
        print(f"\nUpload complete! {uploaded_count}/{len(ai_songs)} AI-generated songs uploaded successfully.")
        print(f"Metadata saved to: {self.metadata_file}")

def main():
    parser = argparse.ArgumentParser(description="Upload specific songs from analysis results")
    parser.add_argument("--audio-data-dir", default="audio_data", help="Audio data directory")
    parser.add_argument("--docs-dir", default="docs", help="Docs directory")
    
    args = parser.parse_args()
    
    uploader = SpecificSongUploader(args.audio_data_dir, args.docs_dir)
    uploader.upload_all_songs()

if __name__ == "__main__":
    main()
