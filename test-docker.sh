#!/bin/bash

# Docker Testing Script for GateFlow Dashboard
# Run this script to test your Docker setup

set -e  # Exit on error

echo "=================================="
echo "GateFlow Dashboard - Docker Test"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    exit 1
fi

echo "✓ Docker is installed"

# Check Docker daemon
if ! docker info &> /dev/null; then
    echo "❌ Cannot connect to Docker daemon"
    echo "Run: sudo usermod -aG docker $USER"
    echo "Then log out and back in"
    exit 1
fi

echo "✓ Docker daemon is running"
echo ""

# Build the image
echo "🔨 Building Docker image..."
docker build -t gateflow-dashboard:test .

if [ $? -eq 0 ]; then
    echo "✓ Image built successfully"
else
    echo "❌ Build failed"
    exit 1
fi
echo ""

# Check image size
echo "📦 Image details:"
docker images gateflow-dashboard:test
echo ""

# Test: Run container in detached mode
echo "🚀 Starting container..."
docker run -d --name gateflow-test -p 8501:8501 -v $(pwd)/assets:/app/assets gateflow-dashboard:test

# Wait for container to start
echo "⏳ Waiting for container to start (10 seconds)..."
sleep 10

# Check if container is running
if docker ps | grep -q gateflow-test; then
    echo "✓ Container is running"
else
    echo "❌ Container failed to start"
    echo "Logs:"
    docker logs gateflow-test
    docker rm -f gateflow-test 2>/dev/null
    exit 1
fi
echo ""

# Test health endpoint
echo "🏥 Testing health endpoint..."
if curl -f http://localhost:8501/_stcore/health 2>/dev/null; then
    echo ""
    echo "✓ Health check passed"
else
    echo "❌ Health check failed"
fi
echo ""

# Show container logs
echo "📋 Container logs (last 20 lines):"
docker logs --tail 20 gateflow-test
echo ""

# Show container stats
echo "📊 Container stats:"
docker stats --no-stream gateflow-test
echo ""

# Test web interface
echo "🌐 Testing web interface..."
echo "Opening http://localhost:8501 in your browser..."
echo ""

# Instructions
echo "=================================="
echo "Manual Testing Steps:"
echo "=================================="
echo "1. Open browser: http://localhost:8501"
echo "2. Test the login functionality"
echo "3. Test the dashboard features"
echo "4. Check for any errors in console"
echo ""
echo "Commands:"
echo "  View logs:    docker logs -f gateflow-test"
echo "  Stop:         docker stop gateflow-test"
echo "  Remove:       docker rm gateflow-test"
echo "  Clean up:     docker rmi gateflow-dashboard:test"
echo ""
echo "To stop and remove the test container, run:"
echo "  docker stop gateflow-test && docker rm gateflow-test"
echo "=================================="
