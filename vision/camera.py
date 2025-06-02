import cv2
import platform
from pathlib import Path
from config import DEFAULT_IMAGE_FILENAME

def take_picture(filename=None):
    """Toma una foto usando la cámara disponible según el sistema operativo"""
    if filename is None:
        filename = DEFAULT_IMAGE_FILENAME
    
    filename = Path(filename)
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            return _take_picture_opencv(filename)
        elif system == "Linux":
            # Intentar primero con PiCamera si está disponible
            try:
                return _take_picture_picamera(filename)
            except ImportError:
                print("PiCamera no disponible, usando OpenCV...")
                return _take_picture_opencv(filename)
        else:
            return _take_picture_opencv(filename)
            
    except Exception as e:
        print(f"Error tomando foto: {e}")
        return None

def _take_picture_opencv(filename):
    """Toma foto usando OpenCV"""
    cam = cv2.VideoCapture(0)
    
    if not cam.isOpened():
        print("Error: No se pudo acceder a la cámara")
        return None
    
    # Dar tiempo a la cámara para inicializar
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    ret, frame = cam.read()
    cam.release()
    
    if ret:
        cv2.imwrite(str(filename), frame)
        print(f"Foto guardada en: {filename}")
        return str(filename)
    else:
        print("Error: No se pudo capturar la imagen")
        return None

def _take_picture_picamera(filename):
    """Toma foto usando PiCamera2"""
    from picamera2 import Picamera2
    
    picam2 = Picamera2()
    picam2.start()
    picam2.capture_file(str(filename))
    picam2.stop()
    print(f"Foto guardada en: {filename}")
    return str(filename)