#!/bin/bash

echo "========================================="
echo "Smart Food Donation Management System"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./install.sh first"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running!"
    echo ""
    echo "Please start Ollama in a separate terminal:"
    echo "  ollama serve"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Ollama is running"
fi

# Activate virtual environment
source venv/bin/activate

echo ""
echo "🚀 Starting Django development server..."
echo ""
echo "Access the application at: http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run Django server
python3 manage.py runserver
