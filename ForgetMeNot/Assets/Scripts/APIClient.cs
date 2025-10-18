using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using System.Text;

public class APIClient : MonoBehaviour
{
    [Header("API Configuration")]
    public string baseURL = Config.API_BASE_URL;
    public int timeout = Config.REQUEST_TIMEOUT;
    
    [Header("Debug")]
    public bool enableDebugLogs = true;
    
    private void Log(string message)
    {
        if (enableDebugLogs)
        {
            Debug.Log($"[APIClient] {message}");
        }
    }
    
    private void LogError(string message)
    {
        Debug.LogError($"[APIClient] {message}");
    }
    
    /// <summary>
    /// Test connectivity to the backend server
    /// </summary>
    public IEnumerator TestConnection(Action<bool> callback)
    {
        string url = $"{baseURL}/ping";
        Log($"Testing connection to: {url}");
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.timeout = timeout;
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Log("Connection test successful");
                callback(true);
            }
            else
            {
                LogError($"Connection test failed: {request.error}");
                callback(false);
            }
        }
    }
    
    /// <summary>
    /// Enroll a person with image and audio data
    /// </summary>
    public IEnumerator EnrollPerson(byte[] imageData, byte[] audioData, Action<EnrollResponse> callback)
    {
        string url = $"{baseURL}/enroll";
        Log($"Enrolling person with image ({imageData.Length} bytes) and audio ({audioData.Length} bytes)");
        
        // Create multipart form data
        List<IMultipartFormSection> formData = new List<IMultipartFormSection>();
        formData.Add(new MultipartFormFileSection("image", imageData, "image.jpg", "image/jpeg"));
        formData.Add(new MultipartFormFileSection("audio", audioData, "audio.wav", "audio/wav"));
        
        using (UnityWebRequest request = UnityWebRequest.Post(url, formData))
        {
            request.timeout = timeout;
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    EnrollResponse response = JsonUtility.FromJson<EnrollResponse>(request.downloadHandler.text);
                    Log($"Enrollment response: {response.status}");
                    callback(response);
                }
                catch (Exception e)
                {
                    LogError($"Failed to parse enrollment response: {e.Message}");
                    callback(new EnrollResponse { status = "error", message = "Failed to parse response" });
                }
            }
            else
            {
                LogError($"Enrollment request failed: {request.error}");
                callback(new EnrollResponse { status = "error", message = request.error });
            }
        }
    }
    
    /// <summary>
    /// Recall a person using image data
    /// </summary>
    public IEnumerator RecallPerson(byte[] imageData, Action<RecallResponse> callback)
    {
        string url = $"{baseURL}/recall";
        Log($"Recalling person with image ({imageData.Length} bytes)");
        
        // Create multipart form data
        List<IMultipartFormSection> formData = new List<IMultipartFormSection>();
        formData.Add(new MultipartFormFileSection("image", imageData, "image.jpg", "image/jpeg"));
        
        using (UnityWebRequest request = UnityWebRequest.Post(url, formData))
        {
            request.timeout = timeout;
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    RecallResponse response = JsonUtility.FromJson<RecallResponse>(request.downloadHandler.text);
                    Log($"Recall response: {response.status}");
                    callback(response);
                }
                catch (Exception e)
                {
                    LogError($"Failed to parse recall response: {e.Message}");
                    callback(new RecallResponse { status = "error", message = "Failed to parse response" });
                }
            }
            else
            {
                LogError($"Recall request failed: {request.error}");
                callback(new RecallResponse { status = "error", message = request.error });
            }
        }
    }
    
    /// <summary>
    /// Get health status from the backend
    /// </summary>
    public IEnumerator GetHealthStatus(Action<bool, string> callback)
    {
        string url = $"{baseURL}/health";
        Log($"Checking health status: {url}");
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.timeout = timeout;
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Log("Health check successful");
                callback(true, request.downloadHandler.text);
            }
            else
            {
                LogError($"Health check failed: {request.error}");
                callback(false, request.error);
            }
        }
    }
    
    /// <summary>
    /// List all enrolled persons (debug endpoint)
    /// </summary>
    public IEnumerator ListPersons(Action<string> callback)
    {
        string url = $"{baseURL}/list_persons";
        Log($"Listing persons: {url}");
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.timeout = timeout;
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Log("List persons successful");
                callback(request.downloadHandler.text);
            }
            else
            {
                LogError($"List persons failed: {request.error}");
                callback(null);
            }
        }
    }
}
