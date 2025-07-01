import subprocess
import os
import requests
from pathlib import Path
from config import TTS_OUTPUT_FILE, OPENAI_API_KEY, OPENAI_TTS_VOICE

def speak(text):
    """Convierte texto a voz usando OpenAI TTS"""
    if not text or not text.strip():
        return
    
    text = text.strip()
    
    if not OPENAI_API_KEY:
        print(f"[Error] No hay clave API de OpenAI configurada. Texto: {text}")
        return
    
    _speak_with_openai(text)

def _speak_with_openai(text):
    """Usar OpenAI TTS para generar voz"""
    try:
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        
        data = {
            "model": "tts-1",
            "input": text,
            "voice": OPENAI_TTS_VOICE,
            "response_format": "mp3"
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            output_file = str(TTS_OUTPUT_FILE).replace('.wav', '.mp3')
            
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            # Reproducir el archivo de audio en Raspberry Pi
            try:
                subprocess.run(["mpg123", output_file], check=True)
            except FileNotFoundError:
                # Fallback a ffplay si mpg123 no está disponible
                try:
                    subprocess.run(["ffplay", "-nodisp", "-autoexit", output_file], check=True)
                except FileNotFoundError:
                    # Último fallback: convertir a wav y usar aplay
                    wav_file = output_file.replace('.mp3', '.wav')
                    subprocess.run(["ffmpeg", "-i", output_file, wav_file], check=True)
                    subprocess.run(["aplay", wav_file], check=True)
                    os.remove(wav_file)
            
            # Limpiar archivo temporal
            try:
                os.remove(output_file)
            except OSError:
                pass
        else:
            print(f"[OpenAI-TTS Error] Error {response.status_code}: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"[OpenAI-TTS Error] Error de conexión: {e}")
    except Exception as e:
        print(f"[OpenAI-TTS Error] Error inesperado: {e}")