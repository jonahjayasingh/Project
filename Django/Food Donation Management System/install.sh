#!/bin/bash

echo "========================================="
echo "Smart Food Donation Management System"
echo "Installation Script"
echo "========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed."
    echo "Please install Ollama first:"
    echo "  macOS: brew install ollama"
    echo "  Then run: ollama pull gemma2:2b"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Ollama found"
    echo ""
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️  Setting up database..."
python3 manage.py migrate

# Create superuser prompt
echo ""
echo "========================================="
echo "Create Admin User"
echo "========================================="
echo ""
echo "You need to create an admin user to manage the system."
read -p "Create admin user now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 manage.py createsuperuser
fi

echo ""
echo "========================================="
echo "✅ Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start Ollama (in a separate terminal):"
echo "   ollama serve"
echo ""
echo "2. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the development server:"
echo "   python3 manage.py runserver"
echo ""
echo "4. Open your browser:"
echo "   http://127.0.0.1:8000"
echo ""
echo "========================================="
