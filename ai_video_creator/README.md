# AI Video Creator

A production-grade CLI tool that creates engaging vertical videos with AI narration, dynamic subtitles, and background gameplay footage. Works on Windows, macOS, and Linux.

## Features

- **Dual Input Modes**:
  - Manual text input (write your own story)
  - AI-generated story (using OpenAI API)

- **Smart Voice Selection**:
  - Analyzes the tone/theme of the story
  - Selects an appropriate ElevenLabs voice (emotional, dramatic, comedic, etc.)

- **Dynamic Video Creation**:
  - Generates voiceover narration via ElevenLabs API
  - Selects random background gameplay video from local folder
  - Creates word-by-word highlighted subtitles
  - Outputs a vertical (1080x1920) video ready for social media

- **Cross-Platform Support**:
  - Works on Windows, macOS, and Linux
  - Platform-specific installation scripts
  - Path handling compatible with all operating systems

- **Production-Grade Features**:
  - Comprehensive error handling and recovery
  - Automatic dependency management
  - Configurable via environment variables or command-line arguments
  - Detailed logging for debugging and monitoring
  - Automatic retry for API calls
  - Graceful handling of interruptions
  - Temporary file cleanup
  - Progress tracking during video rendering
  - Unique output filenames to prevent overwrites

## Installation

### Manual Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ai-video-creator.git
   cd ai-video-creator
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up API keys:
   Create a `.env` file in the project root with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ```

4. Add background videos:
   Place your gameplay videos in the `videos/` directory.

### Automated Installation

#### On Linux/macOS:
```
./install.sh
```

#### On Windows:
```
install.bat
```

These scripts will:
1. Check system requirements
2. Install dependencies
3. Set up the project in a user-accessible location
4. Create shortcuts for easy access

## Usage

### Quick Start

#### On Linux/macOS:
Use the provided shell script to set up and run the tool:
```
./run.sh
```

#### On Windows:
Use the provided batch file to set up and run the tool:
```
run.bat
```

These scripts will:
1. Create a virtual environment
2. Install dependencies
3. Set up the .env file if needed
4. Run the AI Video Creator

### Command-Line Arguments

The tool supports various command-line arguments for automation:

```
python ai_video_creator.py --help
```

Common usage patterns:

```bash
# Use a specific story from a file
python ai_video_creator.py --input-file story.txt

# Provide story directly via command line
python ai_video_creator.py --story "Your story text here"

# Use a specific background video
python ai_video_creator.py --video /path/to/video.mp4

# Select a specific voice
python ai_video_creator.py --voice Rachel

# Specify output filename
python ai_video_creator.py --output my_video.mp4

# Change video dimensions
python ai_video_creator.py --width 720 --height 1280
```

### Interactive Mode

Run the script without arguments for interactive mode:
```
python ai_video_creator.py
```

Follow the prompts to:
1. Choose input mode (manual or AI-generated)
2. Enter or generate a story
3. Wait for the video to be created

The final video will be saved in the `output/` directory.

### Demo Mode

To see a demonstration without requiring API keys:
```
python demo.py
```

This will simulate the process without making actual API calls or generating a real video.

## Example CLI Flow

```
$ python ai_video_creator.py
==================================================
AI Video Creator
Create engaging videos with AI narration and dynamic subtitles
==================================================
Select input mode:
[1] Manually enter story
[2] Auto-generate story using AI
> 2

Generating story...
[✔] Generated story:
In the shadow of towering skyscrapers, a homeless man named Marcus carefully unfolds a tattered photograph. It shows a smiling family—his family—from a time before addiction took everything. Each morning, he places a small origami crane beside the photo, a promise he made to his daughter. "One thousand cranes, and I'll come home clean," he whispers. Today marks crane number 973. A businessman who passes Marcus daily notices the growing collection. Without a word, he sits down and begins folding paper. Sometimes healing begins with the smallest acts of kindness from unexpected places.

Analyzing story theme...
[✔] Theme detected: Emotional
[✔] Voice selected: "Rachel" (ElevenLabs)

Generating speech...
[✔] Speech generated: /tmp/ai_video_creator/a1b2c3d4/speech_a1b2c3d4.mp3
Generating word timings...
[✔] Estimated timings for 127 words

Selecting background video...
[✔] Selected video: cityscape_night.mp4

Creating final video...
[✔] Created 42 subtitle clips
Rendering: 60.0s / 60.0s (100%)

[✔] Video ready: /workspace/ai_video_creator/output/ai_video_20250604_123456_a1b2c3d4.mp4
```

## Configuration

All aspects of the video creator can be configured via environment variables or the `.env` file:

### Video Settings
```
VIDEO_WIDTH=1080
VIDEO_HEIGHT=1920
FPS=30
VIDEO_CODEC=libx264
AUDIO_CODEC=aac
VIDEO_BITRATE=8000k
AUDIO_BITRATE=192k
PRESET=medium
THREADS=4
```

### Directory Settings
```
VIDEOS_DIR=videos
OUTPUT_DIR=output
TEMP_DIR=/tmp
OUTPUT_FILENAME=final_output.mp4
```

### API Settings
```
OPENAI_MODEL=gpt-3.5-turbo
STORY_PROMPT=Write a dramatic, emotional story for a 60-second video narration.
ELEVENLABS_MODEL=eleven_monolingual_v1
VOICE_STABILITY=0.5
VOICE_SIMILARITY=0.75
```

### Subtitle Settings
```
SUBTITLE_FONTSIZE=40
SUBTITLE_COLOR=white
SUBTITLE_BG_COLOR=rgba(0,0,0,0.5)
SUBTITLE_FONT=Arial-Bold
SUBTITLE_POSITION=0.8
HIGHLIGHT_COLOR=yellow
```

## Error Handling

The tool includes robust error handling:

- **API Failures**: Automatically retries failed API calls with exponential backoff
- **Missing Dependencies**: Automatically installs required packages
- **Invalid Inputs**: Provides clear error messages and fallbacks
- **Interruptions**: Gracefully handles Ctrl+C and other interruptions
- **Logging**: Detailed logs saved to `ai_video_creator.log`

## Requirements

- Python 3.8+
- OpenAI API key (for AI story generation)
- ElevenLabs API key (for voice synthesis)
- Background videos in MP4 format
- FFmpeg (installed automatically on most systems)

## Dependencies

- moviepy
- requests
- numpy
- textblob
- openai
- python-dotenv
- tqdm
- retry
- pydub
- elevenlabs
- pathlib

## Platform-Specific Notes

### Windows
- The Windows batch files (`run.bat` and `install.bat`) provide easy setup and execution
- FFmpeg is automatically downloaded and installed if missing
- Desktop shortcuts are created during installation

### macOS/Linux
- The shell scripts (`run.sh` and `install.sh`) provide easy setup and execution
- FFmpeg can be installed via package managers if missing (e.g., `brew install ffmpeg` on macOS)
- System-wide installation is available via the install script

## License

MIT