FROM openjdk:11-jre-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    wget \
    unzip \
    python3 \
    python3-pip \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Download and setup Audiveris
RUN wget -q https://github.com/Audiveris/audiveris/releases/download/5.3.1/audiveris-5.3.1.zip && \
    unzip audiveris-5.3.1.zip && \
    rm audiveris-5.3.1.zip && \
    mv audiveris-5.3.1 audiveris

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for input/output
RUN mkdir -p /app/input /app/output /app/temp

# Set environment variables
ENV AUDIVERIS_HOME=/app/audiveris
ENV JAVA_OPTS="-Xmx2g"

# Expose port for web interface (if we add one later)
EXPOSE 8000

# Default command
CMD ["python3", "process_music.py"]