# AI Video Creator

A CLI tool that creates engaging vertical videos with AI narration, dynamic subtitles, and background gameplay footage.

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

## Installation

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

## Usage

### Quick Start

Use the provided shell script to set up and run the tool:
```
./run.sh
```

This script will:
1. Create a virtual environment
2. Install dependencies
3. Set up the .env file if needed
4. Run the AI Video Creator

### Manual Execution

Alternatively, run the script directly:
```
python ai_video_creator.py
```

Follow the prompts to:
1. Choose input mode (manual or AI-generated)
2. Enter or generate a story
3. Wait for the video to be created

The final video will be saved as `output/final_output.mp4`.

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
[✔] Speech generated: /tmp/speech.mp3
Generating word timings...
[✔] Estimated timings for 127 words

Selecting background video...
[✔] Selected video: cityscape_night.mp4

Creating final video...
[✔] Created 42 subtitle clips

[✔] Video ready: /workspace/ai_video_creator/output/final_output.mp4
```

## Requirements

- Python 3.8+
- OpenAI API key (for AI story generation)
- ElevenLabs API key (for voice synthesis)
- Background videos in MP4 format

## Dependencies

- moviepy
- requests
- numpy
- textblob
- openai
- python-dotenv

## Customization

- Add more background videos to the `videos/` directory
- Modify the `VOICE_MAPPING` dictionary to change theme-to-voice mapping
- Adjust video dimensions in the constants section

## License

MIT