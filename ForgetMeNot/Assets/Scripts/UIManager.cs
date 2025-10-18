using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class UIManager : MonoBehaviour
{
    [Header("UI References")]
    public Canvas worldSpaceCanvas;
    public TextMeshProUGUI statusText;
    public TextMeshProUGUI summaryText;
    public Image statusBackground;
    public Image summaryBackground;
    
    [Header("UI Settings")]
    public float fadeInDuration = 0.5f;
    public float fadeOutDuration = 0.3f;
    public Color successColor = Color.green;
    public Color errorColor = Color.red;
    public Color warningColor = Color.yellow;
    public Color infoColor = Color.blue;
    
    [Header("Debug")]
    public bool enableDebugLogs = true;
    
    private Camera playerCamera;
    private Coroutine fadeCoroutine;
    
    private void Start()
    {
        InitializeUI();
    }
    
    private void InitializeUI()
    {
        // Find the player camera
        playerCamera = Camera.main;
        if (playerCamera == null)
        {
            playerCamera = FindObjectOfType<Camera>();
        }
        
        // Position UI in front of camera
        if (playerCamera != null)
        {
            PositionUIInFrontOfCamera();
        }
        
        // Set initial state
        SetStatus("Ready", infoColor);
        SetSummary("");
        
        Log("UI Manager initialized");
    }
    
    private void PositionUIInFrontOfCamera()
    {
        if (worldSpaceCanvas != null && playerCamera != null)
        {
            // Position canvas 2 units in front of camera
            Vector3 cameraPosition = playerCamera.transform.position;
            Vector3 cameraForward = playerCamera.transform.forward;
            Vector3 uiPosition = cameraPosition + cameraForward * Config.UI_DISTANCE;
            uiPosition.y += Config.UI_HEIGHT;
            
            worldSpaceCanvas.transform.position = uiPosition;
            worldSpaceCanvas.transform.LookAt(cameraPosition);
            worldSpaceCanvas.transform.Rotate(0, 180, 0); // Face the camera
        }
    }
    
    private void Log(string message)
    {
        if (enableDebugLogs)
        {
            Debug.Log($"[UIManager] {message}");
        }
    }
    
    /// <summary>
    /// Set the status text with color
    /// </summary>
    public void SetStatus(string message, Color color)
    {
        if (statusText != null)
        {
            statusText.text = message;
            statusText.color = color;
        }
        
        if (statusBackground != null)
        {
            statusBackground.color = new Color(color.r, color.g, color.b, 0.3f);
        }
        
        Log($"Status updated: {message}");
    }
    
    /// <summary>
    /// Set the summary text
    /// </summary>
    public void SetSummary(string summary)
    {
        if (summaryText != null)
        {
            summaryText.text = summary;
        }
        
        Log($"Summary updated: {summary.Length} characters");
    }
    
    /// <summary>
    /// Show a success message
    /// </summary>
    public void ShowSuccess(string message)
    {
        SetStatus(message, successColor);
        TriggerHapticFeedback();
    }
    
    /// <summary>
    /// Show an error message
    /// </summary>
    public void ShowError(string message)
    {
        SetStatus(message, errorColor);
        TriggerHapticFeedback();
    }
    
    /// <summary>
    /// Show a warning message
    /// </summary>
    public void ShowWarning(string message)
    {
        SetStatus(message, warningColor);
    }
    
    /// <summary>
    /// Show an info message
    /// </summary>
    public void ShowInfo(string message)
    {
        SetStatus(message, infoColor);
    }
    
    /// <summary>
    /// Show recording status
    /// </summary>
    public void ShowRecordingStatus(float duration)
    {
        SetStatus($"Recording... {duration:F1}s", warningColor);
    }
    
    /// <summary>
    /// Show processing status
    /// </summary>
    public void ShowProcessingStatus(string operation)
    {
        SetStatus($"Processing {operation}...", infoColor);
    }
    
    /// <summary>
    /// Show enrollment result
    /// </summary>
    public void ShowEnrollmentResult(string personId, string summary, bool isSuccess)
    {
        if (isSuccess)
        {
            SetStatus("Person enrolled successfully!", successColor);
            SetSummary($"Person ID: {personId}\n\nSummary: {summary}");
        }
        else
        {
            SetStatus("Enrollment failed", errorColor);
            SetSummary(summary);
        }
    }
    
    /// <summary>
    /// Show recall result
    /// </summary>
    public void ShowRecallResult(string personId, string summary, float confidence, bool isMatch)
    {
        if (isMatch)
        {
            SetStatus($"Person found! (Confidence: {confidence:P0})", successColor);
            SetSummary($"Person ID: {personId}\n\nSummary: {summary}");
        }
        else
        {
            SetStatus("Person not recognized", errorColor);
            SetSummary("No matching person found in database");
        }
    }
    
    /// <summary>
    /// Show network error
    /// </summary>
    public void ShowNetworkError(string error)
    {
        SetStatus("Connection Error", errorColor);
        SetSummary($"Failed to connect to server:\n{error}");
    }
    
    /// <summary>
    /// Clear the summary
    /// </summary>
    public void ClearSummary()
    {
        SetSummary("");
    }
    
    /// <summary>
    /// Fade in the UI
    /// </summary>
    public void FadeIn()
    {
        if (fadeCoroutine != null)
        {
            StopCoroutine(fadeCoroutine);
        }
        fadeCoroutine = StartCoroutine(FadeUI(0f, 1f, fadeInDuration));
    }
    
    /// <summary>
    /// Fade out the UI
    /// </summary>
    public void FadeOut()
    {
        if (fadeCoroutine != null)
        {
            StopCoroutine(fadeCoroutine);
        }
        fadeCoroutine = StartCoroutine(FadeUI(1f, 0f, fadeOutDuration));
    }
    
    private System.Collections.IEnumerator FadeUI(float startAlpha, float endAlpha, float duration)
    {
        CanvasGroup canvasGroup = worldSpaceCanvas.GetComponent<CanvasGroup>();
        if (canvasGroup == null)
        {
            canvasGroup = worldSpaceCanvas.gameObject.AddComponent<CanvasGroup>();
        }
        
        float elapsed = 0f;
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float alpha = Mathf.Lerp(startAlpha, endAlpha, elapsed / duration);
            canvasGroup.alpha = alpha;
            yield return null;
        }
        
        canvasGroup.alpha = endAlpha;
        fadeCoroutine = null;
    }
    
    private void TriggerHapticFeedback()
    {
        // Trigger haptic feedback on controllers
        OVRInput.SetControllerVibration(0.5f, 0.5f, OVRInput.Controller.RTouch);
        OVRInput.SetControllerVibration(0.5f, 0.5f, OVRInput.Controller.LTouch);
        
        // Stop haptic after short duration
        Invoke(nameof(StopHapticFeedback), 0.1f);
    }
    
    private void StopHapticFeedback()
    {
        OVRInput.SetControllerVibration(0f, 0f, OVRInput.Controller.RTouch);
        OVRInput.SetControllerVibration(0f, 0f, OVRInput.Controller.LTouch);
    }
    
    /// <summary>
    /// Update UI position to follow camera
    /// </summary>
    public void UpdateUIPosition()
    {
        if (playerCamera != null)
        {
            PositionUIInFrontOfCamera();
        }
    }
    
    /// <summary>
    /// Check if UI is ready
    /// </summary>
    public bool IsReady()
    {
        return worldSpaceCanvas != null && statusText != null && summaryText != null;
    }
    
    private void Update()
    {
        // Update UI position to follow camera
        if (playerCamera != null)
        {
            UpdateUIPosition();
        }
    }
}
