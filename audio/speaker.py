import platform
import subprocess
import os
from pathlib import Path
from config import TTS_OUTPUT_FILE

try:
    from TTS.api import TTS as CoquiTTS
    coqui_model = CoquiTTS(model_name="tts_models/es/css10/vits", progress_bar=False, gpu=False)
    COQUI_AVAILABLE = True
    print("[INFO] Coqui TTS disponible")
except ImportError:
    COQUI_AVAILABLE = False
    print("[INFO] Coqui TTS no disponible. Usando TTS del sistema.")

def speak(text):
    """Convierte texto a voz usando el mejor método disponible"""
    if not text or not text.strip():
        return
    
    text = text.strip()
    system = platform.system()
    
    if COQUI_AVAILABLE:
        _speak_with_coqui(text, system)
    else:
        _speak_with_system(text, system)

def _speak_with_coqui(text, system):
    """Usar Coqui TTS para generar voz"""
    try:
        output_file = str(TTS_OUTPUT_FILE)
        coqui_model.tts_to_file(text=text, file_path=output_file)
        
        if system == "Darwin":  # macOS
            subprocess.run(["afplay", output_file], check=True)
        elif system == "Linux":  # Linux/Raspberry Pi
            subprocess.run(["aplay", output_file], check=True)
        else:
            print(f"[Coqui-TTS] {text}")
            
        # Limpiar archivo temporal
        try:
            os.remove(output_file)
        except OSError:
            pass
            
    except subprocess.CalledProcessError as e:
        print(f"[TTS Error] Error reproduciendo audio: {e}")
        _speak_with_system(text, system)  # Fallback
    except Exception as e:
        print(f"[TTS Error] Error con Coqui TTS: {e}")
        _speak_with_system(text, system)  # Fallback

def _speak_with_system(text, system):
    """Usar TTS del sistema operativo"""
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["say", text], check=True)
        elif system == "Linux":  # Linux/Raspberry Pi
            subprocess.run(["espeak", "-s", "150", text], check=True)
        else:
            print(f"[System TTS] {text}")
    except subprocess.CalledProcessError as e:
        print(f"[System TTS Error] {e}")
        print(f"[Fallback] {text}")
    except FileNotFoundError:
        print(f"[TTS] Comando de TTS no encontrado. Texto: {text}")