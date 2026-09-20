#!/usr/bin/env bash
set -euo pipefail

echo "Building Docker image with uv..."
docker build -t iiot-diagrams:latest .

echo "Generating diagrams via Docker container..."
mkdir -p output
docker run --rm -v "$(pwd)/output:/app/output" iiot-diagrams:latest

echo "Diagram generation complete. Artifacts written to ./output/"
