#!/usr/bin/env python3
"""
Demo script for AI Video Creator.
This script demonstrates the functionality without requiring API keys.
"""

import os
import sys
from pathlib import Path

# Ensure the script can be run from any directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Create necessary directories
os.makedirs("output", exist_ok=True)
os.makedirs("videos", exist_ok=True)

# Check if sample videos exist
if not any(Path("videos").glob("*.mp4")):
    print("No sample videos found. Creating placeholder video files...")
    Path("videos/sample_gameplay.mp4").touch()
    Path("videos/gameplay_action.mp4").touch()
    print("Created placeholder video files. In a real scenario, you would need actual video files.")

print("=" * 50)
print("AI Video Creator Demo")
print("=" * 50)
print("\nThis is a demonstration of how the AI Video Creator would work.")
print("For full functionality, you would need:")
print("1. OpenAI API key for story generation")
print("2. ElevenLabs API key for voice synthesis")
print("3. Actual video files in the 'videos' directory")
print("\nDemo flow:")

# Simulate story input
print("\nSelect input mode:")
print("[1] Manually enter story")
print("[2] Auto-generate story using AI")
print("\nFor this demo, we'll use option 1 (manual input).")

# Sample story
story = """In the shadow of towering skyscrapers, a homeless man named Marcus carefully unfolds a tattered photograph. 
It shows a smiling family—his family—from a time before addiction took everything. 
Each morning, he places a small origami crane beside the photo, a promise he made to his daughter. 
"One thousand cranes, and I'll come home clean," he whispers. Today marks crane number 973. 
A businessman who passes Marcus daily notices the growing collection. 
Without a word, he sits down and begins folding paper. 
Sometimes healing begins with the smallest acts of kindness from unexpected places."""

print(f"\n[✔] Story received:\n{story}")

# Simulate theme detection
print("\nAnalyzing story theme...")
print("[✔] Theme detected: Emotional")
print("[✔] Voice selected: \"Rachel\" (ElevenLabs)")

# Simulate speech generation
print("\nGenerating speech...")
print("[✔] In a real scenario, this would connect to ElevenLabs API")
print("[✔] Speech would be generated and saved as a file")

# Simulate background video selection
print("\nSelecting background video...")
print("[✔] Selected video: sample_gameplay.mp4")

# Simulate video creation
print("\nCreating final video...")
print("[✔] In a real scenario, this would:")
print("  - Process the background video")
print("  - Generate word-by-word subtitles")
print("  - Combine everything into a final video")

# Simulate final output
print("\n[✔] Video would be ready at: output/final_output.mp4")
print("\nTo use the actual tool with full functionality:")
print("1. Get API keys for OpenAI and ElevenLabs")
print("2. Add them to a .env file (see .env.example)")
print("3. Add real video files to the 'videos' directory")
print("4. Run: python ai_video_creator.py")

print("\nThank you for trying the AI Video Creator demo!")

# Create a dummy output file to simulate the process
with open("output/final_output.mp4", "w") as f:
    f.write("This is a placeholder file. The actual tool would create a real video here.")

print("\n[Note: A placeholder output file has been created for demonstration purposes.]")