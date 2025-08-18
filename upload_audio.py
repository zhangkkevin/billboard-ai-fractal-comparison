#!/usr/bin/env python3
"""
Audio Upload Script for Billboard AI Fractal Comparison Website

This script helps upload audio files from the audio_data directory to the website's audio folder
and manages the metadata for the website.
"""

import os
import shutil
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

class AudioUploader:
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
        """Load existing audio metadata from JSON file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {self.metadata_file}, starting fresh")
                return {}
        return {}
    
    def save_metadata(self):
        """Save audio metadata to JSON file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def get_audio_files(self) -> Dict[str, List[Path]]:
        """Get all audio files from the audio_data directory."""
        audio_files = {}
        
        for model_dir in self.audio_data_dir.iterdir():
            if model_dir.is_dir():
                model_name = model_dir.name
                audio_files[model_name] = []
                
                # Look for audio files in non_separated/full_duration (billboard)
                non_separated_dir = model_dir / "non_separated"
                if non_separated_dir.exists():
                    full_duration_dir = non_separated_dir / "full_duration"
                    if full_duration_dir.exists():
                        # Billboard structure
                        for audio_file in full_duration_dir.glob("*.mp3"):
                            audio_files[model_name].append(audio_file)
                    else:
                        # AI model structure (files directly in non_separated)
                        for audio_file in non_separated_dir.glob("*.mp3"):
                            audio_files[model_name].append(audio_file)
                else:
                    # Some models have files directly in the main directory
                    for audio_file in model_dir.glob("*.mp3"):
                        audio_files[model_name].append(audio_file)
        
        return audio_files
    
    def parse_filename(self, filename: str) -> Dict:
        """Parse audio filename to extract metadata."""
        # Expected format: YYYY_Rank_Artist_Title.mp3
        # Example: 2006_1_Daniel Powter_Bad Day.mp3
        
        name_without_ext = filename.replace('.mp3', '')
        parts = name_without_ext.split('_', 2)  # Split into max 3 parts
        
        if len(parts) >= 3:
            year = parts[0]
            rank = parts[1]
            artist_title = parts[2]
            
            # Try to separate artist and title (usually by last underscore)
            if '_' in artist_title:
                # Find the last underscore to separate artist and title
                last_underscore = artist_title.rfind('_')
                artist = artist_title[:last_underscore]
                title = artist_title[last_underscore + 1:]
            else:
                artist = artist_title
                title = artist_title
            
            return {
                'year': int(year),
                'rank': rank,
                'artist': artist,
                'title': title
            }
        
        return {
            'year': None,
            'rank': None,
            'artist': 'Unknown',
            'title': filename.replace('.mp3', '')
        }
    
    def copy_audio_file(self, source_path: Path, model: str) -> Optional[str]:
        """Copy an audio file to the website audio directory."""
        try:
            # Create a unique filename to avoid conflicts
            filename = source_path.name
            parsed_info = self.parse_filename(filename)
            
            # Create a more descriptive filename
            safe_title = parsed_info['title'].replace(' ', '_').replace('/', '_').replace('\\', '_')
            safe_artist = parsed_info['artist'].replace(' ', '_').replace('/', '_').replace('\\', '_')
            
            new_filename = f"{model}_{parsed_info['year']}_{parsed_info['rank']}_{safe_artist}_{safe_title}.mp3"
            new_filename = new_filename.replace('__', '_')  # Clean up double underscores
            
            dest_path = self.audio_dir / new_filename
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            
            # Calculate file hash for integrity
            file_hash = self.calculate_file_hash(source_path)
            
            # Store metadata
            file_id = str(hash(file_hash))
            self.metadata[file_id] = {
                'filename': new_filename,
                'original_path': str(source_path),
                'model': model,
                'title': parsed_info['title'],
                'artist': parsed_info['artist'],
                'year': parsed_info['year'],
                'rank': parsed_info['rank'],
                'file_size': source_path.stat().st_size,
                'file_hash': file_hash,
                'upload_date': str(Path().cwd())
            }
            
            return file_id
            
        except Exception as e:
            print(f"Error copying {source_path}: {e}")
            return None
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def upload_all_audio(self, models: Optional[List[str]] = None):
        """Upload all audio files from specified models."""
        audio_files = self.get_audio_files()
        
        if models:
            audio_files = {k: v for k, v in audio_files.items() if k in models}
        
        total_files = sum(len(files) for files in audio_files.values())
        uploaded_count = 0
        
        print(f"Found {total_files} audio files to upload")
        
        for model, files in audio_files.items():
            print(f"\nProcessing {model} ({len(files)} files):")
            
            for file_path in files:
                print(f"  Uploading: {file_path.name}")
                file_id = self.copy_audio_file(file_path, model)
                
                if file_id:
                    uploaded_count += 1
                    print(f"    ✓ Uploaded as {self.metadata[file_id]['filename']}")
                else:
                    print(f"    ✗ Failed to upload")
        
        # Save metadata
        self.save_metadata()
        
        print(f"\nUpload complete! {uploaded_count}/{total_files} files uploaded successfully.")
        print(f"Metadata saved to: {self.metadata_file}")
    
    def list_uploaded_files(self):
        """List all uploaded audio files."""
        if not self.metadata:
            print("No audio files uploaded yet.")
            return
        
        print(f"Uploaded Audio Files ({len(self.metadata)} total):")
        print("-" * 80)
        
        for file_id, info in self.metadata.items():
            print(f"ID: {file_id}")
            print(f"  File: {info['filename']}")
            print(f"  Song: {info['title']} - {info['artist']}")
            print(f"  Year: {info['year']}, Rank: {info['rank']}")
            print(f"  Model: {info['model']}")
            print(f"  Size: {info['file_size']} bytes")
            print()
    
    def cleanup_orphaned_files(self):
        """Remove audio files that are no longer in metadata."""
        if not self.audio_dir.exists():
            return
        
        metadata_files = {info['filename'] for info in self.metadata.values()}
        actual_files = {f.name for f in self.audio_dir.iterdir() if f.is_file()}
        
        orphaned_files = actual_files - metadata_files
        
        if orphaned_files:
            print(f"Found {len(orphaned_files)} orphaned files:")
            for filename in orphaned_files:
                file_path = self.audio_dir / filename
                print(f"  {filename}")
                if input("Delete this file? (y/N): ").lower() == 'y':
                    file_path.unlink()
                    print(f"    Deleted {filename}")
        else:
            print("No orphaned files found.")

def main():
    parser = argparse.ArgumentParser(description="Upload audio files to the website")
    parser.add_argument("--audio-data-dir", default="audio_data", help="Directory containing audio files")
    parser.add_argument("--docs-dir", default="docs", help="Website docs directory")
    parser.add_argument("--models", nargs="+", help="Specific models to upload (e.g., billboard suno)")
    parser.add_argument("--list", action="store_true", help="List uploaded files")
    parser.add_argument("--cleanup", action="store_true", help="Clean up orphaned files")
    
    args = parser.parse_args()
    
    uploader = AudioUploader(args.audio_data_dir, args.docs_dir)
    
    if args.list:
        uploader.list_uploaded_files()
    elif args.cleanup:
        uploader.cleanup_orphaned_files()
    else:
        uploader.upload_all_audio(args.models)

if __name__ == "__main__":
    main()
