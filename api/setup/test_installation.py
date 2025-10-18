"""
Test script to verify Forget Me Not Backend installation
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        import face_recognition
        print("✓ face_recognition imported successfully")
    except ImportError as e:
        print(f"✗ face_recognition import failed: {e}")
        return False
    
    try:
        import whisper
        print("✓ Whisper imported successfully")
    except ImportError as e:
        print(f"✗ Whisper import failed: {e}")
        return False
    
    try:
        import numpy
        print("✓ NumPy imported successfully")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    try:
        import requests
        print("✓ Requests imported successfully")
    except ImportError as e:
        print(f"✗ Requests import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow imported successfully")
    except ImportError as e:
        print(f"✗ Pillow import failed: {e}")
        return False
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
    except ImportError as e:
        print(f"✗ OpenCV import failed: {e}")
        return False
    
    return True

def test_face_recognition():
    """Test face recognition functionality."""
    print("\nTesting face recognition...")
    
    try:
        import face_recognition
        import numpy as np
        
        # Create a simple test image (dummy)
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # This will fail to find a face, but should not crash
        face_locations = face_recognition.face_locations(test_image)
        print("✓ Face recognition library working (no face found in test image - expected)")
        return True
        
    except Exception as e:
        print(f"✗ Face recognition test failed: {e}")
        return False

def test_whisper():
    """Test Whisper model loading."""
    print("\nTesting Whisper...")
    
    try:
        import whisper
        
        # Try to load the base model
        print("Loading Whisper base model...")
        model = whisper.load_model("base")
        print("✓ Whisper model loaded successfully")
        return True
        
    except Exception as e:
        print(f"✗ Whisper test failed: {e}")
        return False

def test_modules():
    """Test our custom modules."""
    print("\nTesting custom modules...")
    
    try:
        from face_recognition_module import FaceRecognitionManager
        print("✓ FaceRecognitionManager imported successfully")
        
        face_manager = FaceRecognitionManager()
        print("✓ FaceRecognitionManager initialized successfully")
        
    except Exception as e:
        print(f"✗ FaceRecognitionManager test failed: {e}")
        return False
    
    try:
        from llm_audio_module import LLMAudioProcessor
        print("✓ LLMAudioProcessor imported successfully")
        
        # Don't initialize as it loads Whisper model
        print("✓ LLMAudioProcessor class available")
        
    except Exception as e:
        print(f"✗ LLMAudioProcessor test failed: {e}")
        return False
    
    try:
        from database_manager import DatabaseManager
        print("✓ DatabaseManager imported successfully")
        
        db_manager = DatabaseManager()
        print("✓ DatabaseManager initialized successfully")
        
    except Exception as e:
        print(f"✗ DatabaseManager test failed: {e}")
        return False
    
    return True

def test_directories():
    """Test if required directories exist."""
    print("\nTesting directories...")
    
    required_dirs = ['uploads']
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✓ Directory '{directory}' exists")
        else:
            print(f"✗ Directory '{directory}' missing")
            return False
    
    return True

def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from config import Config
        print("✓ Config imported successfully")
        
        # Test configuration validation
        Config.validate_config()
        print("✓ Configuration validated successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Forget Me Not Backend Installation\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Directory Tests", test_directories),
        ("Configuration Tests", test_config),
        ("Module Tests", test_modules),
        ("Face Recognition Tests", test_face_recognition),
        ("Whisper Tests", test_whisper),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 All tests passed! Your installation is ready.")
        print("\nNext steps:")
        print("1. Edit .env file and add your Llama API key (optional)")
        print("2. Run: python api.py")
        print("3. Find your IP address and share with Unity developer")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("You may need to:")
        print("- Run setup.py again")
        print("- Install missing dependencies manually")
        print("- Check your Python version (3.8+ required)")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
