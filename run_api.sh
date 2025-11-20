#!/bin/bash

# Run FastAPI backend for ICP Analysis Agent

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run with uvicorn
echo "🚀 Starting ICP Analysis Agent API..."
echo "📍 API will be available at http://localhost:8000"
echo "📖 Docs available at http://localhost:8000/docs"
echo ""

python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

