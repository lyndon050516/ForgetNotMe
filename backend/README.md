# Forget Me Not Backend

A proof-of-concept productivity tool backend for Meta Quest 3 that leverages Passthrough and Llama APIs to enhance human memory. This backend handles face recognition, audio transcription, and conversation summarization for the Unity VR application.

## 🚀 Quick Start

1. **Run the setup script:**
   ```bash
   python setup.py
   ```

2. **Activate the virtual environment:**
   - **macOS/Linux:** `source venv/bin/activate`
   - **Windows:** `venv\Scripts\activate`

3. **Start the server:**
   ```bash
   python api.py
   ```

4. **Test the installation:**
   ```bash
   python test_installation.py
   ```

## 📋 API Contract

The backend provides two main endpoints for the Unity VR application:

### POST /enroll
**Purpose:** Enroll a new person with face and conversation data
**Input:** 
- `image` (file): Face image (PNG/JPG/JPEG)
- `audio` (file): Conversation audio (WAV/MP3/M4A)

**Output:**
```json
{
  "status": "success",
  "person_id": "unique-uuid-here",
  "summary": "Conversation summary..."
}
```

### POST /recall
**Purpose:** Recall a person from face image
**Input:**
- `image` (file): Face image (PNG/JPG/JPEG)

**Output (Match Found):**
```json
{
  "status": "match",
  "person_id": "unique-uuid-here",
  "confidence": 0.85,
  "summary": "Last time we talked about...",
  "enrolled_at": "2024-01-01T12:00:00"
}
```

**Output (No Match):**
```json
{
  "status": "no_match",
  "message": "No matching person found"
}
```

## 🏗️ Architecture

The backend is built with a modular architecture:

### Core Components

- **`api.py`** - Main Flask server with REST API endpoints
- **`face_recognition_module.py`** - Face embedding generation and similarity search
- **`llm_audio_module.py`** - Audio transcription (Whisper) and text summarization (Llama)
- **`database_manager.py`** - JSON-based storage for person data
- **`config.py`** - Configuration management

### Key Features

- **Face Recognition:** Uses `face_recognition` library for facial embedding generation
- **Audio Processing:** OpenAI Whisper for speech-to-text transcription
- **Text Summarization:** Llama API integration with fallback to simple text truncation
- **Database:** JSON file-based storage for person data and face embeddings
- **File Handling:** Secure file upload and validation
- **Error Handling:** Comprehensive error handling and logging

## 🔧 Configuration

Create a `.env` file with the following variables:

```bash
# Llama API Configuration (Optional)
LLAMA_API_KEY=your_llama_api_key_here
LLAMA_API_URL=https://api.llama-api.com/chat/completions

# Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True

# Face Recognition Configuration
FACE_CONFIDENCE_THRESHOLD=0.6

# Database Configuration
DATABASE_FILE=person_database.json

# Upload Configuration
MAX_FILE_SIZE_MB=16
UPLOAD_FOLDER=uploads
```

## 📁 Project Structure

```
backend/
├── api.py                      # Main Flask application
├── face_recognition_module.py  # Face recognition logic
├── llm_audio_module.py        # Audio processing and LLM integration
├── database_manager.py        # Data storage and retrieval
├── config.py                  # Configuration management
├── setup.py                   # Installation script
├── test_installation.py       # Installation verification
├── requirements.txt           # Python dependencies
├── DEPLOYMENT_GUIDE.md       # Detailed deployment instructions
├── README.md                 # This file
├── uploads/                  # File upload directory
├── person_database.json      # Person data storage (created at runtime)
└── venv/                     # Virtual environment (created by setup)
```

## 🌐 Network Setup

### Finding Your IP Address

**macOS:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Linux:**
```bash
hostname -I
```

**Windows:**
```bash
ipconfig | findstr IPv4
```

### Unity Configuration

Share your server URL with the Unity developer:
- **Server URL:** `http://YOUR_IP_ADDRESS:5000`
- **Health Check:** `http://YOUR_IP_ADDRESS:5000/health`

## 🔍 Debug Endpoints

The backend includes several debug endpoints for development:

- **GET /health** - Server health check
- **GET /list_persons** - List all enrolled persons
- **POST /clear_database** - Clear all data (debug only)

## 🛠️ Development

### Running in Development Mode

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Start server with debug mode
python api.py
```

### Testing

```bash
# Run installation tests
python test_installation.py

# Test API endpoints
curl http://localhost:5000/health
```

## 📦 Dependencies

Key dependencies include:

- **Flask** - Web framework
- **face_recognition** - Facial embedding generation
- **openai-whisper** - Speech-to-text transcription
- **requests** - HTTP client for Llama API
- **numpy** - Numerical computations
- **Pillow** - Image processing
- **opencv-python** - Computer vision

See `requirements.txt` for the complete list.

## 🔒 Security Considerations

- File upload validation and sanitization
- Secure filename handling
- Maximum file size limits
- CORS configuration for Unity app
- Error message sanitization

## 🚨 Troubleshooting

### Common Issues

1. **Port 5000 in use:** Change `FLASK_PORT` in `.env`
2. **Unity can't connect:** Check firewall settings and network connectivity
3. **Face recognition fails:** Ensure clear, well-lit faces in images
4. **Audio processing fails:** Check audio format and quality

### Getting Help

1. Check the console output for error messages
2. Verify network connectivity between devices
3. Test individual components using debug endpoints
4. Review the detailed `DEPLOYMENT_GUIDE.md`

## 📝 License

This project is part of the Forget Me Not proof-of-concept for Meta Quest 3.

## 🤝 Contributing

This is a proof-of-concept project. For production use, consider:

- Adding proper authentication
- Implementing HTTPS
- Using a production WSGI server
- Adding comprehensive logging
- Implementing data backup strategies
- Adding rate limiting
- Implementing proper error monitoring

---

**Ready to deploy?** Run `python setup.py` and follow the `DEPLOYMENT_GUIDE.md` for detailed instructions!
