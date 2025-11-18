#!/bin/bash

# Check .env file for required variables

echo "Checking .env file configuration..."
echo ""

if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Create one by copying .env.example:"
    echo "   cp .env.example .env"
    exit 1
fi

echo "✅ .env file exists"
echo ""

# Check for API keys (without showing them)
if grep -q "^OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo "✅ OPENAI_API_KEY is set"
elif grep -q "^OPENAI_API_KEY=" .env 2>/dev/null; then
    echo "⚠️  OPENAI_API_KEY is present but may be empty or invalid"
    echo "   Format should be: OPENAI_API_KEY=sk-proj-..."
else
    echo "❌ OPENAI_API_KEY not found in .env"
fi

if grep -q "^ANTHROPIC_API_KEY=sk-ant-" .env 2>/dev/null; then
    echo "✅ ANTHROPIC_API_KEY is set"
elif grep -q "^ANTHROPIC_API_KEY=" .env 2>/dev/null; then
    echo "⚠️  ANTHROPIC_API_KEY is present but may be empty or invalid"
else
    echo "ℹ️  ANTHROPIC_API_KEY not found (optional)"
fi

echo ""
echo "Required .env format:"
echo "---"
echo "OPENAI_API_KEY=sk-proj-your-actual-key-here"
echo "# OR"
echo "ANTHROPIC_API_KEY=sk-ant-your-actual-key-here"
echo "---"
echo ""
echo "You can find your OpenAI API key at:"
echo "https://platform.openai.com/api-keys"

