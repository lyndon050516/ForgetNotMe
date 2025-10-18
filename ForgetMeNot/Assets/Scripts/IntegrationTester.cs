using System.Collections;
using UnityEngine;
using UnityEngine.UI;

public class IntegrationTester : MonoBehaviour
{
    [Header("Test Settings")]
    public bool enableAutoTest = false;
    public float testInterval = 10f;
    
    [Header("Test Results")]
    public Text testResultsText;
    
    [Header("Debug")]
    public bool enableDebugLogs = true;
    
    private ForgetMeNotManager manager;
    private APIClient apiClient;
    private bool isTestRunning = false;
    private int testStep = 0;
    private string testResults = "";
    
    private void Start()
    {
        manager = FindObjectOfType<ForgetMeNotManager>();
        apiClient = FindObjectOfType<APIClient>();
        
        if (enableAutoTest)
        {
            StartCoroutine(AutoTestSequence());
        }
    }
    
    private void Log(string message)
    {
        if (enableDebugLogs)
        {
            Debug.Log($"[IntegrationTester] {message}");
        }
    }
    
    private IEnumerator AutoTestSequence()
    {
        while (true)
        {
            yield return new WaitForSeconds(testInterval);
            
            if (!isTestRunning)
            {
                StartCoroutine(RunIntegrationTest());
            }
        }
    }
    
    [ContextMenu("Run Integration Test")]
    public void RunIntegrationTestManual()
    {
        StartCoroutine(RunIntegrationTest());
    }
    
    private IEnumerator RunIntegrationTest()
    {
        if (isTestRunning)
        {
            Log("Test already running");
            yield break;
        }
        
        isTestRunning = true;
        testStep = 0;
        testResults = "Integration Test Results:\n\n";
        
        Log("Starting integration test...");
        AddTestResult("Starting integration test...");
        
        // Test 1: Backend Connection
        yield return StartCoroutine(TestBackendConnection());
        
        // Test 2: Component Availability
        yield return StartCoroutine(TestComponentAvailability());
        
        // Test 3: Camera Capture
        yield return StartCoroutine(TestCameraCapture());
        
        // Test 4: Audio Recording
        yield return StartCoroutine(TestAudioRecording());
        
        // Test 5: Controller Input
        yield return StartCoroutine(TestControllerInput());
        
        // Test 6: UI System
        yield return StartCoroutine(TestUISystem());
        
        Log("Integration test completed");
        AddTestResult("Integration test completed");
        
        isTestRunning = false;
    }
    
    private IEnumerator TestBackendConnection()
    {
        testStep++;
        AddTestResult($"Step {testStep}: Testing backend connection...");
        
        bool connectionSuccess = false;
        yield return StartCoroutine(apiClient.TestConnection(success => connectionSuccess = success));
        
        if (connectionSuccess)
        {
            AddTestResult("✓ Backend connection successful");
        }
        else
        {
            AddTestResult("✗ Backend connection failed");
        }
    }
    
    private IEnumerator TestComponentAvailability()
    {
        testStep++;
        AddTestResult($"Step {testStep}: Testing component availability...");
        
        bool allComponentsFound = true;
        
        if (manager == null)
        {
            AddTestResult("✗ ForgetMeNotManager not found");
            allComponentsFound = false;
        }
        else
        {
            AddTestResult("✓ ForgetMeNotManager found");
        }
        
        if (apiClient == null)
        {
            AddTestResult("✗ APIClient not found");
            allComponentsFound = false;
        }
        else
        {
            AddTestResult("✓ APIClient found");
        }
        
        CameraCapture cameraCapture = FindObjectOfType<CameraCapture>();
        if (cameraCapture == null)
        {
            AddTestResult("✗ CameraCapture not found");
            allComponentsFound = false;
        }
        else
        {
            AddTestResult("✓ CameraCapture found");
        }
        
        AudioRecorder audioRecorder = FindObjectOfType<AudioRecorder>();
        if (audioRecorder == null)
        {
            AddTestResult("✗ AudioRecorder not found");
            allComponentsFound = false;
        }
        else
        {
            AddTestResult("✓ AudioRecorder found");
        }
        
        ControllerInputHandler controllerInput = FindObjectOfType<ControllerInputHandler>();
        if (controllerInput == null)
        {
            AddTestResult("✗ ControllerInputHandler not found");
            allComponentsFound = false;
        }
        else
        {
            AddTestResult("✓ ControllerInputHandler found");
        }
        
        UIManager uiManager = FindObjectOfType<UIManager>();
        if (uiManager == null)
        {
            AddTestResult("✗ UIManager not found");
            allComponentsFound = false;
        }
        else
        {
            AddTestResult("✓ UIManager found");
        }
        
        if (allComponentsFound)
        {
            AddTestResult("✓ All components available");
        }
        else
        {
            AddTestResult("✗ Some components missing");
        }
    }
    
    private IEnumerator TestCameraCapture()
    {
        testStep++;
        AddTestResult($"Step {testStep}: Testing camera capture...");
        
        CameraCapture cameraCapture = FindObjectOfType<CameraCapture>();
        if (cameraCapture == null)
        {
            AddTestResult("✗ CameraCapture not available");
            yield break;
        }
        
        if (!cameraCapture.IsReady())
        {
            AddTestResult("✗ CameraCapture not ready");
            yield break;
        }
        
        // Test capture
        byte[] imageData = cameraCapture.CapturePassthroughSnapshot();
        if (imageData != null && imageData.Length > 0)
        {
            AddTestResult($"✓ Camera capture successful ({imageData.Length} bytes)");
        }
        else
        {
            AddTestResult("✗ Camera capture failed");
        }
    }
    
    private IEnumerator TestAudioRecording()
    {
        testStep++;
        AddTestResult($"Step {testStep}: Testing audio recording...");
        
        AudioRecorder audioRecorder = FindObjectOfType<AudioRecorder>();
        if (audioRecorder == null)
        {
            AddTestResult("✗ AudioRecorder not available");
            yield break;
        }
        
        if (!audioRecorder.IsReady())
        {
            AddTestResult("✗ AudioRecorder not ready");
            yield break;
        }
        
        // Test recording start
        if (audioRecorder.StartRecording())
        {
            AddTestResult("✓ Audio recording started");
            
            // Record for 2 seconds
            yield return new WaitForSeconds(2f);
            
            // Test recording stop
            byte[] audioData = audioRecorder.StopRecordingAndGetData();
            if (audioData != null && audioData.Length > 0)
            {
                AddTestResult($"✓ Audio recording successful ({audioData.Length} bytes)");
            }
            else
            {
                AddTestResult("✗ Audio recording failed");
            }
        }
        else
        {
            AddTestResult("✗ Failed to start audio recording");
        }
    }
    
    private IEnumerator TestControllerInput()
    {
        testStep++;
        AddTestResult($"Step {testStep}: Testing controller input...");
        
        ControllerInputHandler controllerInput = FindObjectOfType<ControllerInputHandler>();
        if (controllerInput == null)
        {
            AddTestResult("✗ ControllerInputHandler not available");
            yield break;
        }
        
        if (controllerInput.AreControllersConnected())
        {
            AddTestResult("✓ Controllers connected");
        }
        else
        {
            AddTestResult("✗ No controllers connected");
        }
        
        // Test button mappings
        string mappingInfo = controllerInput.GetButtonMappingInfo();
        AddTestResult($"Button mappings:\n{mappingInfo}");
    }
    
    private IEnumerator TestUISystem()
    {
        testStep++;
        AddTestResult($"Step {testStep}: Testing UI system...");
        
        UIManager uiManager = FindObjectOfType<UIManager>();
        if (uiManager == null)
        {
            AddTestResult("✗ UIManager not available");
            yield break;
        }
        
        if (!uiManager.IsReady())
        {
            AddTestResult("✗ UIManager not ready");
            yield break;
        }
        
        // Test UI functions
        uiManager.ShowInfo("Test message");
        yield return new WaitForSeconds(0.5f);
        
        uiManager.ShowSuccess("Test success");
        yield return new WaitForSeconds(0.5f);
        
        uiManager.ShowError("Test error");
        yield return new WaitForSeconds(0.5f);
        
        uiManager.SetSummary("Test summary text");
        yield return new WaitForSeconds(0.5f);
        
        AddTestResult("✓ UI system functional");
    }
    
    private void AddTestResult(string result)
    {
        testResults += result + "\n";
        
        if (testResultsText != null)
        {
            testResultsText.text = testResults;
        }
        
        Log(result);
    }
    
    private void Update()
    {
        // Display test results in console
        if (testResultsText == null)
        {
            testResultsText = FindObjectOfType<Text>();
        }
    }
    
    [ContextMenu("Clear Test Results")]
    public void ClearTestResults()
    {
        testResults = "";
        if (testResultsText != null)
        {
            testResultsText.text = "";
        }
    }
}
