# Forget Me Not - Unity VR Integration

This folder contains all the C# scripts for the Unity VR application that integrates with the Python Flask backend.

## Scripts Overview

### Core Components

- **`ForgetMeNotManager.cs`** - Main orchestrator that coordinates all components
- **`APIClient.cs`** - Handles HTTP communication with the Flask backend
- **`CameraCapture.cs`** - Captures passthrough camera snapshots
- **`AudioRecorder.cs`** - Records audio from Quest 3 microphone
- **`ControllerInputHandler.cs`** - Maps controller buttons to actions
- **`UIManager.cs`** - Manages world space UI display

### Data Models

- **`Models/EnrollResponse.cs`** - API response for enrollment requests
- **`Models/RecallResponse.cs`** - API response for recall requests
- **`Models/APIError.cs`** - Error handling for API responses

### Configuration

- **`Config.cs`** - Application settings and constants

## Setup Instructions

### 1. Scene Setup

1. Open the Unity scene
2. Add an empty GameObject and name it "ForgetMeNotManager"
3. Add the `ForgetMeNotManager` script to this GameObject
4. The manager will automatically find and configure all other components

### 2. Required GameObjects

The system expects these GameObjects in the scene:

- **OVRCameraRig** (from Meta XR SDK)
- **World Space Canvas** for UI display
- **TextMeshPro components** for status and summary text

### 3. Controller Button Mapping

- **Right Controller A Button**: Start enrollment (capture + record)
- **Right Controller B Button**: Stop enrollment (stop record + send)
- **Left Controller X Button**: Recall (capture + query)

### 4. Backend Connection

1. Start the Python Flask backend: `cd api && python api.py`
2. Verify backend is running at `http://localhost:5001/ping`
3. For Quest 3 deployment, update `Config.API_BASE_URL` to your Mac's IP address

## Workflow

### Enrollment Process
1. Press A button to start enrollment
2. System captures image and starts audio recording
3. Press B button to stop recording
4. System sends image + audio to `/enroll` endpoint
5. UI displays person ID and conversation summary

### Recall Process
1. Press X button to start recall
2. System captures image
3. System sends image to `/recall` endpoint
4. UI displays person match and previous conversation summary

## Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Check if Python backend is running
   - Verify network connectivity
   - Check firewall settings

2. **No Image Captured**
   - Ensure OVRCameraRig is in scene
   - Check camera permissions
   - Verify passthrough is enabled

3. **Audio Recording Failed**
   - Check microphone permissions
   - Verify audio device is available
   - Check Unity audio settings

4. **Controller Input Not Working**
   - Ensure OVRInput is properly configured
   - Check controller connection
   - Verify button mappings

### Debug Mode

Enable debug logs in each component to see detailed information about the process flow.

## Network Configuration

### Development (PC)
- Backend URL: `http://localhost:5001`
- No additional configuration needed

### Quest 3 Deployment
1. Find your Mac's IP address: `ifconfig | grep "inet " | grep -v 127.0.0.1`
2. Update `Config.API_BASE_URL` to `http://YOUR_IP:5001`
3. Ensure Mac and Quest 3 are on same Wi-Fi network
4. Allow port 5001 through Mac firewall

## File Formats

- **Images**: JPEG format (85% quality)
- **Audio**: WAV format (44.1kHz, 16-bit, mono)
- **API**: HTTP multipart/form-data

## Performance Notes

- Image resolution: 1280x720 (configurable)
- Max recording duration: 60 seconds
- Request timeout: 30 seconds
- UI updates at 60fps for smooth experience
