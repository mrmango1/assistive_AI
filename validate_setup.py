#!/usr/bin/env python3
"""
Script de validación simple para la aplicación de IA Asistiva
Prueba la funcionalidad principal sin dependencias pesadas
"""
import sys
import os

def test_config():
    """Probar carga de configuración"""
    try:
        import config
        print("✅ Configuración cargada exitosamente")
        print(f"   - OCR OpenAI: {config.USE_OPENAI_OCR}")
        print(f"   - TTS OpenAI: {config.USE_OPENAI_TTS}")
        print(f"   - Voz TTS: {config.OPENAI_TTS_VOICE}")
        print(f"   - Clave API configurada: {'Sí' if config.OPENAI_API_KEY else 'No (configura variable OPENAI_API_KEY)'}")
        return True
    except Exception as e:
        print(f"❌ Prueba de configuración falló: {e}")
        return False

def test_commands():
    """Probar carga de comandos"""
    try:
        import json
        if os.path.exists('commands.json'):
            with open('commands.json', 'r', encoding='utf-8') as f:
                commands = json.load(f)
            print("✅ Comandos cargados exitosamente")
            print(f"   - Comandos disponibles: {list(commands.keys())}")
            return True
        else:
            print("❌ commands.json no encontrado")
            return False
    except Exception as e:
        print(f"❌ Prueba de comandos falló: {e}")
        return False

def test_imports():
    """Probar importaciones críticas"""
    modules = [
        ('requests', 'Peticiones HTTP'),
        ('json', 'Manejo de JSON'),
        ('threading', 'Soporte de hilos'),
        ('pathlib', 'Manejo de rutas'),
        ('difflib', 'Coincidencias difusas'),
    ]
    
    all_good = True
    for module, description in modules:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
        except ImportError as e:
            print(f"❌ {module} - {description}: {e}")
            all_good = False
    
    return all_good

def test_openai_integration():
    """Probar integración con OpenAI (sin hacer llamadas a la API)"""
    try:
        import openai
        print("✅ SDK de OpenAI disponible")
        
        import config
        if config.OPENAI_API_KEY and config.OPENAI_API_KEY != "your_openai_api_key_here":
            print("✅ Clave API de OpenAI está configurada")
        else:
            print("⚠️  Clave API de OpenAI no configurada - funciones de OpenAI estarán deshabilitadas")
        
        return True
    except ImportError:
        print("❌ SDK de OpenAI no instalado")
        return False

def test_directories():
    """Probar directorios requeridos"""
    directories = ['temp', 'audio', 'vision', 'utils']
    all_good = True
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ directorio {directory}/ existe")
        else:
            print(f"❌ directorio {directory}/ faltante")
            all_good = False
    
    return all_good

def main():
    """Ejecutar todas las pruebas"""
    print("🔍 Validando Configuración de la Aplicación de Voz Asistiva con IA")
    print("=" * 50)
    
    tests = [
        ("Configuración", test_config),
        ("Comandos", test_commands),
        ("Importaciones Principales", test_imports),
        ("Integración OpenAI", test_openai_integration),
        ("Estructura de Directorios", test_directories),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Probando {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"   ⚠️  Prueba de {test_name} tuvo problemas")
    
    print("\n" + "=" * 50)
    print(f"🎯 Resultados de Pruebas: {passed}/{total} pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! La aplicación debería funcionar correctamente.")
        print("\n📌 Próximos pasos:")
        print("   1. Configura la variable de entorno OPENAI_API_KEY o crea archivo .env")
        print("   2. Ejecuta: python main.py")
    else:
        print("⚠️  Algunas pruebas fallaron. Por favor revisa los problemas anteriores.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
