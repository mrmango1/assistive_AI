import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from config import VOSK_MODEL_PATH

class VoskRecognizer:
    def __init__(self):
        self.q = queue.Queue()
        self.model = None
        self.recognizer = None
        self.stream = None
        self.initialized = False
        self.listening = False
        self.paused = False
    
    def _callback(self, indata, frames, time, status):
        if status:
            print("Status:", status)
        # Solo procesar audio si no está pausado
        if not self.paused:
            self.q.put(bytes(indata))
    
    def initialize(self):
        """Inicializa el modelo Vosk y el reconocedor"""
        try:
            print("Cargando modelo Vosk...")
            self.model = Model(VOSK_MODEL_PATH)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            print("Modelo Vosk cargado exitosamente.")
            self.initialized = True
            return True
        except Exception as e:
            print(f"Error inicializando Vosk: {e}")
            return False
    
    def start_listening(self):
        """Inicia el stream de audio"""
        if not self.initialized:
            raise RuntimeError("Vosk no está inicializado. Llama a initialize() primero.")
        
        try:
            self.stream = sd.RawInputStream(
                samplerate=16000, 
                blocksize=8000, 
                dtype='int16',
                channels=1, 
                callback=self._callback
            )
            self.stream.start()
            self.listening = True
            self.paused = False
            print("Escuchando continuamente con Vosk...")
            return True
        except Exception as e:
            print(f"Error iniciando stream de audio: {e}")
            return False
    
    def stop_listening(self):
        """Detiene el stream de audio"""
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.listening = False
        self.paused = False
    
    def pause_listening(self):
        """Pausa el procesamiento de audio sin detener el stream"""
        if self.listening:
            self.paused = True
            # Limpiar la cola de audio acumulado
            while not self.q.empty():
                try:
                    self.q.get_nowait()
                except:
                    break
            print("🔇 Escucha pausada durante procesamiento...")
    
    def resume_listening(self):
        """Reanuda el procesamiento de audio"""
        if self.listening:
            self.paused = False
            # Limpiar la cola antes de reanudar
            while not self.q.empty():
                try:
                    self.q.get_nowait()
                except:
                    break
            print("🎤 Escucha reanudada...")
    
    def listen_command(self):
        """Escucha un comando de voz"""
        if not self.initialized or not self.stream or self.paused:
            return None
        
        try:
            data = self.q.get_nowait()
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").strip().lower()
                if text:
                    print(f"Detectado: {text}")
                    return text
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Error en reconocimiento: {e}")
        
        return None

# Instancia global del reconocedor
recognizer_instance = VoskRecognizer()

def initialize_recognizer():
    """Inicializa el reconocedor de voz"""
    return recognizer_instance.initialize()

def start_listening():
    """Inicia la escucha de comandos"""
    return recognizer_instance.start_listening()

def stop_listening():
    """Detiene la escucha de comandos"""
    recognizer_instance.stop_listening()

def pause_listening():
    """Pausa la escucha de comandos"""
    recognizer_instance.pause_listening()

def resume_listening():
    """Reanuda la escucha de comandos"""
    recognizer_instance.resume_listening()

def listen_command():
    """Función de compatibilidad para escuchar comandos"""
    return recognizer_instance.listen_command()