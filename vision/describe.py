import base64
import requests
from config import OPENAI_API_KEY

def describe_image_openai(image_path):
    """Describe una imagen usando la API de OpenAI GPT-4 Vision"""
    if not OPENAI_API_KEY:
        return "Error: No se encontró la clave API de OpenAI."
    
    try:
        with open(image_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode("utf-8")
        
        # URL y estructura correcta para la API de OpenAI
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        data = {
            "model": "gpt-4.1-mini",  # Modelo correcto que soporta visión
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "Describe esta imagen de manera concisa y útil para una persona con discapacidad visual. Incluye elementos importantes, objetos, texto visible y el contexto general de la escena."
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
            "max_tokens": 300
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            description = result["choices"][0]["message"]["content"]
            print(f"Descripción generada: {description}")
            return description
        else:
            print(f"Error en API OpenAI: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return "Error al describir la imagen con inteligencia artificial."
            
    except FileNotFoundError:
        return "Error: No se pudo encontrar el archivo de imagen."
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return "Error de conexión al servicio de descripción."
    except Exception as e:
        print(f"Error inesperado en describe_image_openai: {e}")
        return "Error inesperado al describir la imagen."