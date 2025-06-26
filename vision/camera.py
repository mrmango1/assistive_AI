import platform
import time
import sys
import os
import subprocess
from pathlib import Path

# Agregar el directorio padre al path para poder importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import DEFAULT_IMAGE_FILENAME, CAMERA_ROTATION
except ImportError:
    # Fallback si no se puede importar config
    DEFAULT_IMAGE_FILENAME = Path.cwd().parent / "temp" / "captured_image.jpg"
    DEFAULT_IMAGE_FILENAME.parent.mkdir(exist_ok=True)
    CAMERA_ROTATION = 0

# Importar librerías según disponibilidad
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("OpenCV no disponible")

try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False

try:
    import picamera
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False

def take_picture(filename=None, rotation=None):
    """Toma una foto usando la cámara disponible según el sistema operativo"""
    if filename is None:
        filename = DEFAULT_IMAGE_FILENAME
    
    if rotation is None:
        rotation = CAMERA_ROTATION
    
    filename = Path(filename)
    system = platform.system()
    
    try:
        result_path = None
        
        if system == "Linux":  # Raspberry Pi
            # Prioridad: Comandos del sistema > PiCamera2 > PiCamera > OpenCV
            if _take_picture_system_command(filename):
                result_path = str(filename)
            elif PICAMERA2_AVAILABLE:
                print("Usando PiCamera2...")
                result_path = _take_picture_picamera2(filename)
            elif PICAMERA_AVAILABLE:
                print("Usando PiCamera legacy...")
                result_path = _take_picture_picamera_legacy(filename)
            elif CV2_AVAILABLE:
                print("Usando OpenCV con configuración alternativa...")
                result_path = _take_picture_opencv_alternative(filename)
            else:
                print("Error: No hay librerías de cámara disponibles")
                return None
        else:  # macOS, Windows
            result_path = _take_picture_opencv_fast(filename)
        
        # Aplicar rotación si es necesario
        if result_path and rotation != 0:
            print(f"Aplicando rotación de {rotation}°...")
            _rotate_image(result_path, rotation)
        
        return result_path
            
    except Exception as e:
        print(f"Error tomando foto: {e}")
        return None

def _take_picture_system_command(filename):
    """Usar comandos del sistema para tomar foto (más confiable en RPi)"""
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)
    
    commands_to_try = [
        # libcamera (Raspberry Pi OS Bullseye+)
        ["libcamera-still", "-o", str(filename), "-t", "1000", "--width", "1920", "--height", "1080"],
        # raspistill (Raspberry Pi OS legacy)
        ["raspistill", "-o", str(filename), "-t", "1000", "-w", "1920", "-h", "1080"],
        # fswebcam (USB cameras)
        ["fswebcam", "-r", "1280x720", "--no-banner", str(filename)],
        # uvccapture (USB cameras alternative)
        ["uvccapture", "-o", str(filename), "-x", "1280", "-y", "720"]
    ]
    
    for cmd in commands_to_try:
        try:
            print(f"Intentando comando: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and filename.exists() and filename.stat().st_size > 0:
                print(f"✅ Foto capturada con {cmd[0]}: {filename}")
                return True
            else:
                print(f"❌ {cmd[0]} falló: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"❌ {cmd[0]} timeout")
        except FileNotFoundError:
            print(f"❌ {cmd[0]} no disponible")
        except Exception as e:
            print(f"❌ Error con {cmd[0]}: {e}")
    
    return False

def _take_picture_opencv_alternative(filename):
    """Configuración alternativa de OpenCV para RPi"""
    if not CV2_AVAILABLE:
        return None
        
    print("Probando configuración alternativa de OpenCV...")
    
    # Diferentes backends para probar
    backends = [
        cv2.CAP_V4L2,
        cv2.CAP_V4L,
        cv2.CAP_GSTREAMER,
        cv2.CAP_ANY
    ]
    
    for backend in backends:
        print(f"Probando backend: {backend}")
        cam = cv2.VideoCapture(0, backend)
        
        if not cam.isOpened():
            print(f"Backend {backend} no disponible")
            continue
        
        try:
            # Configuraciones más básicas
            cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            cam.set(cv2.CAP_PROP_FPS, 10)
            
            # Esperar más tiempo
            time.sleep(5)
            
            # Intentar capturar con timeout manual
            print("Intentando captura...")
            for attempt in range(20):  # Más intentos
                ret, frame = cam.read()
                if ret and frame is not None:
                    filename.parent.mkdir(parents=True, exist_ok=True)
                    success = cv2.imwrite(str(filename), frame)
                    if success:
                        print(f"✅ Foto guardada con OpenCV backend {backend}: {filename}")
                        cam.release()
                        return str(filename)
                
                time.sleep(0.2)  # Pausa entre intentos
            
            print(f"Backend {backend} no pudo capturar frames")
            
        except Exception as e:
            print(f"Error con backend {backend}: {e}")
        finally:
            cam.release()
    
    return None

def _take_picture_picamera2(filename):
    """Toma foto usando PiCamera2"""
    if not PICAMERA2_AVAILABLE:
        return None
        
    try:
        print("Inicializando PiCamera2...")
        picam2 = Picamera2()
        
        # Configuración más simple
        config = picam2.create_still_configuration()
        picam2.configure(config)
        
        print("Iniciando cámara...")
        picam2.start()
        
        # Esperar estabilización
        time.sleep(3)
        
        # Capturar imagen
        print("Capturando imagen...")
        filename.parent.mkdir(parents=True, exist_ok=True)
        picam2.capture_file(str(filename))
        
        # Detener cámara
        picam2.stop()
        
        print(f"✅ Foto guardada con PiCamera2: {filename}")
        return str(filename)
        
    except Exception as e:
        print(f"Error con PiCamera2: {e}")
        return None

def _take_picture_picamera_legacy(filename):
    """Toma foto usando PiCamera legacy"""
    if not PICAMERA_AVAILABLE:
        return None
        
    try:
        print("Inicializando PiCamera legacy...")
        with picamera.PiCamera() as camera:
            # Configuración básica
            camera.resolution = (1920, 1080)
            # No usar preview en modo headless
            # camera.start_preview()
            
            # Esperar estabilización
            time.sleep(3)
            
            # Capturar imagen
            filename.parent.mkdir(parents=True, exist_ok=True)
            camera.capture(str(filename))
            
        print(f"✅ Foto guardada con PiCamera legacy: {filename}")
        return str(filename)
        
    except Exception as e:
        print(f"Error con PiCamera legacy: {e}")
        return None

def _take_picture_opencv_fast(filename):
    """Versión para macOS/Windows"""
    if not CV2_AVAILABLE:
        return None
        
    print("Accediendo a la cámara...")
    
    backend = cv2.CAP_AVFOUNDATION if platform.system() == "Darwin" else cv2.CAP_ANY
    cam = cv2.VideoCapture(0, backend)
    
    if not cam.isOpened():
        print("Error: No se pudo acceder a la cámara")
        return None
    
    try:
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1024)
        cam.set(cv2.CAP_PROP_FPS, 30)
        cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if platform.system() == "Darwin":
            cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        
        time.sleep(1)
        
        for _ in range(3):
            ret, frame = cam.read()
            if not ret:
                break
        
        ret, frame = cam.read()
        
        if ret and frame is not None:
            filename.parent.mkdir(parents=True, exist_ok=True)
            success = cv2.imwrite(str(filename), frame)
            if success:
                print(f"✅ Foto guardada: {filename}")
                return str(filename)
        
        return None
            
    except Exception as e:
        print(f"Error en _take_picture_opencv_fast: {e}")
        return None
    finally:
        cam.release()

def _rotate_image(image_path, rotation_degrees):
    """Rota una imagen según los grados especificados"""
    if not CV2_AVAILABLE or rotation_degrees == 0:
        return
    
    try:
        # Leer la imagen
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"❌ No se pudo leer la imagen para rotación: {image_path}")
            return
        
        # Normalizar el ángulo de rotación
        rotation_degrees = rotation_degrees % 360
        
        if rotation_degrees == 0:
            return  # No hay necesidad de rotar
        
        # Obtener dimensiones de la imagen
        height, width = image.shape[:2]
        
        # Calcular el centro de rotación
        center = (width // 2, height // 2)
        
        # Crear la matriz de rotación
        rotation_matrix = cv2.getRotationMatrix2D(center, rotation_degrees, 1.0)
        
        # Calcular las nuevas dimensiones después de la rotación
        cos = abs(rotation_matrix[0, 0])
        sin = abs(rotation_matrix[0, 1])
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))
        
        # Ajustar la matriz de rotación para centrar la imagen
        rotation_matrix[0, 2] += (new_width / 2) - center[0]
        rotation_matrix[1, 2] += (new_height / 2) - center[1]
        
        # Aplicar la rotación
        rotated_image = cv2.warpAffine(image, rotation_matrix, (new_width, new_height))
        
        # Guardar la imagen rotada
        success = cv2.imwrite(str(image_path), rotated_image)
        if success:
            print(f"✅ Imagen rotada {rotation_degrees}° correctamente")
        else:
            print(f"❌ Error guardando imagen rotada")
            
    except Exception as e:
        print(f"❌ Error rotando imagen: {e}")

def test_camera_fast():
    """Prueba rápida de cámara"""
    print("=== PRUEBA DE CÁMARAS DISPONIBLES ===")
    print(f"OpenCV disponible: {CV2_AVAILABLE}")
    print(f"PiCamera2 disponible: {PICAMERA2_AVAILABLE}")
    print(f"PiCamera legacy disponible: {PICAMERA_AVAILABLE}")
    print(f"Rotación configurada: {CAMERA_ROTATION}°")
    
    system = platform.system()
    print(f"Sistema: {system}")
    
    if system == "Linux":
        # Probar comandos del sistema primero
        print("\nProbando comandos del sistema...")
        temp_file = Path("/tmp/test_camera.jpg")
        if _take_picture_system_command(temp_file):
            print("✅ Comandos del sistema funcionan")
            if temp_file.exists():
                temp_file.unlink()
            return True
        
        # Probar PiCamera2
        if PICAMERA2_AVAILABLE:
            try:
                print("\nProbando PiCamera2...")
                picam2 = Picamera2()
                info = picam2.camera_properties
                print(f"✅ PiCamera2 funcional: {info}")
                return True
            except Exception as e:
                print(f"❌ Error con PiCamera2: {e}")
        
        # Probar PiCamera legacy
        if PICAMERA_AVAILABLE:
            try:
                print("\nProbando PiCamera legacy...")
                with picamera.PiCamera() as camera:
                    print("✅ PiCamera legacy funcional")
                    return True
            except Exception as e:
                print(f"❌ Error con PiCamera legacy: {e}")
    
    # Probar OpenCV como último recurso
    if CV2_AVAILABLE:
        print(f"\nProbando OpenCV...")
        backend = cv2.CAP_V4L2 if system == "Linux" else cv2.CAP_ANY
        cam = cv2.VideoCapture(0, backend)
        
        if cam.isOpened():
            print("✅ OpenCV puede acceder a la cámara")
            cam.release()
            return True
        else:
            print("❌ OpenCV no puede acceder a la cámara")
            cam.release()
    
    return False

if __name__ == "__main__":
    print("🎥 PRUEBA DE CÁMARA RASPBERRY PI 🎥\n")
    
    start_time = time.time()
    if test_camera_fast():
        print("\n=== TOMANDO FOTO DE PRUEBA ===")
        result = take_picture("test_photo.jpg")
        
        if result:
            print(f"✅ Foto guardada: {result}")
            if os.path.exists(result):
                size = os.path.getsize(result)
                print(f"Tamaño: {size} bytes")
                
                # Probar rotación de imagen
                rotated_result = result.parent / f"rotated_{result.name}"
                _rotate_image(result, CAMERA_ROTATION)
                
                if os.path.exists(result):
                    print(f"✅ Imagen rotada guardada: {result}")
                else:
                    print("❌ La imagen rotada no se encontró")
        else:
            print("❌ Error tomando foto")
    else:
        print("❌ No se encontraron cámaras funcionales")
    
    total_time = time.time() - start_time
    print(f"\n⏱️ Tiempo total: {total_time:.2f} segundos")