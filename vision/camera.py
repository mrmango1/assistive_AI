import cv2
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

def take_picture(filename=None):
    """Toma una foto usando la cámara disponible según el sistema operativo"""
    if filename is None:
        filename = DEFAULT_IMAGE_FILENAME
    
    filename = Path(filename)
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            return _take_picture_opencv_fast(filename)
        elif system == "Linux":
            # Intentar primero con PiCamera si está disponible
            try:
                return _take_picture_picamera(filename)
            except ImportError:
                print("PiCamera no disponible, usando OpenCV...")
                return _take_picture_opencv_fast(filename)
        else:
            return _take_picture_opencv_fast(filename)
            
    except Exception as e:
        print(f"Error tomando foto: {e}")
        return None

def _take_picture_opencv_fast(filename):
    """Versión optimizada y rápida para tomar fotos"""
    print("Accediendo a la cámara...")
    
    # Usar AVFoundation en macOS para mejor rendimiento
    backend = cv2.CAP_AVFOUNDATION if platform.system() == "Darwin" else cv2.CAP_ANY
    cam = cv2.VideoCapture(0, backend)
    
    if not cam.isOpened():
        print("Error: No se pudo acceder a la cámara")
        return None
    
    try:
        # Configuración rápida y eficiente
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1024)
        cam.set(cv2.CAP_PROP_FPS, 30)
        cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Buffer mínimo para menor latencia
        
        # Solo para macOS: habilitar auto-exposición rápida
        if platform.system() == "Darwin":
            cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        
        # Tiempo mínimo de inicialización (1 segundo)
        time.sleep(1)
        
        # Descartar solo 3 frames iniciales para ahorrar tiempo
        for _ in range(3):
            ret, frame = cam.read()
            if not ret:
                break
        
        # Tomar la foto final
        ret, frame = cam.read()
        
        if ret and frame is not None:
            brightness = frame.mean()
            
            # Solo si la imagen está MUY oscura, intentar una más
            if brightness < 10:
                print("Imagen muy oscura, reintentando...")
                time.sleep(0.5)
                ret, frame = cam.read()
            
            if ret and frame is not None:
                # Crear directorio si no existe
                filename.parent.mkdir(parents=True, exist_ok=True)
                
                success = cv2.imwrite(str(filename), frame)
                if success:
                    print(f"Foto guardada: {filename} (brightness: {brightness:.1f})")
                    return str(filename)
                else:
                    print("Error: No se pudo guardar la imagen")
                    return None
            else:
                print("Error: No se pudo capturar frame válido")
                return None
        else:
            print("Error: No se pudo capturar la imagen")
            return None
            
    except Exception as e:
        print(f"Error en _take_picture_opencv_fast: {e}")
        return None
    finally:
        cam.release()

def _take_picture_picamera(filename):
    """Toma foto usando PiCamera2 - versión rápida"""
    try:
        from picamera2 import Picamera2
        
        picam2 = Picamera2()
        # Configuración básica y rápida
        config = picam2.create_still_configuration()
        picam2.configure(config)
        
        picam2.start()
        # Tiempo reducido de espera
        time.sleep(1)
        
        picam2.capture_file(str(filename))
        picam2.stop()
        print(f"Foto guardada en: {filename}")
        return str(filename)
        
    except Exception as e:
        print(f"Error en _take_picture_picamera: {e}")
        return None

def test_camera_fast():
    """Prueba rápida de cámara"""
    print("=== PRUEBA RÁPIDA DE CÁMARA ===")
    
    backend = cv2.CAP_AVFOUNDATION if platform.system() == "Darwin" else cv2.CAP_ANY
    cam = cv2.VideoCapture(0, backend)
    
    if not cam.isOpened():
        print("❌ No se puede acceder a la cámara")
        return False
    
    print("✅ Cámara accesible")
    
    # Mostrar propiedades básicas
    width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"Resolución: {width}x{height}")
    
    # Prueba rápida de captura
    time.sleep(0.5)
    ret, frame = cam.read()
    
    if ret and frame is not None:
        brightness = frame.mean()
        print(f"✅ Captura exitosa (brightness: {brightness:.1f})")
        success = True
    else:
        print("❌ No se pudo capturar frame")
        success = False
    
    cam.release()
    return success

if __name__ == "__main__":
    print("🎥 PRUEBA RÁPIDA DE CÁMARA 🎥\n")
    
    # Prueba rápida
    start_time = time.time()
    if test_camera_fast():
        # Tomar foto de prueba
        print("\n=== TOMANDO FOTO DE PRUEBA ===")
        result = take_picture("test_photo.jpg")
        
        if result:
            print(f"✅ Foto guardada: {result}")
            if os.path.exists(result):
                size = os.path.getsize(result)
                print(f"Tamaño: {size} bytes")
        else:
            print("❌ Error tomando foto")
    
    total_time = time.time() - start_time
    print(f"\n⏱️  Tiempo total: {total_time:.2f} segundos")