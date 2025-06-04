#!/usr/bin/env python3
"""
AI Video Creator - Create engaging videos with AI narration and dynamic subtitles.

This tool allows users to create vertical videos (1080x1920) with:
- Manual or AI-generated story narration
- ElevenLabs voice synthesis
- Background gameplay footage
- Dynamic subtitles with word highlighting
"""

import argparse
import os
import random
import json
import time
from pathlib import Path
import tempfile
from typing import Dict, List, Tuple, Optional
import re

try:
    import requests
    from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
    from moviepy.video.tools.subtitles import SubtitlesClip
    import numpy as np
    from textblob import TextBlob
    import openai
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(["pip", "install", "requests", "moviepy", "numpy", "textblob", "openai", "python-dotenv"])
    import requests
    from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
    from moviepy.video.tools.subtitles import SubtitlesClip
    import numpy as np
    from textblob import TextBlob
    import openai

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Constants
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
OUTPUT_FILE = "output/final_output.mp4"
VIDEOS_DIR = "videos"
TEMP_DIR = tempfile.gettempdir()

# Voice mapping based on themes
VOICE_MAPPING = {
    "emotional": "Rachel",  # Emotional, reflective
    "dramatic": "Bella",    # Intense, dramatic
    "comedic": "Elli",      # Upbeat, comedic
    "neutral": "Adam",      # Default, neutral
    "mysterious": "Antoni", # Mysterious, suspenseful
    "energetic": "Josh",    # Energetic, exciting
}

# Voice IDs for ElevenLabs (replace with actual IDs)
VOICE_IDS = {
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Bella": "EXAVITQu4vr4xnSDxMaL",
    "Elli": "MF3mGyEYCl7XYWbV9V6O",
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Antoni": "ErXwobaYiN019PkySvjV",
    "Josh": "TxGEqnHWrfWFTfGW9XjX",
}

class AIVideoCreator:
    def __init__(self):
        self.story = ""
        self.theme = "neutral"
        self.voice = "Adam"
        self.voice_id = VOICE_IDS["Adam"]
        self.audio_path = ""
        self.video_path = ""
        self.subtitles = []
        self.word_timings = []
        
    def get_user_input(self):
        """Get the story input mode from the user."""
        print("Select input mode:")
        print("[1] Manually enter story")
        print("[2] Auto-generate story using AI")
        
        choice = input("> ")
        
        if choice == "1":
            print("\nEnter your story (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)
            self.story = "\n".join(lines)
            print("\n[✔] Story received")
        elif choice == "2":
            self.generate_ai_story()
        else:
            print("Invalid choice. Defaulting to manual input.")
            self.get_user_input()
    
    def generate_ai_story(self):
        """Generate a story using OpenAI's API."""
        if not OPENAI_API_KEY:
            print("Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            self.story = input("Please enter a story manually instead: ")
            return
            
        print("\nGenerating story...")
        
        try:
            openai.api_key = OPENAI_API_KEY
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative storyteller."},
                    {"role": "user", "content": "Write a dramatic, emotional story for a 60-second video narration. Keep it concise (150-200 words) and engaging."}
                ]
            )
            self.story = response.choices[0].message.content.strip()
            print(f"\n[✔] Generated story:\n{self.story}\n")
        except Exception as e:
            print(f"Error generating story: {e}")
            self.story = input("Please enter a story manually instead: ")
    
    def detect_theme(self):
        """Detect the theme/emotion of the story."""
        print("\nAnalyzing story theme...")
        
        # Simple keyword-based theme detection
        keywords = {
            "emotional": ["love", "heart", "tears", "cry", "emotion", "feel", "loss", "grief", "sad", "sorrow"],
            "dramatic": ["death", "betrayal", "revenge", "fight", "battle", "war", "conflict", "tension", "dramatic"],
            "comedic": ["funny", "laugh", "joke", "humor", "silly", "ridiculous", "comedy", "amusing", "hilarious"],
            "mysterious": ["mystery", "secret", "unknown", "shadow", "dark", "hidden", "reveal", "discover"],
            "energetic": ["run", "jump", "race", "fast", "quick", "speed", "action", "energy", "exciting"]
        }
        
        # Count keyword occurrences
        theme_scores = {theme: 0 for theme in keywords}
        for theme, words in keywords.items():
            for word in words:
                if re.search(r'\b' + word + r'\b', self.story.lower()):
                    theme_scores[theme] += 1
        
        # Use TextBlob for sentiment analysis
        blob = TextBlob(self.story)
        sentiment = blob.sentiment
        
        # Adjust scores based on sentiment
        if sentiment.polarity < -0.3:
            theme_scores["emotional"] += 2
            theme_scores["dramatic"] += 1
        elif sentiment.polarity > 0.3:
            theme_scores["comedic"] += 1
            theme_scores["energetic"] += 1
            
        if sentiment.subjectivity > 0.6:
            theme_scores["emotional"] += 1
            
        # Select the theme with the highest score
        max_score = max(theme_scores.values())
        if max_score > 0:
            self.theme = max(theme_scores.items(), key=lambda x: x[1])[0]
        else:
            self.theme = "neutral"  # Default theme
            
        # Select voice based on theme
        self.voice = VOICE_MAPPING.get(self.theme, "Adam")
        self.voice_id = VOICE_IDS.get(self.voice, VOICE_IDS["Adam"])
        
        print(f"[✔] Theme detected: {self.theme.capitalize()}")
        print(f"[✔] Voice selected: \"{self.voice}\" (ElevenLabs)")
    
    def generate_speech(self):
        """Generate speech using ElevenLabs API."""
        print("\nGenerating speech...")
        
        if not ELEVENLABS_API_KEY:
            print("Error: ElevenLabs API key not found. Please set the ELEVENLABS_API_KEY environment variable.")
            print("Skipping speech generation. Final video will have no audio.")
            return False
            
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": ELEVENLABS_API_KEY
            }
            
            data = {
                "text": self.story,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                self.audio_path = os.path.join(TEMP_DIR, "speech.mp3")
                with open(self.audio_path, "wb") as f:
                    f.write(response.content)
                print(f"[✔] Speech generated: {self.audio_path}")
                
                # Get word timings
                self.get_word_timings()
                return True
            else:
                print(f"Error generating speech: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error generating speech: {e}")
            return False
    
    def get_word_timings(self):
        """Get word-level timing information for the generated speech."""
        print("Generating word timings...")
        
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "xi-api-key": ELEVENLABS_API_KEY
            }
            
            data = {
                "text": self.story,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                },
                "output_format": "json_format"
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract word timings from the response
                # Note: This is a simplified version and may need adjustment based on actual API response
                if "word_timings" in result:
                    self.word_timings = result["word_timings"]
                else:
                    # Fallback: estimate word timings based on audio duration
                    self.estimate_word_timings()
            else:
                print(f"Error getting word timings: {response.status_code} - {response.text}")
                self.estimate_word_timings()
                
        except Exception as e:
            print(f"Error getting word timings: {e}")
            self.estimate_word_timings()
    
    def estimate_word_timings(self):
        """Estimate word timings based on audio duration and word count."""
        print("Estimating word timings...")
        
        if not self.audio_path or not os.path.exists(self.audio_path):
            print("Audio file not found. Cannot estimate word timings.")
            return
            
        try:
            # Load audio to get duration
            audio_clip = AudioFileClip(self.audio_path)
            total_duration = audio_clip.duration
            
            # Split story into words
            words = re.findall(r'\b\w+\b|\W+', self.story)
            word_count = len(words)
            
            # Estimate average word duration
            avg_word_duration = total_duration / word_count
            
            # Create estimated timings
            current_time = 0
            self.word_timings = []
            
            for word in words:
                word_duration = len(word) * avg_word_duration / 5  # Adjust based on word length
                if word_duration < 0.1:
                    word_duration = 0.1
                
                self.word_timings.append({
                    "word": word,
                    "start": current_time,
                    "end": current_time + word_duration
                })
                
                current_time += word_duration
                
            # Adjust to match total duration
            if current_time < total_duration:
                scale_factor = total_duration / current_time
                for timing in self.word_timings:
                    timing["start"] *= scale_factor
                    timing["end"] *= scale_factor
                    
            print(f"[✔] Estimated timings for {word_count} words")
            
        except Exception as e:
            print(f"Error estimating word timings: {e}")
    
    def select_background_video(self):
        """Select a random background video from the videos directory."""
        print("\nSelecting background video...")
        
        videos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), VIDEOS_DIR)
        video_files = [f for f in os.listdir(videos_dir) if f.endswith(('.mp4', '.mov', '.avi'))]
        
        if not video_files:
            print("No video files found in the videos directory.")
            return False
            
        selected_video = random.choice(video_files)
        self.video_path = os.path.join(videos_dir, selected_video)
        
        print(f"[✔] Selected video: {selected_video}")
        return True
    
    def create_subtitles(self):
        """Create subtitles with word highlighting based on word timings."""
        print("\nCreating subtitles...")
        
        if not self.word_timings:
            print("No word timings available. Cannot create subtitles.")
            return []
            
        # Group words into lines (max 5-7 words per line)
        lines = []
        current_line = []
        current_line_word_count = 0
        
        for word_timing in self.word_timings:
            word = word_timing["word"]
            start_time = word_timing["start"]
            end_time = word_timing["end"]
            
            current_line.append((word, start_time, end_time))
            current_line_word_count += 1
            
            # Check if we should start a new line
            if current_line_word_count >= 5 and word.strip() in ['.', ',', '!', '?', ';', ':'] or current_line_word_count >= 7:
                lines.append(current_line)
                current_line = []
                current_line_word_count = 0
                
        # Add the last line if not empty
        if current_line:
            lines.append(current_line)
            
        # Create subtitle clips for each line
        subtitle_clips = []
        
        for line in lines:
            line_text = " ".join([word[0] for word in line])
            line_start = line[0][1]  # Start time of first word
            line_end = line[-1][2]   # End time of last word
            
            # Create a clip for the entire line (background)
            line_clip = TextClip(
                line_text,
                fontsize=40,
                color='white',
                bg_color='rgba(0,0,0,0.5)',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=1,
                method='caption',
                size=(VIDEO_WIDTH * 0.9, None),
                align='center'
            ).set_position(('center', VIDEO_HEIGHT * 0.8)).set_start(line_start).set_end(line_end)
            
            subtitle_clips.append(line_clip)
            
            # Create highlighted word clips
            for word_info in line:
                word, word_start, word_end = word_info
                
                # Find the position of this word in the line
                word_index = line_text.find(word)
                if word_index >= 0:
                    # Create a highlighted version of just this word
                    highlighted_text = line_text[:word_index] + f"[{word}]" + line_text[word_index + len(word):]
                    
                    word_clip = TextClip(
                        highlighted_text,
                        fontsize=40,
                        color='white',
                        bg_color='rgba(0,0,0,0.5)',
                        font='Arial-Bold',
                        stroke_color='black',
                        stroke_width=1,
                        method='caption',
                        size=(VIDEO_WIDTH * 0.9, None),
                        align='center',
                        highlight_color='yellow'
                    ).set_position(('center', VIDEO_HEIGHT * 0.8)).set_start(word_start).set_end(word_end)
                    
                    subtitle_clips.append(word_clip)
        
        print(f"[✔] Created {len(subtitle_clips)} subtitle clips")
        return subtitle_clips
    
    def create_video(self):
        """Create the final video with background, audio, and subtitles."""
        print("\nCreating final video...")
        
        if not self.video_path or not os.path.exists(self.video_path):
            print("Background video not found. Cannot create final video.")
            return False
            
        try:
            # Load background video
            background = VideoFileClip(self.video_path)
            
            # Determine video duration based on audio
            if self.audio_path and os.path.exists(self.audio_path):
                audio = AudioFileClip(self.audio_path)
                duration = audio.duration
            else:
                duration = 60  # Default duration: 60 seconds
                audio = None
                
            # Crop and resize background video to vertical format
            bg_height, bg_width = background.size
            
            if bg_width / bg_height > VIDEO_WIDTH / VIDEO_HEIGHT:
                # Video is wider than our target aspect ratio
                new_width = int(bg_height * VIDEO_WIDTH / VIDEO_HEIGHT)
                x_center = bg_width // 2
                x1 = max(0, x_center - new_width // 2)
                x2 = min(bg_width, x_center + new_width // 2)
                background = background.crop(x1=x1, y1=0, x2=x2, y2=bg_height)
            else:
                # Video is taller than our target aspect ratio
                new_height = int(bg_width * VIDEO_HEIGHT / VIDEO_WIDTH)
                y_center = bg_height // 2
                y1 = max(0, y_center - new_height // 2)
                y2 = min(bg_height, y_center + new_height // 2)
                background = background.crop(x1=0, y1=y1, x2=bg_width, y2=y2)
                
            # Resize to target dimensions
            background = background.resize((VIDEO_WIDTH, VIDEO_HEIGHT))
            
            # Loop the background video if it's shorter than the audio
            if background.duration < duration:
                background = background.loop(duration=duration)
            else:
                background = background.subclip(0, duration)
                
            # Create subtitle clips
            subtitle_clips = self.create_subtitles()
            
            # Combine everything
            clips = [background] + subtitle_clips
            final_video = CompositeVideoClip(clips)
            
            # Add audio if available
            if audio:
                final_video = final_video.set_audio(audio)
                
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
            os.makedirs(output_dir, exist_ok=True)
            
            # Write final video
            output_path = os.path.join(output_dir, "final_output.mp4")
            final_video.write_videofile(
                output_path,
                fps=30,
                codec="libx264",
                audio_codec="aac",
                threads=4,
                preset="medium"
            )
            
            print(f"\n[✔] Video ready: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error creating video: {e}")
            return False
    
    def run(self):
        """Run the complete video creation process."""
        self.get_user_input()
        self.detect_theme()
        speech_success = self.generate_speech()
        video_success = self.select_background_video()
        
        if video_success:
            self.create_video()
        else:
            print("Cannot create video without a background video.")

def main():
    """Main function to run the AI Video Creator."""
    print("=" * 50)
    print("AI Video Creator")
    print("Create engaging videos with AI narration and dynamic subtitles")
    print("=" * 50)
    
    creator = AIVideoCreator()
    creator.run()

if __name__ == "__main__":
    main()