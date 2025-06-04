FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p videos output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV VIDEOS_DIR=/app/videos
ENV OUTPUT_DIR=/app/output
ENV TEMP_DIR=/tmp

# Set volume mount points
VOLUME ["/app/videos", "/app/output"]

# Set entrypoint
ENTRYPOINT ["python", "ai_video_creator.py"]

# Default command (can be overridden)
CMD []