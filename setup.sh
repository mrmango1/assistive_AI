#!/bin/bash

# Script de configuración para la Aplicación de Voz Asistiva con IA
echo "🤖 Configurando Aplicación de Voz Asistiva con IA..."

# Verificar si Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 es requerido pero no está instalado. Por favor instala Python 3.8+ primero."
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "🔧 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "🔧 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📦 Instalando dependencias de Python..."
pip install -r requirements.txt

# Crear directorio temporal
echo "📁 Creando directorio temporal..."
mkdir -p temp

# Crear commands.json si no existe
if [ ! -f "commands.json" ]; then
    echo "📝 Creando commands.json predeterminado..."
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

# Verificar dependencias del sistema
echo "🔍 Verificando dependencias del sistema..."

# Verificar Tesseract OCR
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR no encontrado. Instalando..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install tesseract tesseract-lang-spa
        else
            echo "❌ Homebrew no encontrado. Por favor instala Tesseract manualmente o instala Homebrew primero."
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-spa
    fi
else
    echo "✅ Tesseract OCR encontrado"
fi

# Verificar herramientas de audio
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Verificar espeak (TTS de Linux)
    if ! command -v espeak &> /dev/null; then
        echo "⚠️  espeak no encontrado. Instalando..."
        sudo apt-get install -y espeak
    else
        echo "✅ espeak encontrado"
    fi
    
    # Verificar aplay (reproductor de audio de Linux)
    if ! command -v aplay &> /dev/null; then
        echo "⚠️  aplay no encontrado. Instalando utilidades ALSA..."
        sudo apt-get install -y alsa-utils
    else
        echo "✅ aplay encontrado"
    fi
    
    # Opcional: mpg123 para reproducción MP3 (OpenAI TTS)
    if ! command -v mpg123 &> /dev/null; then
        echo "⚠️  mpg123 no encontrado. Instalando para soporte de OpenAI TTS..."
        sudo apt-get install -y mpg123
    else
        echo "✅ mpg123 encontrado"
    fi
fi

# Crear archivo .env.example
if [ ! -f ".env.example" ]; then
    echo "📝 Creando archivo .env.example..."
    cat > .env.example << 'EOF'
# Clave API de OpenAI para funciones mejoradas
OPENAI_API_KEY=your_openai_api_key_here

# Configurar qué herramientas usar
USE_OPENAI_OCR=true
USE_OPENAI_TTS=true

# Voz de OpenAI TTS (alloy, echo, fable, onyx, nova, shimmer)
OPENAI_TTS_VOICE=alloy
EOF
fi

echo ""
echo "🎉 ¡Configuración completa!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Copia .env.example a .env y agrega tu clave API de OpenAI (opcional pero recomendado)"
echo "2. Ejecuta la aplicación con: python3 main.py"
echo ""
echo "ℹ️  Configuración:"
echo "   - Edita config.py para cambiar preferencias de OCR/TTS"
echo "   - Edita commands.json para agregar comandos de voz personalizados"
echo "   - Revisa README.md para instrucciones detalladas de uso"
echo ""
echo "🚀 Listo para ejecutar: python3 main.py"
