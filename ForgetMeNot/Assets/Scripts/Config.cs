public static class Config
{
    // API Configuration
    public const string API_BASE_URL = "http://localhost:5001";
    public const int REQUEST_TIMEOUT = 30;
    
    // Recording Configuration
    public const int MAX_RECORDING_TIME = 60; // seconds
    public const int SAMPLE_RATE = 44100;
    public const int CHANNELS = 1; // Mono
    
    // Camera Configuration
    public const int CAMERA_WIDTH = 1280;
    public const int CAMERA_HEIGHT = 720;
    
    // UI Configuration
    public const float UI_DISTANCE = 2.0f; // Distance from camera
    public const float UI_HEIGHT = 0.0f; // Height offset from camera
    
    // Controller Button Mappings
    public const string START_ENROLLMENT_BUTTON = "A"; // Right controller A button
    public const string STOP_ENROLLMENT_BUTTON = "B"; // Right controller B button
    public const string RECALL_BUTTON = "X"; // Left controller X button
}
