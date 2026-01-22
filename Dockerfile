# Use Python 3.13.9 Slim (Debian-based, smaller size)
FROM python:3.13.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# - ffmpeg: Required for video processing and thumbnails
# - git: Required if installing specific python packages from GitHub
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip to ensure compatibility with 3.13 features
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# ⚠️ UPDATED COMMAND ⚠️
# Runs the web server (gunicorn) in the background AND the bot in the foreground.
# This keeps the container alive on Render.
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:8080 app:app & python3 bot.py"]
