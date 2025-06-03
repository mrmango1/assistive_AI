import cv2
import pytesseract
import base64
import requests
from config import LANGUAGE, OPENAI_API_KEY, USE_OPENAI_OCR

def ocr_image_openai(image_path):
    """Extrae texto de una imagen usando la API de OpenAI GPT-4 Vision"""
    if not OPENAI_API_KEY:
        return "Error: No se encontró la clave API de OpenAI."
    
    try:
        with open(image_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode("utf-8")
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        data = {
            "model": "gpt-4.1-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "Extrae todo el texto visible en esta imagen. Devuelve únicamente el texto sin comentarios adicionales, manteniendo el formato y estructura original cuando sea posible."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 500
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            text = result["choices"][0]["message"]["content"]
            print(f"Texto extraído con OpenAI: {text}")
            return text.strip()
        else:
            print(f"Error en API OpenAI para OCR: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return "Error al extraer texto con inteligencia artificial."
            
    except FileNotFoundError:
        return "Error: No se pudo encontrar el archivo de imagen."
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión en OCR OpenAI: {e}")
        return "Error de conexión al servicio de extracción de texto."
    except Exception as e:
        print(f"Error inesperado en ocr_image_openai: {e}")
        return "Error inesperado al extraer texto de la imagen."

def ocr_image_tesseract(filename):
    """Extrae texto usando pytesseract (método tradicional)"""
    try:
        image = cv2.imread(filename)
        if image is None:
            return "Error: No se pudo cargar la imagen."
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, lang=LANGUAGE)
        return text.strip()
    except Exception as e:
        print(f"Error en OCR con tesseract: {e}")
        return "Error al extraer texto con tesseract."

def ocr_image(filename):
    """Función principal de OCR que usa el método configurado"""
    if USE_OPENAI_OCR:
        print("Usando OpenAI para OCR...")
        return ocr_image_openai(filename)
    else:
        print("Usando Tesseract para OCR...")
        return ocr_image_tesseract(filename)