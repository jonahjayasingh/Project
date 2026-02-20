#!/bin/bash

# ChatGPT Clone Setup Script
echo "🚀 ChatGPT Clone Setup"
echo "====================="
echo ""

# Check if Ollama is installed
echo "📋 Checking prerequisites..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed!"
    echo "   Please install Ollama from: https://ollama.ai/"
    echo "   Then run this script again."
    exit 1
fi
echo "✅ Ollama is installed"

# Check if Ollama is running
echo ""
echo "🔍 Checking if Ollama is running..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running!"
    echo "   Starting Ollama in the background..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
    echo "✅ Ollama started"
else
    echo "✅ Ollama is already running"
fi

# Check if model is downloaded
echo ""
echo "🤖 Checking for AI model..."
if ollama list | grep -q "llava:7b"; then
    echo "✅ Model llava:7b is already downloaded"
else
    echo "⬇️  Downloading llava:7b model (this may take a while)..."
    ollama pull llava:7b
    echo "✅ Model downloaded"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Run migrations
echo ""
echo "🗄️  Setting up database..."
python manage.py migrate --no-input
echo "✅ Database ready"

# Create directories
echo ""
echo "📁 Creating necessary directories..."
mkdir -p books book_db
echo "✅ Directories created"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎉 You're ready to go!"
echo ""
echo "To start the application:"
echo "  1. Make sure Ollama is running: ollama serve"
echo "  2. Start the Django server: python manage.py runserver"
echo "  3. Open your browser: http://127.0.0.1:8000/"
echo ""
echo "📚 To use RAG features:"
echo "  - Go to Settings (gear icon)"
echo "  - Upload PDF or TXT files"
echo "  - Start chatting with your documents!"
echo ""
