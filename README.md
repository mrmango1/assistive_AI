# 🦯 Assistive Voice App

Asistente de voz asistivo para personas ciegas. Usa comandos de voz en español para leer documentos o describir el entorno con ayuda de inteligencia artificial.

---

## ✅ Características

- **Reconocimiento de voz offline** con **Vosk** para escucha continua
- **OCR inteligente** con dos opciones:
  - **OpenAI GPT-4 Vision** (mayor precisión, requiere internet)
  - **Tesseract OCR** (funciona sin internet)
- **Descripción de escenas** mediante **OpenAI GPT-4 Vision**
- **Síntesis de voz avanzada** con tres opciones:
  - **OpenAI TTS** (voz natural de alta calidad)
  - **Coqui TTS** (voz neural offline)
  - **TTS del sistema** (espeak/say como fallback)
- **Detección automática de conectividad** con fallback inteligente
- **Comandos personalizables** con coincidencias aproximadas
- **Manejo inteligente de errores** y limpieza automática de archivos temporales

---

## 📦 Requisitos

- Python 3.10 o superior
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- Modelo Vosk en español
- Clave API de OpenAI (opcional, para mejor calidad)
- Librerías Python (ver `requirements.txt`)

---

## 🔧 Instalación

### 1. Clona el proyecto y entra al directorio

```bash
git clone https://github.com/tu-usuario/assistive_ai.git
cd assistive_ai
```

### 2. Crea y activa el entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 4. Instala Tesseract (requerido)

**En macOS:**

```bash
brew install tesseract
```

**En Raspberry Pi/Linux:**

```bash
sudo apt update && sudo apt install tesseract-ocr tesseract-ocr-spa
```

### 5. Instala herramientas de audio adicionales (opcional)

**En macOS:** Ya incluidas

**En Linux/Raspberry Pi:**

```bash
sudo apt install espeak espeak-data mpg123 ffmpeg
```

---

## 🎙️ Configuración de Vosk

1. Descarga el modelo en español desde:  
   [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)

   **Modelo recomendado:** `vosk-model-small-es-0.42`

2. Extrae el modelo y colócalo en la carpeta `models/`:

   ```
   assistive_ai/
   └── models/
       └── vosk-model-small-es-0.42/
           ├── am/
           ├── graph/
           ├── ivector/
           └── conf/
   ```

---

## 🤖 Configuración de OpenAI (Opcional)

Para mejor calidad en OCR, descripción de imágenes y síntesis de voz:

1. Obtén una clave API de [OpenAI](https://platform.openai.com/api-keys)

2. Configura la variable de entorno:

   ```bash
   export OPENAI_API_KEY="tu-clave-api-aqui"
   ```

3. O edita directamente `config.py`:

   ```python
   OPENAI_API_KEY = "tu-clave-api-aqui"
   ```

---

## ⚙️ Configuración Avanzada

Edita `config.py` para personalizar el comportamiento:

```python
# Configuración de OCR
USE_OPENAI_OCR = True    # False para usar solo Tesseract

# Configuración de TTS  
USE_OPENAI_TTS = True    # False para usar Coqui/Sistema

# Configuración de idioma
LANGUAGE = "spa"         # Idioma para Tesseract

# Timeouts
API_REQUEST_TIMEOUT = 30
INTERNET_CHECK_TIMEOUT = 3
```

---

## 🚀 Ejecución

```bash
python main.py
```

**Salida esperada:**

```
Iniciando asistente de voz...
Configuración - OCR: OpenAI
Configuración - TTS: OpenAI
Inicializando reconocedor de voz...
Modelo Vosk cargado exitosamente.
Configurando escucha de audio...
Escuchando continuamente con Vosk...
Asistente listo. Di un comando para comenzar.
```

---

## 🗣️ Comandos Disponibles

### Comandos por defecto

| Acción | Frases de ejemplo |
|--------|-------------------|
| **Leer documento** | "leer documento", "quiero que leas", "lee esto" |
| **Describir escena** | "describir escena", "qué ves", "dime qué hay aquí" |
| **Salir** | "salir", "terminar", "adiós", "cerrar" |

### Personalizar comandos

Crea o edita el archivo `commands.json`:

```json
{
  "read_document": [
    "leer documento", "quiero que leas", "puedes leer esto",
    "lee esto", "lee el documento", "leer texto"
  ],
  "describe_scene": [
    "describir escena", "qué ves", "descríbeme el lugar", 
    "describe la imagen", "qué hay aquí", "dime qué ves"
  ],
  "exit": ["salir", "terminar", "adiós", "bye", "cerrar"]
}
```

---

## 🔄 Modos de Funcionamiento

### Con Internet (Modo Completo)

- **OCR:** OpenAI GPT-4 Vision (alta precisión)
- **TTS:** OpenAI TTS (voz natural)
- **Descripción:** OpenAI GPT-4 Vision

### Sin Internet (Modo Offline)

- **OCR:** Tesseract (funcional)
- **TTS:** Coqui TTS o sistema (espeak/say)
- **Descripción:** No disponible

### Modo Híbrido

- El asistente detecta automáticamente la conectividad
- Cambia entre modos según disponibilidad
- Informa al usuario qué método está usando

---

## 🛠️ Resolución de Problemas

### Error de cámara

```bash
# Probar la cámara
python vision/camera.py
```

### Error de audio

```bash
# Verificar dispositivos de audio
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### Error de Tesseract

```bash
# Verificar instalación
tesseract --version
```

### Error de modelo Vosk

- Verifica que el modelo esté en `models/vosk-model-small-es-0.42/`
- Descarga de nuevo si es necesario

---

## 📁 Estructura del Proyecto

```
assistive_ai/
├── audio/
│   ├── recognizer.py      # Reconocimiento de voz con Vosk
│   └── speaker.py         # Síntesis de voz (OpenAI/Coqui/Sistema)
├── vision/
│   ├── camera.py          # Captura de imágenes
│   ├── ocr.py            # OCR (OpenAI/Tesseract)
│   └── describe.py       # Descripción de imágenes (OpenAI)
├── utils/
│   └── internet.py       # Verificación de conectividad
├── models/               # Modelos Vosk
├── temp/                 # Archivos temporales
├── config.py            # Configuración general
├── main.py              # Aplicación principal
├── commands.json        # Comandos personalizables
└── requirements.txt     # Dependencias
```

---

## 🔮 Características Avanzadas

- **Reconocimiento fuzzy:** Entiende comandos aunque no sean exactos
- **Ejecución concurrente:** Múltiples comandos con control de concurrencia  
- **Limpieza automática:** Elimina archivos temporales automáticamente
- **Fallback inteligente:** Cambia de método según disponibilidad
- **Configuración flexible:** Fácil personalización sin tocar código

---

## 📋 Dependencias Principales

```txt
vosk>=0.3.45
sounddevice>=0.4.6
opencv-python>=4.8.0
pytesseract>=0.3.10
requests>=2.31.0
TTS>=0.22.0
```

---

## 🎯 Casos de Uso

1. **Lectura de documentos:** Facturas, cartas, menús, etiquetas
2. **Descripción de entorno:** Identificar objetos, personas, texto
3. **Navegación asistida:** Descripción de espacios y obstáculos
4. **Accesibilidad diaria:** Herramienta de independencia personal

---

## 🚧 Limitaciones Actuales  

- La descripción de escenas requiere conexión a internet
- OpenAI TTS y OCR requieren clave API (con límites de uso)
- El modelo Vosk puede tener dificultades con acentos muy marcados
- La calidad del OCR depende de la iluminación y calidad de imagen
