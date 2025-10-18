using System;
using UnityEngine;
using UnityEngine.Rendering;

public class CameraCapture : MonoBehaviour
{
    [Header("Camera Settings")]
    public Camera targetCamera;
    public int captureWidth = Config.CAMERA_WIDTH;
    public int captureHeight = Config.CAMERA_HEIGHT;
    
    [Header("Debug")]
    public bool enableDebugLogs = true;
    
    private RenderTexture renderTexture;
    private Texture2D captureTexture;
    
    private void Start()
    {
        InitializeCapture();
    }
    
    private void InitializeCapture()
    {
        // Create render texture for capture
        renderTexture = new RenderTexture(captureWidth, captureHeight, 24);
        renderTexture.Create();
        
        // Create texture for final capture
        captureTexture = new Texture2D(captureWidth, captureHeight, TextureFormat.RGB24, false);
        
        Log("Camera capture initialized");
    }
    
    private void Log(string message)
    {
        if (enableDebugLogs)
        {
            Debug.Log($"[CameraCapture] {message}");
        }
    }
    
    private void LogError(string message)
    {
        Debug.LogError($"[CameraCapture] {message}");
    }
    
    /// <summary>
    /// Capture a snapshot from the passthrough camera
    /// </summary>
    public byte[] CapturePassthroughSnapshot()
    {
        try
        {
            if (targetCamera == null)
            {
                // Try to find the main camera or OVRCameraRig camera
                targetCamera = Camera.main;
                if (targetCamera == null)
                {
                    targetCamera = FindObjectOfType<Camera>();
                }
            }
            
            if (targetCamera == null)
            {
                LogError("No camera found for capture");
                return null;
            }
            
            Log("Capturing passthrough snapshot...");
            
            // Store original render target
            RenderTexture originalTarget = targetCamera.targetTexture;
            
            // Set camera to render to our texture
            targetCamera.targetTexture = renderTexture;
            
            // Render the camera
            targetCamera.Render();
            
            // Read pixels from render texture
            RenderTexture.active = renderTexture;
            captureTexture.ReadPixels(new Rect(0, 0, captureWidth, captureHeight), 0, 0);
            captureTexture.Apply();
            
            // Restore original render target
            targetCamera.targetTexture = originalTarget;
            RenderTexture.active = null;
            
            // Convert to JPEG bytes
            byte[] jpegData = captureTexture.EncodeToJPG(85); // 85% quality
            
            Log($"Snapshot captured: {jpegData.Length} bytes");
            return jpegData;
        }
        catch (Exception e)
        {
            LogError($"Failed to capture snapshot: {e.Message}");
            return null;
        }
    }
    
    /// <summary>
    /// Capture a snapshot asynchronously
    /// </summary>
    public void CapturePassthroughSnapshotAsync(Action<byte[]> callback)
    {
        try
        {
            byte[] imageData = CapturePassthroughSnapshot();
            callback?.Invoke(imageData);
        }
        catch (Exception e)
        {
            LogError($"Async capture failed: {e.Message}");
            callback?.Invoke(null);
        }
    }
    
    /// <summary>
    /// Get a preview texture of the current camera view (for UI display)
    /// </summary>
    public Texture2D GetPreviewTexture()
    {
        if (captureTexture != null)
        {
            return captureTexture;
        }
        return null;
    }
    
    /// <summary>
    /// Check if camera capture is ready
    /// </summary>
    public bool IsReady()
    {
        return targetCamera != null && renderTexture != null && captureTexture != null;
    }
    
    private void OnDestroy()
    {
        // Clean up textures
        if (renderTexture != null)
        {
            renderTexture.Release();
            DestroyImmediate(renderTexture);
        }
        
        if (captureTexture != null)
        {
            DestroyImmediate(captureTexture);
        }
    }
    
    private void OnValidate()
    {
        // Ensure valid dimensions
        captureWidth = Mathf.Clamp(captureWidth, 64, 4096);
        captureHeight = Mathf.Clamp(captureHeight, 64, 4096);
    }
}
