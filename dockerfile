# Use existing Audiveris Docker image as base
FROM toprock/audiveris:latest

# Install Python and additional dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for input/output
RUN mkdir -p /app/input /app/output /app/temp

# Set environment variables - use the pre-installed Audiveris
ENV JAVA_OPTS="-Xmx2g"

# Expose port for web interface (if we add one later)
EXPOSE 8000

# Default command
CMD ["python3", "process_music.py"]