import platform
import time
import sys
import os
from pathlib import Path

# Agregar el directorio padre al path para poder importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import DEFAULT_IMAGE_FILENAME
except ImportError:
    # Fallback si no se puede importar config
    DEFAULT_IMAGE_FILENAME = Path.cwd().parent / "temp" / "captured_image.jpg"
    DEFAULT_IMAGE_FILENAME.parent.mkdir(exist_ok=True)

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

def take_picture(filename=None):
    """Toma una foto usando la cámara disponible según el sistema operativo"""
    if filename is None:
        filename = DEFAULT_IMAGE_FILENAME
    
    filename = Path(filename)
    system = platform.system()
    
    try:
        if system == "Linux":  # Raspberry Pi
            # Prioridad: PiCamera2 > PiCamera > OpenCV
            if PICAMERA2_AVAILABLE:
                print("Usando PiCamera2...")
                return _take_picture_picamera2(filename)
            elif PICAMERA_AVAILABLE:
                print("Usando PiCamera legacy...")
                return _take_picture_picamera_legacy(filename)
            elif CV2_AVAILABLE:
                print("Usando OpenCV con configuración para RPi...")
                return _take_picture_opencv_rpi(filename)
            else:
                print("Error: No hay librerías de cámara disponibles")
                return None
        else:  # macOS, Windows
            return _take_picture_opencv_fast(filename)
            
    except Exception as e:
        print(f"Error tomando foto: {e}")
        return None

def _take_picture_opencv_rpi(filename):
    """OpenCV específicamente configurado para Raspberry Pi"""
    if not CV2_AVAILABLE:
        return None
        
    print("Accediendo a la cámara con OpenCV...")
    
    # Configuración específica para Raspberry Pi
    cam = cv2.VideoCapture(0, cv2.CAP_V4L2)
    
    if not cam.isOpened():
        print("Error: No se pudo acceder a la cámara")
        return None
    
    try:
        # Configuración optimizada para RPi
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Resolución más baja
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cam.set(cv2.CAP_PROP_FPS, 15)            # FPS más bajo
        cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)      # Buffer mínimo
        
        # Configuraciones adicionales para V4L2
        cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        
        print("Esperando inicialización de cámara...")
        time.sleep(3)  # Más tiempo de espera para RPi
        
        # Descartar frames iniciales
        for i in range(10):
            ret, frame = cam.read()
            if ret:
                print(f"Frame {i+1} capturado correctamente")
            else:
                print(f"Frame {i+1} falló")
            time.sleep(0.1)
        
        # Capturar frame final
        print("Capturando imagen final...")
        for attempt in range(5):
            ret, frame = cam.read()
            if ret and frame is not None:
                # Crear directorio si no existe
                filename.parent.mkdir(parents=True, exist_ok=True)
                
                success = cv2.imwrite(str(filename), frame)
                if success:
                    print(f"✅ Foto guardada: {filename}")
                    return str(filename)
                else:
                    print("Error guardando imagen")
            else:
                print(f"Intento {attempt+1} falló, reintentando...")
                time.sleep(0.5)
        
        print("❌ No se pudo capturar ningún frame válido")
        return None
            
    except Exception as e:
        print(f"Error en _take_picture_opencv_rpi: {e}")
        return None
    finally:
        cam.release()

def _take_picture_picamera2(filename):
    """Toma foto usando PiCamera2"""
    if not PICAMERA2_AVAILABLE:
        return None
        
    try:
        print("Inicializando PiCamera2...")
        picam2 = Picamera2()
        
        # Configuración para foto
        config = picam2.create_still_configuration(
            main={"size": (1920, 1080)},
            lores={"size": (640, 480)},
            display="lores"
        )
        picam2.configure(config)
        
        print("Iniciando cámara...")
        picam2.start()
        
        # Esperar estabilización
        time.sleep(2)
        
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
            camera.start_preview()
            
            # Esperar estabilización
            time.sleep(2)
            
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

def test_camera_fast():
    """Prueba rápida de cámara"""
    print("=== PRUEBA DE CÁMARAS DISPONIBLES ===")
    print(f"OpenCV disponible: {CV2_AVAILABLE}")
    print(f"PiCamera2 disponible: {PICAMERA2_AVAILABLE}")
    print(f"PiCamera legacy disponible: {PICAMERA_AVAILABLE}")
    
    system = platform.system()
    print(f"Sistema: {system}")
    
    if system == "Linux":
        # Probar PiCamera2 primero
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
        else:
            print("❌ Error tomando foto")
    else:
        print("❌ No se encontraron cámaras funcionales")
    
    total_time = time.time() - start_time
    print(f"\n⏱️ Tiempo total: {total_time:.2f} segundos")