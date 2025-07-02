import json
import os
import threading
import difflib
import sys
import time
from pathlib import Path

from audio.recognizer import initialize_recognizer, start_listening, stop_listening, listen_command, pause_listening, resume_listening
from audio.speaker import speak
from vision.camera import take_picture
from vision.ocr import ocr_image
from utils.internet import check_internet
from config import TEMP_DIR

command_lock = threading.Lock()

def get_best_command_match(text, command_aliases, cutoff=0.6):
    """Encuentra la mejor coincidencia de comando usando búsqueda difusa"""
    if not text or not command_aliases:
        return None
        
    # Normalizar el texto de entrada
    text = text.lower().strip()
    
    all_phrases = {
        alias.lower(): action
        for action, aliases in command_aliases.items()
        for alias in aliases
    }
    
    match = difflib.get_close_matches(text, all_phrases.keys(), n=1, cutoff=cutoff)
    return all_phrases[match[0]] if match else None

def load_commands_from_file(file_path="commands.json"):
    """Carga comandos desde archivo JSON o retorna comandos por defecto"""
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                commands = json.load(f)
                if not isinstance(commands, dict):
                    raise ValueError("El archivo de comandos debe contener un diccionario")
                # Validar que cada comando tenga una lista de aliases
                for action, aliases in commands.items():
                    if not isinstance(aliases, list) or not aliases:
                        raise ValueError(f"El comando '{action}' debe tener una lista no vacía de aliases")
                return commands
    except (json.JSONDecodeError, ValueError, FileNotFoundError) as e:
        print(f"Error cargando comandos desde {file_path}: {e}")
        print("Usando comandos por defecto...")
    
    # Comandos por defecto simplificados para Raspberry Pi
    return {
        "read_document": [
            "leer documento", "quiero que leas", "puedes leer esto",
            "lee esto", "lee el documento", "leer texto"
        ],
        "exit": ["salir", "terminar", "adiós", "bye", "cerrar"]
    }

def cleanup_temp_file(filename):
    """Limpia archivos temporales de manera segura"""
    if filename and os.path.exists(filename):
        try:
            os.remove(filename)
            print(f"Archivo temporal eliminado: {filename}")
        except OSError as e:
            print(f"No se pudo eliminar archivo temporal {filename}: {e}")

def handle_command(action):
    """Maneja la ejecución de comandos con bloqueo para evitar concurrencia"""
    filename = None
    try:
        with command_lock:
            # Pausar la escucha mientras se procesa el comando
            pause_listening()
            
            if action == "read_document":
                speak("Tomando foto del documento...")
                filename = take_picture()
                
                if not filename:
                    speak("No pude tomar la foto del documento.")
                    return
                
                # Verificar conexión
                if not check_internet():
                    speak("Sin conexión a internet.")
                else:
                    speak("Procesando documento con inteligencia artificial.")
                
                text = ocr_image(filename)
                if text and text.strip():
                    speak(f"El documento dice: {text}")
                else:
                    speak("No pude leer texto en el documento.")
                
                speak("Comando completado. Puedes dar otro comando o decir 'salir' para terminar.")

            elif action == "exit":
                speak("Hasta luego.")
                stop_listening()
                cleanup_temp_files()
                sys.exit(0)
                
    except Exception as e:
        print(f"Error ejecutando comando {action}: {e}")
        speak("Ocurrió un error ejecutando el comando.")
    finally:
        # Siempre limpiar el archivo temporal
        if filename:
            cleanup_temp_file(filename)
        # Reanudar la escucha al finalizar el comando
        resume_listening()

def cleanup_temp_files():
    """Limpia todos los archivos temporales al salir"""
    try:
        for file_path in TEMP_DIR.glob("*"):
            if file_path.is_file():
                file_path.unlink()
        print("Archivos temporales limpiados.")
    except Exception as e:
        print(f"Error limpiando archivos temporales: {e}")

def main():
    """Función principal del asistente"""
    try:
        print("Iniciando asistente de voz...")
        
        # Mostrar configuración actual
        print(f"Configuración - OCR: OpenAI")
        print(f"Configuración - TTS: OpenAI")
        
        # Cargar comandos
        known_commands = load_commands_from_file()
        if not known_commands:
            print("Error: No se pudieron cargar los comandos")
            return

        # Inicializar reconocedor de voz
        print("Inicializando reconocedor de voz...")
        if not initialize_recognizer():
            print("Error: No se pudo inicializar el reconocedor de voz")
            return
        
        # Iniciar escucha
        print("Configurando escucha de audio...")
        if not start_listening():
            print("Error: No se pudo iniciar la escucha de audio")
            return

        def listen_loop():
            """Bucle principal de escucha de comandos"""
            # Ahora sí está realmente listo
            speak("Asistente listo. Di un comando para comenzar.")
            
            while True:
                try:
                    command_text = listen_command()
                    if command_text:
                        print(f"Comando detectado: {command_text}")
                        action = get_best_command_match(command_text, known_commands)
                        
                        if action:
                            if command_lock.locked():
                                speak("Espera un momento, estoy procesando otro comando.")
                            else:
                                # Ejecutar comando en hilo separado
                                threading.Thread(
                                    target=handle_command, 
                                    args=(action,), 
                                    daemon=True
                                ).start()
                        else:
                            speak("No entendí el comando. Intenta de nuevo.")
                    else:
                        # Pequeña pausa para no saturar el CPU
                        time.sleep(0.1)
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error en listen_loop: {e}")
                    speak("Error detectando comando.")
                    time.sleep(1)  # Pausa antes de continuar

        # Iniciar hilo de escucha
        listen_thread = threading.Thread(target=listen_loop, daemon=True)
        listen_thread.start()

        try:
            # Mantener el programa ejecutándose
            while listen_thread.is_alive():
                listen_thread.join(timeout=1)
        except KeyboardInterrupt:
            print("\nInterrumpido por el usuario")
            speak("Cerrando asistente.")
            stop_listening()
            cleanup_temp_files()
            sys.exit(0)
            
    except Exception as e:
        print(f"Error en main: {e}")
        stop_listening()
        cleanup_temp_files()
        sys.exit(1)

if __name__ == "__main__":
    main()