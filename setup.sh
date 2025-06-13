#!/bin/bash

# Setup script for Audiveris Docker environment

echo "Setting up Audiveris Music Processing Environment..."

# Create directory structure
mkdir -p input output temp logs

echo "Directory structure created."

# Build the Docker image
echo "Building Docker image..."
docker-compose build

# Test if everything is working
echo "Testing Audiveris installation..."
docker-compose run --rm audiveris-processor java -jar /app/audiveris/lib/audiveris.jar -help

if [ $? -eq 0 ]; then
    echo "✅ Audiveris installed successfully!"
else
    echo "❌ Audiveris installation failed. Trying alternative path..."
    docker-compose run --rm audiveris-processor find /app/audiveris -name "*.jar" -type f
fi

echo ""
echo "Setup complete! To use:"
echo ""
echo "1. Place your PDF files in the 'input' directory"
echo "2. Run a single file:"
echo "   docker-compose run --rm audiveris-processor python3 process_music.py input/your_file.pdf output/"
echo ""
echo "3. Run batch processing:"
echo "   docker-compose run --rm audiveris-processor python3 process_music.py input/ output/ --batch"
echo ""
echo "4. For interactive debugging:"
echo "   docker-compose run --rm audiveris-processor /bin/bash"
echo ""
echo "Output files will appear in the 'output' directory."
