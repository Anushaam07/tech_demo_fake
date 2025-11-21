#!/bin/bash
# Setup script for Promptfoo integration
# This script helps you get started with Promptfoo red teaming

set -e

echo "========================================="
echo "Promptfoo Red Team Setup"
echo "========================================="
echo ""

# Check Node.js and npm
echo "[1/5] Checking Node.js and npm..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Install from: https://nodejs.org/"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "ERROR: npm is not installed"
    exit 1
fi

echo "✓ Node.js $(node --version)"
echo "✓ npm $(npm --version)"
echo ""

# Check if Promptfoo is installed
echo "[2/5] Checking Promptfoo installation..."
if ! command -v promptfoo &> /dev/null; then
    echo "Promptfoo is not installed."
    read -p "Install Promptfoo globally? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing Promptfoo..."
        npm install -g promptfoo
        echo "✓ Promptfoo installed successfully"
    else
        echo "Please install Promptfoo manually:"
        echo "  npm install -g promptfoo"
        exit 1
    fi
else
    echo "✓ Promptfoo is already installed"
fi
echo ""

# Check Python dependencies
echo "[3/5] Checking Python dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

echo "✓ Python $(python3 --version)"

# Check if requests is installed
if ! python3 -c "import requests" &> /dev/null; then
    echo "Installing Python requests library..."
    pip3 install requests
fi

if ! python3 -c "import aiohttp" &> /dev/null; then
    echo "Installing Python aiohttp library..."
    pip3 install aiohttp
fi

echo "✓ Python dependencies installed"
echo ""

# Make provider scripts executable
echo "[4/5] Setting up provider scripts..."
chmod +x ../providers/rag_provider.py
chmod +x ../providers/rag_provider_async.py
echo "✓ Provider scripts configured"
echo ""

# Check Docker and RAG API
echo "[5/5] Checking RAG API..."
if ! command -v docker &> /dev/null; then
    echo "WARNING: Docker is not installed"
    echo "Install from: https://docs.docker.com/get-docker/"
else
    echo "✓ Docker is installed"

    # Check if docker compose is available
    if docker compose version &> /dev/null; then
        echo "✓ Docker Compose is available"

        # Check if containers are running
        if docker compose ps | grep -q "Up"; then
            echo "✓ Docker containers are running"
        else
            echo "WARNING: Docker containers are not running"
            read -p "Start Docker containers? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                cd ../..
                docker compose up -d
                echo "✓ Docker containers started"
            fi
        fi
    fi
fi

# Test RAG API endpoint
echo ""
echo "Testing RAG API endpoint..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ RAG API is accessible at http://localhost:8000"
else
    echo "WARNING: RAG API is not accessible"
    echo "Make sure Docker containers are running:"
    echo "  cd ../.. && docker compose up -d"
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Ensure RAG API is running:"
echo "   docker compose up -d"
echo ""
echo "2. Upload a test document to RAG API"
echo ""
echo "3. Run your first test:"
echo "   ./run_single_test.sh pii"
echo ""
echo "4. View results:"
echo "   promptfoo view"
echo ""
echo "For more information, see:"
echo "  - configs/README.md - Configuration guide"
echo "  - ../INTEGRATION_GUIDE.md - Complete integration guide"
