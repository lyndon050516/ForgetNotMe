"""
Configuration file for Forget Me Not Backend
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Server Configuration
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # API Configuration - Groq
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_API_URL = os.getenv('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.1-70b-versatile')
    
    # Face Recognition Configuration
    FACE_CONFIDENCE_THRESHOLD = float(os.getenv('FACE_CONFIDENCE_THRESHOLD', 0.6))
    
    # Database Configuration
    DATABASE_FILE = os.getenv('DATABASE_FILE', 'person_database.json')
    
    # Upload Configuration
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 16))
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'wav', 'mp3', 'm4a'}
    
    # Whisper Model Configuration
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')  # tiny, base, small, medium, large
    
    @classmethod
    def validate_config(cls):
        """Validate configuration and print warnings."""
        warnings = []
        
        if not cls.GROQ_API_KEY:
            warnings.append("GROQ_API_KEY not set - will use fallback text processing")
        
        if not os.path.exists(cls.UPLOAD_FOLDER):
            os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
            print(f"Created upload directory: {cls.UPLOAD_FOLDER}")
        
        if warnings:
            print("Configuration warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        else:
            print(f"Configuration validated successfully (using Groq model: {cls.GROQ_MODEL})")
        
        return len(warnings) == 0
