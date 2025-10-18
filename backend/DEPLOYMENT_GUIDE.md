# Forget Me Not Backend - Deployment Guide

This guide will help you set up and deploy the Forget Me Not backend server for communication with the Unity VR app on Meta Quest 3.

## Prerequisites

- Python 3.8 or higher
- Internet connection for downloading dependencies
- Meta Quest 3 and development computer on the same Wi-Fi network

## Quick Setup

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

## Manual Setup (Alternative)

If the setup script doesn't work, follow these manual steps:

### 1. Install System Dependencies

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install cmake (required for dlib/face_recognition)
brew install cmake
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y cmake build-essential
```

**Windows:**
- Install Visual Studio Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the backend directory:

```bash
# Forget Me Not Backend Configuration

# Llama API Configuration (Optional - will use fallback if not provided)
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

## Finding Your Computer's IP Address

The Unity app needs to connect to your computer's local IP address. Here's how to find it:

### macOS
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### Linux
```bash
hostname -I
```

### Windows
```bash
ipconfig | findstr IPv4
```

Look for an IP address like `192.168.1.xxx` or `10.0.0.xxx`. This is your local network IP.

## Network Configuration

### 1. Firewall Settings

Make sure your computer's firewall allows incoming connections on port 5000:

**macOS:**
- System Preferences → Security & Privacy → Firewall → Firewall Options
- Add Python or Terminal to allowed applications

**Windows:**
- Windows Defender Firewall → Allow an app through firewall
- Add Python.exe or create a rule for port 5000

**Linux:**
```bash
sudo ufw allow 5000
```

### 2. Router Configuration

Usually no router configuration is needed for local network communication, but if you have issues:

- Ensure both devices are on the same Wi-Fi network
- Check if your router has client isolation enabled (disable it)
- Some enterprise networks may block device-to-device communication

## Running the Server

1. **Activate the virtual environment** (if not already active):
   ```bash
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

2. **Start the server:**
   ```bash
   python api.py
   ```

3. **Verify the server is running:**
   - You should see output like:
     ```
     Starting Forget Me Not Backend Server...
     API Endpoints:
       POST /enroll - Enroll a new person (image + audio)
       POST /recall - Recall a person (image)
       GET /health - Health check
       GET /list_persons - List all enrolled persons (debug)
       POST /clear_database - Clear all data (debug)
     
     To access from Quest 3, find your computer's IP address and use:
       http://YOUR_IP_ADDRESS:5000
     * Running on all addresses (0.0.0.0)
     * Debug mode: on
     ```

4. **Test the server:**
   Open a web browser and go to: `http://YOUR_IP_ADDRESS:5000/health`
   You should see a JSON response with status "healthy"

## Unity App Configuration

Share this information with the Unity developer:

- **Server URL:** `http://YOUR_IP_ADDRESS:5000`
- **Endpoints:**
  - `POST /enroll` - For enrolling new persons (requires image + audio files)
  - `POST /recall` - For recalling persons (requires image file)
  - `GET /health` - For health checks

## API Endpoints Reference

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

### GET /health
**Purpose:** Check if server is running
**Output:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "service": "Forget Me Not Backend"
}
```

## Troubleshooting

### Server Won't Start
- Check if port 5000 is already in use: `lsof -i :5000` (macOS/Linux) or `netstat -an | findstr :5000` (Windows)
- Try a different port by setting `FLASK_PORT=5001` in your `.env` file

### Unity Can't Connect
- Verify both devices are on the same Wi-Fi network
- Check firewall settings
- Test with a web browser first: `http://YOUR_IP:5000/health`
- Try disabling Windows Defender or antivirus temporarily

### Face Recognition Issues
- Ensure images contain clear, well-lit faces
- Images should be at least 100x100 pixels
- Multiple faces in an image may cause issues

### Audio Processing Issues
- Ensure audio files are in supported formats (WAV, MP3, M4A)
- Audio should be at least 1 second long
- Clear speech works better than noisy environments

### Llama API Issues
- Check your API key is correct in `.env`
- Verify you have sufficient API credits
- The system will fall back to simple text truncation if Llama is unavailable

## Development Tips

### Debug Mode
- Set `FLASK_DEBUG=True` in `.env` for detailed error messages
- Server will auto-reload when you change code files

### Database Management
- Database is stored in `person_database.json`
- Use `GET /list_persons` to see all enrolled persons
- Use `POST /clear_database` to reset all data (debug only)

### Logs
- Server logs are printed to the console
- For production, consider using a proper logging framework

## Production Deployment

For production deployment:

1. Set `FLASK_DEBUG=False` in `.env`
2. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 api:app
   ```
3. Set up proper logging and monitoring
4. Use HTTPS with SSL certificates
5. Implement proper authentication if needed

## Support

If you encounter issues:
1. Check the console output for error messages
2. Verify network connectivity between devices
3. Test individual components (face recognition, audio processing)
4. Check the troubleshooting section above
