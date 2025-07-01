import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env si existe
load_dotenv()

# Configuración de API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuración de TTS (solo OpenAI)
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
# Rotación de la imagen en grados (0, 90, 180, 270)
# 0 = sin rotación, 90 = 90° horario, 180 = boca abajo, 270 = 90° antihorario
CAMERA_ROTATION = int(os.getenv("CAMERA_ROTATION", "0"))

# Configuración de reconocimiento de voz
SAMPLE_RATE = 16000
BLOCK_SIZE = 8000

# Tiempos de espera
INTERNET_CHECK_TIMEOUT = 3
API_REQUEST_TIMEOUT = 30