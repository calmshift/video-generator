#!/usr/bin/env python3
"""
AI Video Creator - Production-grade tool for creating engaging videos with AI narration and dynamic subtitles.

This tool allows users to create vertical videos (1080x1920) with:
- Manual or AI-generated story narration
- ElevenLabs voice synthesis
- Background gameplay footage
- Dynamic subtitles with word highlighting
"""

import argparse
import os
import sys
import random
import json
import time
import shutil
import logging
import traceback
import signal
import re
import uuid
from pathlib import Path
import tempfile
from typing import Dict, List, Tuple, Optional, Union, Any
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_video_creator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AIVideoCreator")

# Handle dependency imports with proper error handling
REQUIRED_PACKAGES = [
    "requests", "moviepy", "numpy", "textblob", "openai", 
    "python-dotenv", "tqdm", "retry", "pydub", "elevenlabs", "pathlib"
]

def install_dependencies():
    """Install required dependencies if not already installed."""
    try:
        import importlib
        missing_packages = []
        
        for package in REQUIRED_PACKAGES:
            try:
                importlib.import_module(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.info(f"Installing missing packages: {', '.join(missing_packages)}")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            logger.info("All required packages installed successfully")
            
            # Reload modules that might have been imported before installation
            import importlib
            importlib.invalidate_caches()
    except Exception as e:
        logger.error(f"Failed to install dependencies: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

# Install dependencies if needed
install_dependencies()

# Now import the required packages
try:
    import requests
    from retry import retry
    from tqdm import tqdm
    from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
    from moviepy.video.tools.subtitles import SubtitlesClip
    import numpy as np
    from textblob import TextBlob
    import openai
    from pydub import AudioSegment
    from dotenv import load_dotenv
    import elevenlabs
    from pathlib import Path
except ImportError as e:
    logger.error(f"Failed to import required packages: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    logger.warning(f"Failed to load .env file: {e}")

# Configuration management
class Config:
    """Configuration management class with defaults and environment variable overrides."""
    
    def __init__(self):
        # Video settings
        self.video_width = int(os.getenv("VIDEO_WIDTH", "1080"))
        self.video_height = int(os.getenv("VIDEO_HEIGHT", "1920"))
        self.fps = int(os.getenv("FPS", "30"))
        self.video_codec = os.getenv("VIDEO_CODEC", "libx264")
        self.audio_codec = os.getenv("AUDIO_CODEC", "aac")
        self.video_bitrate = os.getenv("VIDEO_BITRATE", "8000k")
        self.audio_bitrate = os.getenv("AUDIO_BITRATE", "192k")
        self.preset = os.getenv("PRESET", "medium")
        self.threads = int(os.getenv("THREADS", "4"))
        
        # Directory settings
        self.videos_dir = os.getenv("VIDEOS_DIR", "videos")
        self.output_dir = os.getenv("OUTPUT_DIR", "output")
        self.temp_dir = os.getenv("TEMP_DIR", tempfile.gettempdir())
        self.output_filename = os.getenv("OUTPUT_FILENAME", "final_output.mp4")
        
        # API keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY", "")
        
        # OpenAI settings
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.story_prompt = os.getenv("STORY_PROMPT", 
            "Write a dramatic, emotional story for a 60-second video narration. "
            "Keep it concise (150-200 words) and engaging."
        )
        
        # ElevenLabs settings
        self.elevenlabs_model = os.getenv("ELEVENLABS_MODEL", "eleven_monolingual_v1")
        self.voice_stability = float(os.getenv("VOICE_STABILITY", "0.5"))
        self.voice_similarity = float(os.getenv("VOICE_SIMILARITY", "0.75"))
        
        # Subtitle settings
        self.subtitle_fontsize = int(os.getenv("SUBTITLE_FONTSIZE", "40"))
        self.subtitle_color = os.getenv("SUBTITLE_COLOR", "white")
        self.subtitle_bg_color = os.getenv("SUBTITLE_BG_COLOR", "rgba(0,0,0,0.5)")
        self.subtitle_font = os.getenv("SUBTITLE_FONT", "Arial-Bold")
        self.subtitle_position = float(os.getenv("SUBTITLE_POSITION", "0.8"))  # Percentage of screen height
        self.highlight_color = os.getenv("HIGHLIGHT_COLOR", "yellow")
        
        # Retry settings
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("RETRY_DELAY", "2"))
        
        # Voice mapping based on themes
        self.voice_mapping = {
            "emotional": "Rachel",  # Emotional, reflective
            "dramatic": "Bella",    # Intense, dramatic
            "comedic": "Elli",      # Upbeat, comedic
            "neutral": "Adam",      # Default, neutral
            "mysterious": "Antoni", # Mysterious, suspenseful
            "energetic": "Josh",    # Energetic, exciting
        }
        
        # Voice IDs for ElevenLabs
        self.voice_ids = {
            "Rachel": "21m00Tcm4TlvDq8ikWAM",
            "Bella": "EXAVITQu4vr4xnSDxMaL",
            "Elli": "MF3mGyEYCl7XYWbV9V6O",
            "Adam": "pNInz6obpgDQGcFmaJgB",
            "Antoni": "ErXwobaYiN019PkySvjV",
            "Josh": "TxGEqnHWrfWFTfGW9XjX",
        }
        
        # Theme keywords for detection
        self.theme_keywords = {
            "emotional": ["love", "heart", "tears", "cry", "emotion", "feel", "loss", "grief", "sad", "sorrow"],
            "dramatic": ["death", "betrayal", "revenge", "fight", "battle", "war", "conflict", "tension", "dramatic"],
            "comedic": ["funny", "laugh", "joke", "humor", "silly", "ridiculous", "comedy", "amusing", "hilarious"],
            "mysterious": ["mystery", "secret", "unknown", "shadow", "dark", "hidden", "reveal", "discover"],
            "energetic": ["run", "jump", "race", "fast", "quick", "speed", "action", "energy", "exciting"]
        }
        
        # Validate configuration
        self._validate()
    
    def _validate(self):
        """Validate configuration values."""
        if self.video_width <= 0 or self.video_height <= 0:
            raise ValueError("Video dimensions must be positive")
        
        if self.fps <= 0:
            raise ValueError("FPS must be positive")
        
        if self.threads <= 0:
            raise ValueError("Thread count must be positive")
        
        if self.subtitle_position < 0 or self.subtitle_position > 1:
            raise ValueError("Subtitle position must be between 0 and 1")
        
        # Create directories if they don't exist
        Path(self.videos_dir).mkdir(parents=True, exist_ok=True)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "ai_video_creator").mkdir(parents=True, exist_ok=True)

# Initialize configuration
config = Config()

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    """Handle interrupt signals gracefully."""
    logger.info("Received interrupt signal. Cleaning up and exiting...")
    cleanup_temp_files()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Utility functions
def cleanup_temp_files():
    """Clean up temporary files created during processing."""
    try:
        temp_dir = Path(config.temp_dir) / "ai_video_creator"
        if temp_dir.exists():
            logger.info(f"Cleaning up temporary files in {temp_dir}")
            shutil.rmtree(temp_dir)
    except Exception as e:
        logger.error(f"Error cleaning up temporary files: {e}")

def get_unique_filename(directory, base_name, extension):
    """Generate a unique filename to avoid overwriting existing files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return str(Path(directory) / f"{base_name}_{timestamp}_{unique_id}.{extension}")

class ProgressBar:
    """Custom progress bar for tracking operations."""
    
    def __init__(self, total, desc="Progress"):
        self.pbar = tqdm(total=total, desc=desc, unit="step")
    
    def update(self, n=1):
        self.pbar.update(n)
    
    def close(self):
        self.pbar.close()

class AIVideoCreator:
    """Main class for creating AI-narrated videos."""
    
    def __init__(self, args=None):
        """Initialize the video creator with optional command-line arguments."""
        self.config = config
        self.args = args
        self.story = ""
        self.theme = "neutral"
        self.voice = "Adam"
        self.voice_id = self.config.voice_ids["Adam"]
        self.audio_path = ""
        self.video_path = ""
        self.subtitles = []
        self.word_timings = []
        self.temp_files = []
        self.session_id = str(uuid.uuid4())[:8]
        
        # Create temp directory for this session
        self.session_temp_dir = str(Path(self.config.temp_dir) / "ai_video_creator" / self.session_id)
        Path(self.session_temp_dir).mkdir(parents=True, exist_ok=True)
        
        # Set up OpenAI API key if available
        if self.config.openai_api_key:
            openai.api_key = self.config.openai_api_key
        
        # Process command-line arguments if provided
        if args:
            self._process_args()
    
    def _process_args(self):
        """Process command-line arguments."""
        if self.args.input_file:
            try:
                with open(self.args.input_file, 'r', encoding='utf-8') as f:
                    self.story = f.read().strip()
                logger.info(f"Loaded story from file: {self.args.input_file}")
            except Exception as e:
                logger.error(f"Error reading input file: {e}")
                sys.exit(1)
        
        if self.args.story:
            self.story = self.args.story
        
        if self.args.video:
            if os.path.exists(self.args.video):
                self.video_path = self.args.video
            else:
                logger.error(f"Specified video file not found: {self.args.video}")
                sys.exit(1)
        
        if self.args.voice:
            if self.args.voice in self.config.voice_ids:
                self.voice = self.args.voice
                self.voice_id = self.config.voice_ids[self.voice]
            else:
                logger.warning(f"Unknown voice '{self.args.voice}'. Using default voice.")
        
        if self.args.output:
            self.config.output_filename = self.args.output
    
    def get_user_input(self):
        """Get the story input mode from the user."""
        # Skip if story is already provided via arguments
        if self.story:
            logger.info("Using provided story from arguments")
            return
        
        try:
            print("Select input mode:")
            print("[1] Manually enter story")
            print("[2] Auto-generate story using AI")
            
            choice = input("> ").strip()
            
            if choice == "1":
                print("\nEnter your story (press Enter twice to finish):")
                lines = []
                while True:
                    try:
                        line = input()
                        if not line and lines and not lines[-1]:
                            break
                        lines.append(line)
                    except EOFError:
                        break
                
                self.story = "\n".join(lines)
                if not self.story.strip():
                    logger.warning("Empty story provided. Using a default story.")
                    self.story = "This is a default story used because no input was provided. It will be used to demonstrate the video creation capabilities."
                
                logger.info("Story received from manual input")
            elif choice == "2":
                self.generate_ai_story()
            else:
                logger.warning(f"Invalid choice: {choice}. Defaulting to manual input.")
                self.get_user_input()
        except Exception as e:
            logger.error(f"Error getting user input: {e}")
            logger.error(traceback.format_exc())
            sys.exit(1)
    
    @retry(tries=3, delay=2, backoff=2, logger=logger)
    def generate_ai_story(self):
        """Generate a story using OpenAI's API with retry capability."""
        if not self.config.openai_api_key:
            logger.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            self.story = input("Please enter a story manually instead: ")
            return
            
        logger.info("Generating story using OpenAI API...")
        print("\nGenerating story...")
        
        try:
            response = openai.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": "You are a creative storyteller."},
                    {"role": "user", "content": self.config.story_prompt}
                ]
            )
            self.story = response.choices[0].message.content.strip()
            
            if not self.story:
                raise ValueError("Received empty story from OpenAI API")
                
            logger.info("Successfully generated story using OpenAI API")
            print(f"\n[✔] Generated story:\n{self.story}\n")
        except Exception as e:
            logger.error(f"Error generating story: {e}")
            logger.error(traceback.format_exc())
            
            # Fallback to a default story
            self.story = """In the shadow of towering skyscrapers, a homeless man named Marcus carefully unfolds a tattered photograph. 
It shows a smiling family—his family—from a time before addiction took everything. 
Each morning, he places a small origami crane beside the photo, a promise he made to his daughter. 
"One thousand cranes, and I'll come home clean," he whispers. Today marks crane number 973. 
A businessman who passes Marcus daily notices the growing collection. 
Without a word, he sits down and begins folding paper. 
Sometimes healing begins with the smallest acts of kindness from unexpected places."""
            
            logger.info("Using fallback story due to API error")
            print(f"\n[!] Using fallback story due to API error:\n{self.story}\n")
    
    def detect_theme(self):
        """Detect the theme/emotion of the story using keyword analysis and sentiment."""
        logger.info("Analyzing story theme...")
        print("\nAnalyzing story theme...")
        
        try:
            # Count keyword occurrences
            theme_scores = {theme: 0 for theme in self.config.theme_keywords}
            for theme, words in self.config.theme_keywords.items():
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
            self.voice = self.config.voice_mapping.get(self.theme, "Adam")
            self.voice_id = self.config.voice_ids.get(self.voice, self.config.voice_ids["Adam"])
            
            logger.info(f"Theme detected: {self.theme.capitalize()}, Voice selected: {self.voice}")
            print(f"[✔] Theme detected: {self.theme.capitalize()}")
            print(f"[✔] Voice selected: \"{self.voice}\" (ElevenLabs)")
        except Exception as e:
            logger.error(f"Error detecting theme: {e}")
            logger.error(traceback.format_exc())
            
            # Fallback to default theme and voice
            self.theme = "neutral"
            self.voice = "Adam"
            self.voice_id = self.config.voice_ids["Adam"]
            
            logger.info("Using fallback theme and voice due to error")
            print(f"[!] Using fallback theme: {self.theme.capitalize()}")
            print(f"[!] Using fallback voice: \"{self.voice}\" (ElevenLabs)")
    
    @retry(tries=3, delay=2, backoff=2, logger=logger)
    def generate_speech(self):
        """Generate speech using ElevenLabs API with retry capability."""
        logger.info("Generating speech using ElevenLabs API...")
        print("\nGenerating speech...")
        
        if not self.config.elevenlabs_api_key:
            logger.error("ElevenLabs API key not found. Please set the ELEVENLABS_API_KEY environment variable.")
            print("Error: ElevenLabs API key not found. Please set the ELEVENLABS_API_KEY environment variable.")
            print("Skipping speech generation. Final video will have no audio.")
            return False
            
        try:
            # Set the API key for ElevenLabs
            elevenlabs.set_api_key(self.config.elevenlabs_api_key)
            
            # Create the audio path
            self.audio_path = os.path.join(self.session_temp_dir, f"speech_{self.session_id}.mp3")
            
            # Generate speech using the ElevenLabs package
            audio = elevenlabs.generate(
                text=self.story,
                voice=self.voice_id,
                model=self.config.elevenlabs_model,
                output_format="mp3",
                stability=self.config.voice_stability,
                similarity_boost=self.config.voice_similarity
            )
            
            # Save the audio to a file
            with open(self.audio_path, "wb") as f:
                f.write(audio)
            
            self.temp_files.append(self.audio_path)
            logger.info(f"Speech generated successfully: {self.audio_path}")
            print(f"[✔] Speech generated: {self.audio_path}")
            
            # Get word timings
            self.get_word_timings()
            return True
                
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            logger.error(traceback.format_exc())
            print(f"Error generating speech: {e}")
            
            # Try to use a different voice if this one failed
            if self.voice != "Adam":
                logger.info("Trying fallback voice 'Adam'")
                print("Trying fallback voice 'Adam'...")
                self.voice = "Adam"
                self.voice_id = self.config.voice_ids["Adam"]
                return self.generate_speech()
            
            return False
    
    @retry(tries=3, delay=2, backoff=2, logger=logger)
    def get_word_timings(self):
        """Get word-level timing information for the generated speech with retry capability."""
        logger.info("Generating word timings...")
        print("Generating word timings...")
        
        try:
            # Try to get word timings using the ElevenLabs API
            elevenlabs.set_api_key(self.config.elevenlabs_api_key)
            
            # Generate speech with detailed metadata to get word timings
            generation_response = elevenlabs.generate(
                text=self.story,
                voice=self.voice_id,
                model=self.config.elevenlabs_model,
                output_format="json",
                stability=self.config.voice_stability,
                similarity_boost=self.config.voice_similarity
            )
            
            # Parse the JSON response
            if isinstance(generation_response, dict) and "word_timings" in generation_response:
                self.word_timings = generation_response["word_timings"]
                logger.info(f"Retrieved {len(self.word_timings)} word timings from API")
            else:
                # Fallback: estimate word timings based on audio duration
                logger.warning("Word timings not found in API response. Estimating timings.")
                self.estimate_word_timings()
                
        except Exception as e:
            logger.error(f"Error getting word timings: {e}")
            logger.error(traceback.format_exc())
            print(f"Error getting word timings: {e}")
            self.estimate_word_timings()
    
    def estimate_word_timings(self):
        """Estimate word timings based on audio duration and word count."""
        logger.info("Estimating word timings based on audio duration...")
        print("Estimating word timings...")
        
        if not self.audio_path or not os.path.exists(self.audio_path):
            logger.error("Audio file not found. Cannot estimate word timings.")
            print("Audio file not found. Cannot estimate word timings.")
            return
            
        try:
            # Load audio to get duration
            audio_clip = AudioFileClip(self.audio_path)
            total_duration = audio_clip.duration
            
            # Split story into words
            words = re.findall(r'\b\w+\b|\W+', self.story)
            word_count = len(words)
            
            if word_count == 0:
                logger.error("No words found in story. Cannot estimate timings.")
                return
            
            # Estimate average word duration
            avg_word_duration = total_duration / word_count
            
            # Create estimated timings
            current_time = 0
            self.word_timings = []
            
            for word in words:
                # Adjust duration based on word length
                word_duration = len(word) * avg_word_duration / 5
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
                    
            logger.info(f"Estimated timings for {word_count} words")
            print(f"[✔] Estimated timings for {word_count} words")
            
        except Exception as e:
            logger.error(f"Error estimating word timings: {e}")
            logger.error(traceback.format_exc())
            print(f"Error estimating word timings: {e}")
    
    def select_background_video(self):
        """Select a random background video from the videos directory."""
        # Skip if video path is already provided via arguments
        if self.video_path and os.path.exists(self.video_path):
            logger.info(f"Using provided video: {self.video_path}")
            return True
            
        logger.info("Selecting background video...")
        print("\nSelecting background video...")
        
        try:
            # Use Path for cross-platform path handling
            videos_dir = Path(self.config.videos_dir).resolve()
            
            # Get all video files with cross-platform compatibility
            video_files = []
            for ext in ['.mp4', '.mov', '.avi']:
                video_files.extend(list(videos_dir.glob(f'*{ext}')))
                video_files.extend(list(videos_dir.glob(f'*{ext.upper()}')))
            
            if not video_files:
                logger.error(f"No video files found in {videos_dir}")
                print(f"No video files found in {videos_dir}")
                return False
                
            # Select a random video
            selected_video = random.choice(video_files)
            self.video_path = str(selected_video)
            
            # Verify the video file is valid
            try:
                video = VideoFileClip(self.video_path)
                video.close()
            except Exception as e:
                logger.error(f"Selected video is invalid: {e}")
                print(f"Selected video is invalid: {e}")
                
                # Try another video if available
                remaining_videos = [v for v in video_files if v != selected_video]
                if remaining_videos:
                    selected_video = random.choice(remaining_videos)
                    self.video_path = str(selected_video)
                    logger.info(f"Trying alternative video: {selected_video.name}")
                else:
                    return False
            
            logger.info(f"Selected video: {selected_video.name}")
            print(f"[✔] Selected video: {selected_video.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error selecting background video: {e}")
            logger.error(traceback.format_exc())
            print(f"Error selecting background video: {e}")
            return False
    
    def create_subtitles(self):
        """Create subtitles with word highlighting based on word timings."""
        logger.info("Creating subtitles with word highlighting...")
        print("\nCreating subtitles...")
        
        if not self.word_timings:
            logger.error("No word timings available. Cannot create subtitles.")
            print("No word timings available. Cannot create subtitles.")
            return []
            
        try:
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
                try:
                    line_clip = TextClip(
                        line_text,
                        fontsize=self.config.subtitle_fontsize,
                        color=self.config.subtitle_color,
                        bg_color=self.config.subtitle_bg_color,
                        font=self.config.subtitle_font,
                        stroke_color='black',
                        stroke_width=1,
                        method='caption',
                        size=(self.config.video_width * 0.9, None),
                        align='center'
                    ).set_position(('center', self.config.video_height * self.config.subtitle_position)).set_start(line_start).set_end(line_end)
                    
                    subtitle_clips.append(line_clip)
                except Exception as e:
                    logger.error(f"Error creating line clip: {e}")
                    continue
                
                # Create highlighted word clips
                for word_info in line:
                    word, word_start, word_end = word_info
                    
                    # Find the position of this word in the line
                    word_index = line_text.find(word)
                    if word_index >= 0:
                        # Create a highlighted version of just this word
                        highlighted_text = line_text[:word_index] + f"[{word}]" + line_text[word_index + len(word):]
                        
                        try:
                            word_clip = TextClip(
                                highlighted_text,
                                fontsize=self.config.subtitle_fontsize,
                                color=self.config.subtitle_color,
                                bg_color=self.config.subtitle_bg_color,
                                font=self.config.subtitle_font,
                                stroke_color='black',
                                stroke_width=1,
                                method='caption',
                                size=(self.config.video_width * 0.9, None),
                                align='center',
                                highlight_color=self.config.highlight_color
                            ).set_position(('center', self.config.video_height * self.config.subtitle_position)).set_start(word_start).set_end(word_end)
                            
                            subtitle_clips.append(word_clip)
                        except Exception as e:
                            logger.error(f"Error creating word highlight clip: {e}")
                            continue
            
            logger.info(f"Created {len(subtitle_clips)} subtitle clips")
            print(f"[✔] Created {len(subtitle_clips)} subtitle clips")
            return subtitle_clips
            
        except Exception as e:
            logger.error(f"Error creating subtitles: {e}")
            logger.error(traceback.format_exc())
            print(f"Error creating subtitles: {e}")
            return []
    
    def create_video(self):
        """Create the final video with background, audio, and subtitles."""
        logger.info("Creating final video...")
        print("\nCreating final video...")
        
        if not self.video_path or not os.path.exists(self.video_path):
            logger.error("Background video not found. Cannot create final video.")
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
            
            if bg_width / bg_height > self.config.video_width / self.config.video_height:
                # Video is wider than our target aspect ratio
                new_width = int(bg_height * self.config.video_width / self.config.video_height)
                x_center = bg_width // 2
                x1 = max(0, x_center - new_width // 2)
                x2 = min(bg_width, x_center + new_width // 2)
                background = background.crop(x1=x1, y1=0, x2=x2, y2=bg_height)
            else:
                # Video is taller than our target aspect ratio
                new_height = int(bg_width * self.config.video_height / self.config.video_width)
                y_center = bg_height // 2
                y1 = max(0, y_center - new_height // 2)
                y2 = min(bg_height, y_center + new_height // 2)
                background = background.crop(x1=0, y1=y1, x2=bg_width, y2=y2)
                
            # Resize to target dimensions
            background = background.resize((self.config.video_width, self.config.video_height))
            
            # Loop the background video if it's shorter than the audio
            if background.duration < duration:
                # Create a list of clips to concatenate
                num_loops = int(np.ceil(duration / background.duration))
                background_clips = [background] * num_loops
                background = concatenate_videoclips(background_clips)
            
            # Trim to match audio duration
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
            output_dir = Path(self.config.output_dir).resolve()
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate output filename
            if self.args and self.args.output:
                output_path = str(output_dir / self.args.output)
            else:
                # Use default name with timestamp to avoid overwriting
                output_path = get_unique_filename(str(output_dir), "ai_video", "mp4")
            
            # Write final video with progress bar
            print(f"Rendering final video to {output_path}...")
            progress_callback = lambda t, remaining: print(f"Rendering: {t:.1f}s / {duration:.1f}s ({int(t/duration*100)}%)", end="\r")
            
            final_video.write_videofile(
                output_path,
                fps=self.config.fps,
                codec=self.config.video_codec,
                audio_codec=self.config.audio_codec,
                bitrate=self.config.video_bitrate,
                audio_bitrate=self.config.audio_bitrate,
                threads=self.config.threads,
                preset=self.config.preset,
                logger=None,  # Disable moviepy's logger
                progress_bar=True,
                verbose=False
            )
            
            logger.info(f"Video created successfully: {output_path}")
            print(f"\n[✔] Video ready: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            logger.error(traceback.format_exc())
            print(f"Error creating video: {e}")
            return False
        finally:
            # Clean up any open clips
            try:
                if 'background' in locals() and background:
                    background.close()
                if 'audio' in locals() and audio:
                    audio.close()
                if 'final_video' in locals() and final_video:
                    final_video.close()
            except Exception as e:
                logger.error(f"Error closing clips: {e}")
    
    def run(self):
        """Run the complete video creation process with error handling."""
        try:
            # Step 1: Get story input
            if not self.story:
                self.get_user_input()
            
            if not self.story:
                logger.error("No story provided. Cannot proceed.")
                print("Error: No story provided. Cannot proceed.")
                return False
            
            # Step 2: Detect theme and select voice
            self.detect_theme()
            
            # Step 3: Generate speech
            speech_success = self.generate_speech()
            
            # Step 4: Select background video
            video_success = self.select_background_video()
            
            if not video_success:
                logger.error("Failed to select a valid background video.")
                print("Error: Failed to select a valid background video.")
                return False
            
            # Step 5: Create final video
            video_created = self.create_video()
            
            # Step 6: Clean up temporary files
            self.cleanup()
            
            return video_created
        except Exception as e:
            logger.error(f"Unexpected error in video creation process: {e}")
            logger.error(traceback.format_exc())
            print(f"Unexpected error in video creation process: {e}")
            self.cleanup()
            return False
    
    def cleanup(self):
        """Clean up temporary files created during processing."""
        try:
            for file_path in self.temp_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Remove session temp directory if it exists and is empty
            if os.path.exists(self.session_temp_dir) and not os.listdir(self.session_temp_dir):
                os.rmdir(self.session_temp_dir)
                
            logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {e}")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="AI Video Creator - Create engaging videos with AI narration and dynamic subtitles")
    
    # Input options
    input_group = parser.add_argument_group("Input Options")
    input_group.add_argument("--story", type=str, help="Provide story text directly")
    input_group.add_argument("--input-file", type=str, help="Path to a text file containing the story")
    input_group.add_argument("--video", type=str, help="Path to a specific background video to use")
    input_group.add_argument("--voice", type=str, choices=list(config.voice_ids.keys()), help="Specific voice to use")
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("--output", type=str, help="Output filename (default: auto-generated)")
    output_group.add_argument("--width", type=int, help=f"Video width (default: {config.video_width})")
    output_group.add_argument("--height", type=int, help=f"Video height (default: {config.video_height})")
    output_group.add_argument("--fps", type=int, help=f"Frames per second (default: {config.fps})")
    
    # Other options
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--version", action="version", version="AI Video Creator v1.0.0")
    
    return parser.parse_args()

def main():
    """Main function to run the AI Video Creator."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set up logging level
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Update config from arguments
    if args.width:
        config.video_width = args.width
    if args.height:
        config.video_height = args.height
    if args.fps:
        config.fps = args.fps
    
    # Print banner
    print("=" * 50)
    print("AI Video Creator")
    print("Create engaging videos with AI narration and dynamic subtitles")
    print("=" * 50)
    
    # Create and run the video creator
    creator = AIVideoCreator(args)
    success = creator.run()
    
    # Final cleanup
    cleanup_temp_files()
    
    if not success:
        logger.error("Video creation process failed")
        sys.exit(1)
    
    logger.info("Video creation process completed successfully")

if __name__ == "__main__":
    main()