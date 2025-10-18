using System;
using System.Collections;
using UnityEngine;

public class ForgetMeNotManager : MonoBehaviour
{
    [Header("Component References")]
    public APIClient apiClient;
    public CameraCapture cameraCapture;
    public AudioRecorder audioRecorder;
    public ControllerInputHandler controllerInput;
    public UIManager uiManager;
    
    [Header("Settings")]
    public float minRecordingDuration = 1.0f;
    public float maxRecordingDuration = 60.0f;
    
    [Header("Debug")]
    public bool enableDebugLogs = true;
    
    // Application state
    public enum AppState
    {
        Idle,
        Recording,
        Processing,
        Error
    }
    
    private AppState currentState = AppState.Idle;
    private float recordingStartTime;
    private bool isBackendConnected = false;
    
    // Events
    public event Action<AppState> OnStateChanged;
    
    private void Start()
    {
        InitializeComponents();
        StartCoroutine(InitializeApplication());
    }
    
    private void InitializeComponents()
    {
        // Find components if not assigned
        if (apiClient == null) apiClient = FindObjectOfType<APIClient>();
        if (cameraCapture == null) cameraCapture = FindObjectOfType<CameraCapture>();
        if (audioRecorder == null) audioRecorder = FindObjectOfType<AudioRecorder>();
        if (controllerInput == null) controllerInput = FindObjectOfType<ControllerInputHandler>();
        if (uiManager == null) uiManager = FindObjectOfType<UIManager>();
        
        // Subscribe to controller events
        if (controllerInput != null)
        {
            controllerInput.OnStartEnrollmentPressed += HandleStartEnrollment;
            controllerInput.OnStopEnrollmentPressed += HandleStopEnrollment;
            controllerInput.OnRecallPressed += HandleRecall;
        }
        
        Log("Components initialized");
    }
    
    private IEnumerator InitializeApplication()
    {
        SetState(AppState.Processing);
        uiManager?.ShowProcessingStatus("initializing");
        
        // Test backend connection
        yield return StartCoroutine(TestBackendConnection());
        
        if (isBackendConnected)
        {
            SetState(AppState.Idle);
            uiManager?.ShowInfo("Ready - Press A to start enrollment, X to recall");
        }
        else
        {
            SetState(AppState.Error);
            uiManager?.ShowError("Backend connection failed");
        }
    }
    
    private IEnumerator TestBackendConnection()
    {
        bool connectionSuccess = false;
        yield return StartCoroutine(apiClient.TestConnection(success => connectionSuccess = success));
        isBackendConnected = connectionSuccess;
    }
    
    private void Log(string message)
    {
        if (enableDebugLogs)
        {
            Debug.Log($"[ForgetMeNotManager] {message}");
        }
    }
    
    private void LogError(string message)
    {
        Debug.LogError($"[ForgetMeNotManager] {message}");
    }
    
    private void SetState(AppState newState)
    {
        if (currentState != newState)
        {
            currentState = newState;
            OnStateChanged?.Invoke(currentState);
            Log($"State changed to: {currentState}");
        }
    }
    
    private void HandleStartEnrollment()
    {
        if (currentState != AppState.Idle)
        {
            Log("Cannot start enrollment - not in idle state");
            return;
        }
        
        Log("Starting enrollment process");
        StartCoroutine(StartEnrollmentProcess());
    }
    
    private IEnumerator StartEnrollmentProcess()
    {
        SetState(AppState.Processing);
        uiManager?.ShowProcessingStatus("capturing image");
        
        // Capture image
        byte[] imageData = cameraCapture.CapturePassthroughSnapshot();
        if (imageData == null)
        {
            LogError("Failed to capture image");
            uiManager?.ShowError("Failed to capture image");
            SetState(AppState.Error);
            yield break;
        }
        
        // Start audio recording
        if (!audioRecorder.StartRecording())
        {
            LogError("Failed to start audio recording");
            uiManager?.ShowError("Failed to start audio recording");
            SetState(AppState.Error);
            yield break;
        }
        
        SetState(AppState.Recording);
        recordingStartTime = Time.time;
        uiManager?.ShowRecordingStatus(0f);
        
        Log("Enrollment started - recording audio");
    }
    
    private void HandleStopEnrollment()
    {
        if (currentState != AppState.Recording)
        {
            Log("Cannot stop enrollment - not recording");
            return;
        }
        
        Log("Stopping enrollment process");
        StartCoroutine(StopEnrollmentProcess());
    }
    
    private IEnumerator StopEnrollmentProcess()
    {
        SetState(AppState.Processing);
        uiManager?.ShowProcessingStatus("stopping recording");
        
        // Stop audio recording
        byte[] audioData = audioRecorder.StopRecordingAndGetData();
        if (audioData == null)
        {
            LogError("Failed to get audio data");
            uiManager?.ShowError("Failed to get audio data");
            SetState(AppState.Error);
            yield break;
        }
        
        float recordingDuration = Time.time - recordingStartTime;
        if (recordingDuration < minRecordingDuration)
        {
            LogError($"Recording too short: {recordingDuration:F1}s");
            uiManager?.ShowError($"Recording too short (minimum {minRecordingDuration}s)");
            SetState(AppState.Error);
            yield break;
        }
        
        // Capture final image
        uiManager?.ShowProcessingStatus("capturing final image");
        byte[] finalImageData = cameraCapture.CapturePassthroughSnapshot();
        if (finalImageData == null)
        {
            LogError("Failed to capture final image");
            uiManager?.ShowError("Failed to capture final image");
            SetState(AppState.Error);
            yield break;
        }
        
        // Send enrollment request
        uiManager?.ShowProcessingStatus("sending to server");
        yield return StartCoroutine(apiClient.EnrollPerson(finalImageData, audioData, HandleEnrollmentResponse));
    }
    
    private void HandleEnrollmentResponse(EnrollResponse response)
    {
        if (response.IsSuccess || response.IsAlreadyEnrolled)
        {
            Log($"Enrollment successful: {response.person_id}");
            uiManager?.ShowEnrollmentResult(response.person_id, response.summary, true);
            SetState(AppState.Idle);
        }
        else
        {
            LogError($"Enrollment failed: {response.message}");
            uiManager?.ShowError($"Enrollment failed: {response.message}");
            SetState(AppState.Error);
        }
    }
    
    private void HandleRecall()
    {
        if (currentState != AppState.Idle)
        {
            Log("Cannot start recall - not in idle state");
            return;
        }
        
        Log("Starting recall process");
        StartCoroutine(StartRecallProcess());
    }
    
    private IEnumerator StartRecallProcess()
    {
        SetState(AppState.Processing);
        uiManager?.ShowProcessingStatus("capturing image");
        
        // Capture image
        byte[] imageData = cameraCapture.CapturePassthroughSnapshot();
        if (imageData == null)
        {
            LogError("Failed to capture image");
            uiManager?.ShowError("Failed to capture image");
            SetState(AppState.Error);
            yield break;
        }
        
        // Send recall request
        uiManager?.ShowProcessingStatus("searching database");
        yield return StartCoroutine(apiClient.RecallPerson(imageData, HandleRecallResponse));
    }
    
    private void HandleRecallResponse(RecallResponse response)
    {
        if (response.IsMatch)
        {
            Log($"Person found: {response.person_id} (confidence: {response.confidence})");
            uiManager?.ShowRecallResult(response.person_id, response.summary, response.confidence, true);
        }
        else if (response.IsNoMatch)
        {
            Log("No matching person found");
            uiManager?.ShowRecallResult("", "", 0f, false);
        }
        else
        {
            LogError($"Recall failed: {response.message}");
            uiManager?.ShowError($"Recall failed: {response.message}");
        }
        
        SetState(AppState.Idle);
    }
    
    private void Update()
    {
        // Update recording status if recording
        if (currentState == AppState.Recording)
        {
            float recordingDuration = Time.time - recordingStartTime;
            uiManager?.ShowRecordingStatus(recordingDuration);
            
            // Auto-stop if max duration reached
            if (recordingDuration >= maxRecordingDuration)
            {
                HandleStopEnrollment();
            }
        }
    }
    
    /// <summary>
    /// Get current application state
    /// </summary>
    public AppState GetCurrentState()
    {
        return currentState;
    }
    
    /// <summary>
    /// Check if backend is connected
    /// </summary>
    public bool IsBackendConnected()
    {
        return isBackendConnected;
    }
    
    /// <summary>
    /// Force reset to idle state
    /// </summary>
    public void ResetToIdle()
    {
        if (currentState == AppState.Recording)
        {
            audioRecorder.StopRecordingAndGetData();
        }
        
        SetState(AppState.Idle);
        uiManager?.ShowInfo("Ready - Press A to start enrollment, X to recall");
    }
    
    /// <summary>
    /// Test backend connection manually
    /// </summary>
    public void TestConnection()
    {
        StartCoroutine(TestBackendConnection());
    }
    
    private void OnDestroy()
    {
        // Unsubscribe from events
        if (controllerInput != null)
        {
            controllerInput.OnStartEnrollmentPressed -= HandleStartEnrollment;
            controllerInput.OnStopEnrollmentPressed -= HandleStopEnrollment;
            controllerInput.OnRecallPressed -= HandleRecall;
        }
    }
}
