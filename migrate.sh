#!/bin/bash

# Database migration helper script
# Runs migrations for local development

echo "🔄 Database Migration Script"
echo "============================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Make sure DATABASE_URL is set in your environment"
    echo ""
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed!"
    echo "📝 Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "🚀 Running database migrations..."
echo ""

# Run the migration script
uv run python migrate.py

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✅ Migration completed successfully!"
    echo "   You can now start the application with: ./run_api.sh"
else
    echo ""
    echo "❌ Migration failed with exit code $exit_code"
    echo "   Check the error messages above for details"
fi

exit $exit_code

