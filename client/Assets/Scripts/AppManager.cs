// AppManager.cs
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine.Android;

// --- Helper classes to parse the JSON response from your server ---

[System.Serializable]
public class EnrollResponse
{
    public string status;
    public string person_id;
    public string summary;
    public string message;
}

[System.Serializable]
public class RecallResponse
{
    public string status;
    public string person_id;
    public float confidence;
    public string summary;
    public string message;
}

[System.Serializable]
public class PingResponse
{
    public string status;
    public string service;
}


public class AppManager : MonoBehaviour
{
    [Header("Server Settings")]
    public string serverUrl = "https://electrodiagnostic-romona-visceromotor.ngrok-free.dev"; // <-- IMPORTANT: Set this in the Inspector!

    [Header("UI Elements")]
    public Button enrollButton;
    public Button stopButton;
    public Button recallButton;
    public TextMeshProUGUI statusText;

    private AudioClip recording;
    private string microphoneDevice;
    private bool isRecording = false;
    private bool isBusy = false;

    void Start()
    {
        // Add listeners to the buttons first
        enrollButton.onClick.AddListener(StartEnrollment);
        stopButton.onClick.AddListener(StopEnrollment);
        recallButton.onClick.AddListener(StartRecall);

        // Set initial UI state
        UpdateUIState();

        // Start the permission check and initialization process
        StartCoroutine(InitializeApp());
    }

    IEnumerator InitializeApp()
    {
        // Check if we already have microphone permission
        if (!Permission.HasUserAuthorizedPermission(Permission.Microphone))
        {
            // If not, request it
            statusText.text = "Requesting microphone permission...";
            Permission.RequestUserPermission(Permission.Microphone);

            // Wait until the user responds to the permission pop-up
            float startTime = Time.time;
            while (!Permission.HasUserAuthorizedPermission(Permission.Microphone) && Time.time - startTime < 10f)
            {
                yield return null; // Wait for the next frame
            }
        }

        // --- Now, check the result ---

        // 1. If permission was granted
        if (Permission.HasUserAuthorizedPermission(Permission.Microphone))
        {
            // 2. Check if a microphone device actually exists
            if (Microphone.devices.Length == 0)
            {
                statusText.text = "Error: No microphone found (even with permission).";
                enrollButton.interactable = false;
                yield break;
            }

            // 3. All good! Initialize the mic and ping the server
            microphoneDevice = Microphone.devices[0];
            StartCoroutine(SendPing()); // Test connection
        }
        // 4. If permission was denied
        else
        {
            statusText.text = "Microphone permission denied. Cannot record audio.";
            enrollButton.interactable = false;
        }
    }

    private void UpdateUIState()
    {
        // Manage button visibility and interactivity based on state
        enrollButton.gameObject.SetActive(!isRecording);
        recallButton.gameObject.SetActive(!isRecording);
        stopButton.gameObject.SetActive(isRecording);

        enrollButton.interactable = !isBusy && !isRecording;
        recallButton.interactable = !isBusy && !isRecording;
        stopButton.interactable = !isBusy && isRecording;
    }

    public void StartEnrollment()
    {
        if (isBusy) return;

        isRecording = true;
        UpdateUIState();
        statusText.text = "Recording... Look at the person and speak.";

        // Start recording for 5 minutes (300 seconds)
        recording = Microphone.Start(microphoneDevice, false, 300, 44100);
    }

    public void StopEnrollment()
    {
        if (!isRecording) return;
        
        isRecording = false;
        isBusy = true; // Now we are busy with a web request
        Microphone.End(microphoneDevice);
        
        UpdateUIState();
        statusText.text = "Processing enrollment... (Capturing photo)";

        StartCoroutine(CaptureAndSendEnrollmentData());
    }

    public void StartRecall()
    {
        if (isBusy || isRecording) return;
        
        isBusy = true;
        UpdateUIState();
        statusText.text = "Recalling... (Capturing photo)";

        StartCoroutine(CaptureAndSendRecallData());
    }

    private byte[] CaptureSnapshot()
    {
        // Use passthrough camera for real world capture
        Camera passthroughCamera = Camera.main;
        
        if (passthroughCamera != null)
        {
            // Enable passthrough if available
            if (passthroughCamera.GetComponent<OVRCameraRig>() != null)
            {
                // This is a VR camera with passthrough capability
                return CaptureFromPassthroughCamera(passthroughCamera);
            }
            else
            {
                // Regular camera fallback
                return CaptureFromCamera(passthroughCamera);
            }
        }
        
        // Last resort: Use screen capture
        Debug.LogWarning("No camera found, using screen capture");
        Texture2D texture = ScreenCapture.CaptureScreenshotAsTexture();
        byte[] imageBytes = texture.EncodeToJPG(75);
        Destroy(texture);
        return imageBytes;
    }
    
    private byte[] CaptureFromPassthroughCamera(Camera camera)
    {
        // Simple passthrough capture - just use the camera's current view
        // This will capture whatever the user sees through the headset
        RenderTexture renderTexture = new RenderTexture(1920, 1080, 24);
        camera.targetTexture = renderTexture;
        camera.Render();
        
        // Read the pixels from the RenderTexture
        RenderTexture.active = renderTexture;
        Texture2D texture = new Texture2D(renderTexture.width, renderTexture.height, TextureFormat.RGB24, false);
        texture.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        texture.Apply();
        
        // Reset the camera target texture
        camera.targetTexture = null;
        RenderTexture.active = null;
        
        // Encode to JPG
        byte[] imageBytes = texture.EncodeToJPG(75);
        
        // Clean up
        Destroy(texture);
        Destroy(renderTexture);
        
        return imageBytes;
    }
    
    private byte[] CaptureFromCamera(Camera camera)
    {
        // Create a RenderTexture to capture the camera view
        RenderTexture renderTexture = new RenderTexture(1920, 1080, 24);
        camera.targetTexture = renderTexture;
        camera.Render();
        
        // Read the pixels from the RenderTexture
        RenderTexture.active = renderTexture;
        Texture2D texture = new Texture2D(renderTexture.width, renderTexture.height, TextureFormat.RGB24, false);
        texture.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        texture.Apply();
        
        // Reset the camera target texture
        camera.targetTexture = null;
        RenderTexture.active = null;
        
        // Encode to JPG
        byte[] imageBytes = texture.EncodeToJPG(75);
        
        // Clean up
        Destroy(texture);
        Destroy(renderTexture);
        
        return imageBytes;
    }

    private void SaveImageToUploads(byte[] imageBytes)
    {
        try
        {
            string uploadsPath = "/Users/andrewchoy/Desktop/try/uploads";
            string fileName = "captured_image_" + System.DateTime.Now.ToString("yyyyMMdd_HHmmss") + ".jpg";
            string fullPath = System.IO.Path.Combine(uploadsPath, fileName);
            
            System.IO.File.WriteAllBytes(fullPath, imageBytes);
            Debug.Log($"Image saved to: {fullPath}");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to save image: {e.Message}");
        }
    }

    IEnumerator CaptureAndSendEnrollmentData()
    {
        // Step 1: Capture the snapshot
        byte[] imageBytes = CaptureSnapshot();
        if (imageBytes == null)
        {
            statusText.text = "Error: Failed to capture image. Check VR camera setup.";
            isBusy = false;
            UpdateUIState();
            yield break;
        }
        
        // Save the image locally
        SaveImageToUploads(imageBytes);
        
        // Step 2: Convert the AudioClip to a WAV byte array
        // This requires the WavUtility.cs helper script!
        byte[] audioBytes = WavUtility.FromAudioClip(recording);
        if (audioBytes == null)
        {
            statusText.text = "Error: Failed to encode audio.";
            isBusy = false;
            UpdateUIState();
            yield break;
        }

        // Step 3: Create the web request form
        List<IMultipartFormSection> formData = new List<IMultipartFormSection>();
        formData.Add(new MultipartFormFileSection("image", imageBytes, "snapshot.jpg", "image/jpeg"));
        formData.Add(new MultipartFormFileSection("audio", audioBytes, "recording.wav", "audio/wav"));

        // Step 4: Send the request
        UnityWebRequest www = UnityWebRequest.Post(serverUrl + "/enroll", formData);
        yield return www.SendWebRequest();

        // Step 5: Handle the response
        if (www.result == UnityWebRequest.Result.Success)
        {
            EnrollResponse response = JsonUtility.FromJson<EnrollResponse>(www.downloadHandler.text);
            if (response.status == "success")
            {
                statusText.text = $"Enrolled!\nSummary: {response.summary}";
            }
            else if (response.status == "already_enrolled")
            {
                statusText.text = $"Already Enrolled:\n{response.summary}";
            }
            else
            {
                statusText.text = $"Error: {response.message}";
            }
        }
        else
        {
            statusText.text = $"Network Error: {www.error}";
        }
        
        isBusy = false;
        UpdateUIState();
    }

    IEnumerator CaptureAndSendRecallData()
    {
        // Step 1: Capture the snapshot
        byte[] imageBytes = CaptureSnapshot();
        if (imageBytes == null)
        {
            statusText.text = "Error: Failed to capture image. Check VR camera setup.";
            isBusy = false;
            UpdateUIState();
            yield break;
        }
        
        // Save the image locally
        SaveImageToUploads(imageBytes);
        
        // Step 2: Create the web request form
        List<IMultipartFormSection> formData = new List<IMultipartFormSection>();
        formData.Add(new MultipartFormFileSection("image", imageBytes, "snapshot.jpg", "image/jpeg"));

        // Step 3: Send the request
        UnityWebRequest www = UnityWebRequest.Post(serverUrl + "/recall", formData);
        yield return www.SendWebRequest();
        
        // Step 4: Handle the response
        if (www.result == UnityWebRequest.Result.Success)
        {
            RecallResponse response = JsonUtility.FromJson<RecallResponse>(www.downloadHandler.text);
            if (response.status == "match")
            {
                statusText.text = $"Match Found! (Conf: {response.confidence * 100}%)\n{response.summary}";
            }
            else if (response.status == "no_match")
            {
                statusText.text = "No match found.";
            }
            else
            {
                statusText.text = $"Error: {response.message}";
            }
        }
        else
        {
            statusText.text = $"Network Error: {www.error}";
        }

        isBusy = false;
        UpdateUIState();
    }

    IEnumerator SendPing()
    {
        isBusy = true;
        UpdateUIState();
        statusText.text = "Connecting to server...";
        
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + "/ping");
        yield return www.SendWebRequest();

        if (www.result == UnityWebRequest.Result.Success)
        {
            PingResponse response = JsonUtility.FromJson<PingResponse>(www.downloadHandler.text);
            if (response.status == "ok")
            {
                statusText.text = $"Connected to {response.service}!\nReady.";
            }
            else
            {
                statusText.text = "Server connection failed.";
            }
        }
        else
        {
            statusText.text = $"Connection Error. Check IP.\n{www.error}";
        }

        isBusy = false;
        UpdateUIState();
    }
}