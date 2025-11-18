#!/bin/bash

# Quick start script for ICP Analysis Dashboard

echo "🎯 ICP Analysis Dashboard - Quick Start"
echo "========================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "📝 Creating .env from template..."
    if [ -f .env.template ]; then
        cp .env.template .env
        echo "✅ Created .env file. Please edit it with your credentials before running."
        echo ""
        echo "Required configuration:"
        echo "  - Database connection (PostgreSQL)"
        echo "  - OpenAI API key (for Phase 3)"
        echo ""
        exit 1
    else
        echo "❌ .env.template not found!"
        exit 1
    fi
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed!"
    echo "📝 Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   Or with Homebrew: brew install uv"
    exit 1
fi

# Install/sync dependencies with uv
echo "📥 Installing dependencies with uv..."
uv sync

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting Streamlit app..."
echo "   App will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run Streamlit with uv
uv run streamlit run main.py

