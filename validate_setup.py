#!/usr/bin/env python3
"""
Simple validation script for the Assistive AI application
Tests core functionality without heavy dependencies
"""
import sys
import os

def test_config():
    """Test configuration loading"""
    try:
        import config
        print("✅ Config loaded successfully")
        print(f"   - OpenAI OCR: {config.USE_OPENAI_OCR}")
        print(f"   - OpenAI TTS: {config.USE_OPENAI_TTS}")
        print(f"   - TTS Voice: {config.OPENAI_TTS_VOICE}")
        print(f"   - API Key set: {'Yes' if config.OPENAI_API_KEY else 'No (set OPENAI_API_KEY env var)'}")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_commands():
    """Test commands loading"""
    try:
        import json
        if os.path.exists('commands.json'):
            with open('commands.json', 'r', encoding='utf-8') as f:
                commands = json.load(f)
            print("✅ Commands loaded successfully")
            print(f"   - Available commands: {list(commands.keys())}")
            return True
        else:
            print("❌ commands.json not found")
            return False
    except Exception as e:
        print(f"❌ Commands test failed: {e}")
        return False

def test_imports():
    """Test critical imports"""
    modules = [
        ('requests', 'HTTP requests'),
        ('json', 'JSON handling'),
        ('threading', 'Threading support'),
        ('pathlib', 'Path handling'),
        ('difflib', 'Fuzzy matching'),
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
    """Test OpenAI integration (without making API calls)"""
    try:
        import openai
        print("✅ OpenAI SDK available")
        
        import config
        if config.OPENAI_API_KEY and config.OPENAI_API_KEY != "your_openai_api_key_here":
            print("✅ OpenAI API key is configured")
        else:
            print("⚠️  OpenAI API key not set - OpenAI features will be disabled")
        
        return True
    except ImportError:
        print("❌ OpenAI SDK not installed")
        return False

def test_directories():
    """Test required directories"""
    directories = ['temp', 'audio', 'vision', 'utils']
    all_good = True
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ {directory}/ directory exists")
        else:
            print(f"❌ {directory}/ directory missing")
            all_good = False
    
    return all_good

def main():
    """Run all tests"""
    print("🔍 Validating Assistive AI Voice Application Setup")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Commands", test_commands),
        ("Core Imports", test_imports),
        ("OpenAI Integration", test_openai_integration),
        ("Directory Structure", test_directories),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"   ⚠️  {test_name} test had issues")
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work correctly.")
        print("\n📌 Next steps:")
        print("   1. Set OPENAI_API_KEY environment variable or create .env file")
        print("   2. Run: python main.py")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
