import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configuración de API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuración de idioma
LANGUAGE = os.getenv("LANGUAGE", "spa")

# Configuración de OCR
USE_OPENAI_OCR = os.getenv("USE_OPENAI_OCR", "true").lower() == "true"

# Configuración de TTS
USE_OPENAI_TTS = os.getenv("USE_OPENAI_TTS", "true").lower() == "true"
OPENAI_TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "alloy")  # Opciones: alloy, echo, fable, onyx, nova, shimmer 

# Configuración de modelos
VOSK_MODEL_PATH = os.path.expanduser("./models/vosk-model-small-es-0.42")

# Configuración de archivos temporales
TEMP_DIR = Path.cwd() / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# Configuración de TTS
TTS_OUTPUT_FILE = TEMP_DIR / "output.wav"

# Configuración de cámara
DEFAULT_IMAGE_FILENAME = TEMP_DIR / "captured_image.jpg"

# Configuración de reconocimiento de voz
SAMPLE_RATE = 16000
BLOCK_SIZE = 8000

# Timeouts
INTERNET_CHECK_TIMEOUT = 3
API_REQUEST_TIMEOUT = 30