# Unity VR Integration Setup Guide

This guide will help you set up the Unity VR application to work with your Python Flask backend.

## Prerequisites

- Unity 2022.3 LTS or later
- Meta XR SDK v78.0.0 (already installed)
- Python Flask backend running on port 5001
- Meta Quest 3 headset (for final testing)

## Quick Setup

### 1. Backend Setup
```bash
# Navigate to the API directory
cd api

# Start the Flask backend
python api.py
```

Verify backend is running by visiting: http://localhost:5001/ping

### 2. Unity Scene Setup

#### Option A: Automatic Setup (Recommended)
1. Open Unity and load your project
2. In the Unity menu, go to **Forget Me Not > Setup Scene**
3. This will automatically create all required GameObjects and components

#### Option B: Manual Setup
1. Create an empty GameObject named "ForgetMeNotManager"
2. Add the `ForgetMeNotManager` script to it
3. The manager will automatically find and configure other components
4. Create a World Space Canvas for UI display
5. Add TextMeshPro components for status and summary text

### 3. Controller Button Mapping

The system uses these button mappings:
- **Right Controller A Button**: Start enrollment (capture image + start recording)
- **Right Controller B Button**: Stop enrollment (stop recording + send to API)
- **Left Controller X Button**: Recall (capture image + query API)

### 4. Testing

#### PC Testing (Editor Mode)
1. Press Play in Unity
2. Use the Integration Tester to verify all components work
3. Test button presses (simulated in editor)

#### Quest 3 Testing
1. Build and deploy to Quest 3
2. Update `Config.API_BASE_URL` to your Mac's IP address
3. Ensure both devices are on the same Wi-Fi network

## File Structure

```
Assets/Scripts/
├── ForgetMeNotManager.cs      # Main orchestrator
├── APIClient.cs              # Backend communication
├── CameraCapture.cs          # Passthrough camera capture
├── AudioRecorder.cs          # Microphone recording
├── ControllerInputHandler.cs # Button input handling
├── UIManager.cs              # World space UI
├── Config.cs                 # Configuration settings
├── SceneSetupHelper.cs       # Automatic scene setup
├── IntegrationTester.cs      # Testing utilities
├── Models/                   # Data models
│   ├── EnrollResponse.cs
│   ├── RecallResponse.cs
│   └── APIError.cs
└── README.md                 # Detailed documentation
```

## Configuration

### API Settings (Config.cs)
```csharp
public const string API_BASE_URL = "http://localhost:5001";  // Change for Quest 3
public const int REQUEST_TIMEOUT = 30;
public const int MAX_RECORDING_TIME = 60;
```

### Network Configuration for Quest 3
1. Find your Mac's IP address:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```
2. Update `Config.API_BASE_URL` to: `http://YOUR_IP:5001`
3. Allow port 5001 through Mac firewall

## Workflow

### Enrollment Process
1. **Press A Button**: Captures passthrough image and starts audio recording
2. **Press B Button**: Stops recording and sends both to `/enroll` endpoint
3. **Result**: UI displays person ID and conversation summary

### Recall Process
1. **Press X Button**: Captures passthrough image
2. **System**: Sends image to `/recall` endpoint
3. **Result**: UI displays person match and previous conversation

## Troubleshooting

### Common Issues

#### Backend Connection Failed
- Check if Python backend is running: `curl http://localhost:5001/ping`
- Verify network connectivity
- Check firewall settings

#### No Image Captured
- Ensure OVRCameraRig is in the scene
- Check camera permissions
- Verify passthrough is enabled

#### Audio Recording Failed
- Check microphone permissions
- Verify audio device is available
- Check Unity audio settings

#### Controller Input Not Working
- Ensure OVRInput is properly configured
- Check controller connection
- Verify button mappings in ControllerInputHandler

### Debug Mode
Enable debug logs in each component to see detailed information:
- `ForgetMeNotManager`: Main workflow logs
- `APIClient`: Network request logs
- `CameraCapture`: Image capture logs
- `AudioRecorder`: Audio recording logs
- `ControllerInputHandler`: Button input logs
- `UIManager`: UI update logs

## Testing

### Integration Test
1. Add `IntegrationTester` component to any GameObject
2. Right-click and select "Run Integration Test"
3. Check console for test results

### Manual Testing
1. Start backend: `python api.py`
2. Run Unity in Play mode
3. Test button presses
4. Check UI updates
5. Verify API communication

## Deployment

### Quest 3 Build
1. File > Build Settings
2. Select Android platform
3. Switch to Quest 3 device
4. Build and deploy
5. Update network configuration
6. Test on device

### Performance Optimization
- Image resolution: 1280x720 (configurable)
- Audio quality: 44.1kHz, 16-bit, mono
- Request timeout: 30 seconds
- Max recording: 60 seconds

## Support

For issues or questions:
1. Check the console logs
2. Run the integration test
3. Verify backend connectivity
4. Check component configuration

## Next Steps

1. **Test the complete workflow** with the backend running
2. **Deploy to Quest 3** and test on device
3. **Customize UI** and button mappings as needed
4. **Add error handling** for edge cases
5. **Optimize performance** for production use
