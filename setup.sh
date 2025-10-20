#!/bin/bash

# Startup script for RAG Query Rewrite POC

set -e

echo "=========================================="
echo "RAG Query Rewrite POC - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your OPENAI_API_KEY"
    echo "Press Enter to continue after updating .env, or Ctrl+C to exit..."
    read
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p data/vector_store
mkdir -p logs
echo "✓ Directories created"

# Check if OpenAI API key is set
echo ""
echo "Checking configuration..."
if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  WARNING: OpenAI API key not set in .env file!"
    echo "Please update OPENAI_API_KEY in .env before running the application"
else
    echo "✓ Configuration looks good"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Ensure your OpenAI API key is set in .env"
echo "2. Run examples: python example.py"
echo "3. Start API server: python api.py"
echo "4. Or use Docker: docker-compose up -d"
echo ""
echo "For more information, see README.md"
echo ""
