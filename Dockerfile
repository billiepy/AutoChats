FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    mongodb-clients \
    && rm -rf /var/lib/apt/lists/*

# Install uvloop for better async performance
RUN pip install uvloop

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY migrations/ ./migrations/

# Create non-root user
RUN useradd -m -u 1000 userbot && chown -R userbot:userbot /app
USER userbot

# Expose port for health checks
EXPOSE 8080

CMD ["python", "app/main.py"]
