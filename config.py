import os
from pathlib import Path

# Configuración de API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuración de idioma
LANGUAGE = "spa"

# Configuración de OCR
USE_OPENAI_OCR = True

# Configuración de TTS
USE_OPENAI_TTS = True 

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