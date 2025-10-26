#!/bin/bash
# Quick deployment script for GateFlow Dashboard

set -e

echo "🚀 GateFlow Dashboard - Quick Deploy"
echo "===================================="
echo ""

# Check if we're in the deploy directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Must run from the deploy/ directory"
    echo "   Usage: cd deploy && ./quick-deploy.sh"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Ask which mode to deploy
echo "Select deployment mode:"
echo "  1) Development (Streamlit only)"
echo "  2) Production (Streamlit + Nginx)"
read -p "Enter choice (1 or 2): " mode

if [ "$mode" = "1" ]; then
    echo ""
    echo "🔨 Building and starting development environment..."
    docker compose up --build -d
    echo ""
    echo "✅ Development deployment complete!"
    echo "   Access at: http://localhost:8501"
elif [ "$mode" = "2" ]; then
    echo ""
    echo "🔨 Building and starting production environment..."
    docker compose -f docker-compose.prod.yml up --build -d
    echo ""
    echo "✅ Production deployment complete!"
    echo "   Access at: http://smart-gate.tech (or your configured domain)"
    echo "   Note: Make sure your domain DNS is configured"
else
    echo "❌ Invalid choice"
    exit 1
fi

echo ""
echo "📊 Container status:"
docker compose ps

echo ""
echo "💡 Useful commands:"
echo "   View logs:      docker compose logs -f"
echo "   Stop services:  docker compose down"
echo "   Restart:        docker compose restart"
echo "   Health check:   curl http://localhost:8501/_stcore/health"
