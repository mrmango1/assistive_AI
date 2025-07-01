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

# Importar OpenCV solo para rotación de imágenes
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("OpenCV no disponible - rotación de imágenes deshabilitada")

def take_picture(filename=None, rotation=None):
    """Toma una foto usando comandos del sistema de Raspberry Pi"""
    if filename is None:
        filename = DEFAULT_IMAGE_FILENAME
    
    if rotation is None:
        rotation = CAMERA_ROTATION
    
    filename = Path(filename)
    
    try:
        # Solo usar comandos del sistema para Raspberry Pi
        if _take_picture_system_command(filename):
            result_path = str(filename)
            
            # Aplicar rotación si es necesario
            if rotation != 0:
                print(f"Aplicando rotación de {rotation}°...")
                _rotate_image(result_path, rotation)
            
            return result_path
        else:
            print("Error: No se pudo tomar la foto con ningún comando disponible")
            return None
            
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
    """Prueba rápida de cámara para Raspberry Pi"""
    print("=== PRUEBA DE CÁMARAS RASPBERRY PI ===")
    print(f"OpenCV disponible: {CV2_AVAILABLE}")
    print(f"Rotación configurada: {CAMERA_ROTATION}°")
    
    # Probar comandos del sistema
    print("\nProbando comandos del sistema...")
    temp_file = Path("/tmp/test_camera.jpg")
    if _take_picture_system_command(temp_file):
        print("✅ Comandos del sistema funcionan")
        if temp_file.exists():
            temp_file.unlink()
        return True
    else:
        print("❌ No se encontraron comandos de cámara funcionales")
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
                
                # La rotación se aplica automáticamente en take_picture()
                if CAMERA_ROTATION != 0:
                    print(f"✅ Rotación de {CAMERA_ROTATION}° aplicada")
        else:
            print("❌ Error tomando foto")
    else:
        print("❌ No se encontraron cámaras funcionales")
    
    total_time = time.time() - start_time
    print(f"\n⏱️ Tiempo total: {total_time:.2f} segundos")