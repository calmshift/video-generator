#!/usr/bin/env python3
"""
Test script for AI Video Creator.
This script runs basic tests to verify the functionality of the AI Video Creator.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path to import ai_video_creator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the AIVideoCreator class
try:
    from ai_video_creator import AIVideoCreator, Config, cleanup_temp_files
except ImportError as e:
    print(f"Error importing AI Video Creator: {e}")
    sys.exit(1)

class TestAIVideoCreator(unittest.TestCase):
    """Test cases for AI Video Creator."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.videos_dir = os.path.join(self.test_dir, "videos")
        self.output_dir = os.path.join(self.test_dir, "output")
        
        # Create directories
        os.makedirs(self.videos_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create a dummy video file
        self.video_path = os.path.join(self.videos_dir, "test_video.mp4")
        Path(self.video_path).touch()
        
        # Create a test story
        self.test_story = "This is a test story for the AI Video Creator."
        
        # Create a mock args object
        class MockArgs:
            def __init__(self):
                self.story = self.test_story
                self.input_file = None
                self.video = self.video_path
                self.voice = "Adam"
                self.output = "test_output.mp4"
                self.width = None
                self.height = None
                self.fps = None
                self.debug = False
        
        self.args = MockArgs()
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_config_initialization(self):
        """Test that Config class initializes correctly."""
        config = Config()
        self.assertEqual(config.video_width, 1080)
        self.assertEqual(config.video_height, 1920)
        self.assertEqual(config.fps, 30)
        self.assertEqual(config.preset, "medium")
        self.assertTrue(isinstance(config.voice_mapping, dict))
        self.assertTrue(isinstance(config.voice_ids, dict))
    
    def test_creator_initialization(self):
        """Test that AIVideoCreator initializes correctly."""
        creator = AIVideoCreator()
        self.assertEqual(creator.theme, "neutral")
        self.assertEqual(creator.voice, "Adam")
        self.assertTrue(hasattr(creator, "session_id"))
        self.assertTrue(hasattr(creator, "config"))
    
    def test_theme_detection(self):
        """Test theme detection functionality."""
        creator = AIVideoCreator()
        
        # Test emotional theme
        creator.story = "I felt tears in my eyes as I remembered the loss of my loved one."
        creator.detect_theme()
        self.assertEqual(creator.theme, "emotional")
        
        # Test dramatic theme
        creator.story = "The battle raged on as the conflict between the two armies intensified."
        creator.detect_theme()
        self.assertEqual(creator.theme, "dramatic")
        
        # Test comedic theme
        creator.story = "It was a hilarious and funny situation that made everyone laugh."
        creator.detect_theme()
        self.assertEqual(creator.theme, "comedic")
    
    def test_word_timing_estimation(self):
        """Test word timing estimation."""
        creator = AIVideoCreator()
        creator.story = "This is a test story with ten words total."
        
        # Create a mock audio file
        audio_path = os.path.join(self.test_dir, "test_audio.mp3")
        Path(audio_path).touch()
        creator.audio_path = audio_path
        
        # Mock the AudioFileClip class
        class MockAudioClip:
            def __init__(self, path):
                self.duration = 5.0  # 5 seconds
            
            def close(self):
                pass
        
        # Save the original AudioFileClip
        from moviepy.editor import AudioFileClip as OriginalAudioFileClip
        
        # Replace with mock
        from moviepy.editor import AudioFileClip
        AudioFileClip = MockAudioClip
        
        # Run the estimation
        creator.estimate_word_timings()
        
        # Restore original
        from moviepy.editor import AudioFileClip
        AudioFileClip = OriginalAudioFileClip
        
        # Check results
        self.assertTrue(len(creator.word_timings) > 0)
        self.assertEqual(len(creator.word_timings), 10)  # 10 words
        
        # Check timing distribution
        total_duration = creator.word_timings[-1]["end"]
        self.assertAlmostEqual(total_duration, 5.0, delta=0.1)
    
    def test_argument_processing(self):
        """Test command-line argument processing."""
        creator = AIVideoCreator(self.args)
        
        # Check that arguments were processed correctly
        self.assertEqual(creator.story, self.test_story)
        self.assertEqual(creator.video_path, self.video_path)
        self.assertEqual(creator.voice, "Adam")
        self.assertEqual(creator.config.output_filename, "test_output.mp4")

if __name__ == "__main__":
    unittest.main()