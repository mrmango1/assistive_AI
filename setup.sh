#!/bin/bash

# Setup script for Assistive AI Voice Application
echo "🤖 Setting up Assistive AI Voice Application..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "🔧 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create temp directory
echo "📁 Creating temp directory..."
mkdir -p temp

# Create commands.json if it doesn't exist
if [ ! -f "commands.json" ]; then
    echo "📝 Creating default commands.json..."
    cat > commands.json << 'EOF'
{
    "read_document": [
        "leer documento",
        "quiero que leas",
        "puedes leer esto",
        "lee esto",
        "lee el documento",
        "leer texto"
    ],
    "describe_scene": [
        "describir escena",
        "qué ves",
        "descríbeme el lugar",
        "describe la imagen",
        "qué hay aquí",
        "dime qué ves"
    ],
    "exit": [
        "salir",
        "terminar",
        "adiós",
        "bye",
        "cerrar"
    ]
}
EOF
fi

# Check for system dependencies
echo "🔍 Checking system dependencies..."

# Check for Tesseract OCR
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install tesseract tesseract-lang-spa
        else
            echo "❌ Homebrew not found. Please install Tesseract manually or install Homebrew first."
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-spa
    fi
else
    echo "✅ Tesseract OCR found"
fi

# Check for audio tools
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Check for espeak (Linux TTS)
    if ! command -v espeak &> /dev/null; then
        echo "⚠️  espeak not found. Installing..."
        sudo apt-get install -y espeak
    else
        echo "✅ espeak found"
    fi
    
    # Check for aplay (Linux audio player)
    if ! command -v aplay &> /dev/null; then
        echo "⚠️  aplay not found. Installing ALSA utils..."
        sudo apt-get install -y alsa-utils
    else
        echo "✅ aplay found"
    fi
    
    # Optional: mpg123 for MP3 playback (OpenAI TTS)
    if ! command -v mpg123 &> /dev/null; then
        echo "⚠️  mpg123 not found. Installing for OpenAI TTS support..."
        sudo apt-get install -y mpg123
    else
        echo "✅ mpg123 found"
    fi
fi

# Create .env.example file
if [ ! -f ".env.example" ]; then
    echo "📝 Creating .env.example file..."
    cat > .env.example << 'EOF'
# OpenAI API Key for enhanced features
OPENAI_API_KEY=your_openai_api_key_here

# Configure which tools to use
USE_OPENAI_OCR=true
USE_OPENAI_TTS=true

# OpenAI TTS Voice (alloy, echo, fable, onyx, nova, shimmer)
OPENAI_TTS_VOICE=alloy
EOF
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy .env.example to .env and add your OpenAI API key (optional but recommended)"
echo "2. Run the application with: python3 main.py"
echo ""
echo "ℹ️  Configuration:"
echo "   - Edit config.py to change OCR/TTS preferences"
echo "   - Edit commands.json to add custom voice commands"
echo "   - Check README.md for detailed usage instructions"
echo ""
echo "🚀 Ready to run: python3 main.py"
