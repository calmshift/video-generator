# Docker Usage Guide for AI Video Creator

This guide explains how to use AI Video Creator with Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system (optional, but recommended)

## Quick Start with Docker Compose

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-video-creator.git
   cd ai-video-creator
   ```

2. Create a `.env` file with your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. Add your background videos to the `videos/` directory.

4. Run the container:
   ```bash
   docker-compose up
   ```

5. For interactive mode:
   ```bash
   docker-compose run ai-video-creator
   ```

6. With command-line arguments:
   ```bash
   docker-compose run ai-video-creator --story "Your story text here"
   ```

## Manual Docker Setup

If you prefer not to use Docker Compose:

1. Build the Docker image:
   ```bash
   docker build -t ai-video-creator .
   ```

2. Run the container:
   ```bash
   docker run -it \
     -v $(pwd)/videos:/app/videos \
     -v $(pwd)/output:/app/output \
     -v $(pwd)/.env:/app/.env \
     ai-video-creator
   ```

3. With command-line arguments:
   ```bash
   docker run -it \
     -v $(pwd)/videos:/app/videos \
     -v $(pwd)/output:/app/output \
     -v $(pwd)/.env:/app/.env \
     ai-video-creator --story "Your story text here"
   ```

## Volume Mounts

- `/app/videos`: Directory containing background videos
- `/app/output`: Directory where output videos will be saved
- `/app/.env`: Environment file with API keys

## Environment Variables

You can pass environment variables directly to the container:

```bash
docker run -it \
  -v $(pwd)/videos:/app/videos \
  -v $(pwd)/output:/app/output \
  -e OPENAI_API_KEY=your_openai_api_key \
  -e ELEVENLABS_API_KEY=your_elevenlabs_api_key \
  ai-video-creator
```

## Troubleshooting

- **Permission issues**: If you encounter permission problems with the mounted volumes, you may need to adjust the permissions:
  ```bash
  chmod -R 777 videos output
  ```

- **Container crashes**: Check the logs for error messages:
  ```bash
  docker logs $(docker ps -lq)
  ```

- **Performance issues**: Adjust the number of threads used for video processing:
  ```bash
  docker run -it \
    -v $(pwd)/videos:/app/videos \
    -v $(pwd)/output:/app/output \
    -v $(pwd)/.env:/app/.env \
    -e THREADS=2 \
    ai-video-creator
  ```