#!/bin/bash

# Setup script for Audiveris Docker environment using toprock/audiveris base image

echo "Setting up Audiveris Music Processing Environment..."
echo "Using toprock/audiveris base image..."

# Create directory structure
mkdir -p input output temp logs

echo "Directory structure created."

# Build the Docker image
echo "Building Docker image (this may take a few minutes)..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
else
    echo "❌ Docker build failed!"
    exit 1
fi

# Run diagnostic to understand the Audiveris setup
echo ""
echo "🔍 Running Audiveris diagnostic..."
docker-compose run --rm audiveris-processor python3 diagnose_audiveris.py

echo ""
echo "Setup complete! To use:"
echo ""
echo "1. Place your PDF files in the 'input' directory"
echo "2. Run a single file:"
echo "   docker-compose run --rm audiveris-processor python3 musicprocessor.py input/bach-invention-01-a4.pdf output/"
echo ""
echo "3. Run batch processing:"
echo "   docker-compose run --rm audiveris-processor python3 musicprocessor.py input/ output/ --batch"
echo ""
echo "4. For interactive debugging:"
echo "   docker-compose run --rm audiveris-processor /bin/bash"
echo ""
echo "5. Run diagnostic again anytime:"
echo "   docker-compose run --rm audiveris-processor python3 diagnose_audiveris.py"
echo ""
echo "Output files will appear in the 'output' directory."