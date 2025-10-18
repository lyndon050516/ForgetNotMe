using UnityEngine;
using TMPro;

#if UNITY_EDITOR
using UnityEditor;
#endif

public class SceneSetupHelper : MonoBehaviour
{
    [Header("Auto Setup")]
    public bool autoSetupOnStart = true;
    
    [Header("UI Prefab")]
    public GameObject uiPrefab;
    
    private void Start()
    {
        if (autoSetupOnStart)
        {
            SetupScene();
        }
    }
    
    [ContextMenu("Setup Scene")]
    public void SetupScene()
    {
        Debug.Log("[SceneSetupHelper] Starting scene setup...");
        
        // 1. Find or create OVRCameraRig
        SetupCameraRig();
        
        // 2. Create UI Canvas
        SetupUI();
        
        // 3. Create ForgetMeNotManager
        SetupManager();
        
        Debug.Log("[SceneSetupHelper] Scene setup complete!");
    }
    
    private void SetupCameraRig()
    {
        // Look for existing OVRCameraRig
        GameObject cameraRig = GameObject.Find("OVRCameraRig");
        
        if (cameraRig == null)
        {
            Debug.LogWarning("[SceneSetupHelper] OVRCameraRig not found. Please add it from Meta XR SDK Building Blocks.");
        }
        else
        {
            Debug.Log("[SceneSetupHelper] OVRCameraRig found");
        }
    }
    
    private void SetupUI()
    {
        // Look for existing UI Canvas
        Canvas existingCanvas = FindObjectOfType<Canvas>();
        if (existingCanvas != null && existingCanvas.renderMode == RenderMode.WorldSpace)
        {
            Debug.Log("[SceneSetupHelper] World Space Canvas already exists");
            return;
        }
        
        // Create UI Canvas
        GameObject canvasGO = new GameObject("ForgetMeNotUI");
        Canvas canvas = canvasGO.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.WorldSpace;
        canvas.sortingOrder = 10;
        
        // Add CanvasScaler
        CanvasScaler scaler = canvasGO.AddComponent<CanvasScaler>();
        scaler.dynamicPixelsPerUnit = 10;
        
        // Add GraphicRaycaster
        canvasGO.AddComponent<GraphicRaycaster>();
        
        // Position canvas in front of camera
        Camera mainCamera = Camera.main;
        if (mainCamera != null)
        {
            Vector3 cameraPos = mainCamera.transform.position;
            Vector3 cameraForward = mainCamera.transform.forward;
            canvasGO.transform.position = cameraPos + cameraForward * 2f;
            canvasGO.transform.LookAt(cameraPos);
            canvasGO.transform.Rotate(0, 180, 0);
        }
        
        // Create status text
        GameObject statusGO = new GameObject("StatusText");
        statusGO.transform.SetParent(canvasGO.transform);
        TextMeshProUGUI statusText = statusGO.AddComponent<TextMeshProUGUI>();
        statusText.text = "Ready";
        statusText.fontSize = 24;
        statusText.color = Color.white;
        statusText.alignment = TextAlignmentOptions.Center;
        
        RectTransform statusRect = statusText.GetComponent<RectTransform>();
        statusRect.anchoredPosition = new Vector2(0, 100);
        statusRect.sizeDelta = new Vector2(400, 50);
        
        // Create summary text
        GameObject summaryGO = new GameObject("SummaryText");
        summaryGO.transform.SetParent(canvasGO.transform);
        TextMeshProUGUI summaryText = summaryGO.AddComponent<TextMeshProUGUI>();
        summaryText.text = "";
        summaryText.fontSize = 18;
        summaryText.color = Color.white;
        summaryText.alignment = TextAlignmentOptions.TopLeft;
        
        RectTransform summaryRect = summaryText.GetComponent<RectTransform>();
        summaryRect.anchoredPosition = new Vector2(0, 0);
        summaryRect.sizeDelta = new Vector2(600, 300);
        
        // Add UIManager component
        UIManager uiManager = canvasGO.AddComponent<UIManager>();
        uiManager.statusText = statusText;
        uiManager.summaryText = summaryText;
        uiManager.worldSpaceCanvas = canvas;
        
        Debug.Log("[SceneSetupHelper] UI Canvas created");
    }
    
    private void SetupManager()
    {
        // Look for existing ForgetMeNotManager
        ForgetMeNotManager existingManager = FindObjectOfType<ForgetMeNotManager>();
        if (existingManager != null)
        {
            Debug.Log("[SceneSetupHelper] ForgetMeNotManager already exists");
            return;
        }
        
        // Create ForgetMeNotManager
        GameObject managerGO = new GameObject("ForgetMeNotManager");
        ForgetMeNotManager manager = managerGO.AddComponent<ForgetMeNotManager>();
        
        // Add other required components
        managerGO.AddComponent<APIClient>();
        managerGO.AddComponent<CameraCapture>();
        managerGO.AddComponent<AudioRecorder>();
        managerGO.AddComponent<ControllerInputHandler>();
        
        Debug.Log("[SceneSetupHelper] ForgetMeNotManager created");
    }
    
#if UNITY_EDITOR
    [MenuItem("Forget Me Not/Setup Scene")]
    public static void SetupSceneFromMenu()
    {
        SceneSetupHelper helper = FindObjectOfType<SceneSetupHelper>();
        if (helper == null)
        {
            GameObject helperGO = new GameObject("SceneSetupHelper");
            helper = helperGO.AddComponent<SceneSetupHelper>();
        }
        
        helper.SetupScene();
    }
    
    [MenuItem("Forget Me Not/Test Backend Connection")]
    public static void TestBackendConnection()
    {
        APIClient apiClient = FindObjectOfType<APIClient>();
        if (apiClient == null)
        {
            Debug.LogError("APIClient not found in scene");
            return;
        }
        
        // This would need to be run in play mode
        Debug.Log("Backend connection test - run in play mode");
    }
#endif
}
