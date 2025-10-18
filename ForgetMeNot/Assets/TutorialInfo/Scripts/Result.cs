using UnityEngine;
using System;

/// <summary>
/// Gets output from LLM Building Block and displays to console
/// 
/// SETUP:
/// 1. Attach this to any GameObject in your scene
/// 2. Drag the [BuildingBlock] Large Language Models to "LLM Building Block"
/// 3. In the LLM Building Block Inspector:
///    - Find the "On Prompt Sent" or response event
///    - Click "+"
///    - Drag this GameObject
///    - Select Result.OnLLMResult
/// </summary>

[System.Serializable]
public class LLMResponseData
{
    public string summary;
}

public class Result : MonoBehaviour
{
    [Header("Building Block Reference")]
    [Tooltip("Drag the [BuildingBlock] Large Language Models here")]
    public GameObject llmBuildingBlock;
    
    [Header("Last Result (read-only)")]
    public string lastResult = "";
    
    [Header("JSON Output")]
    [Tooltip("Save JSON to file on each response")]
    public bool saveToFile = false;
    
    [Tooltip("File path for JSON output (relative to project folder)")]
    public string jsonFilePath = "LLM_Results.json";
    
    void Start()
    {
        Debug.LogWarning("========================================");
        Debug.LogWarning("RESULT START() CALLED!");
        Debug.LogWarning("✅ Result component initialized!");
        Debug.LogWarning("========================================");
    }
    
    /// <summary>
    /// Called by LLM Building Block when it gets a response
    /// Connect this in the LLM Building Block's response event
    /// </summary>
    public void OnLLMResult(string result)
    {
        Debug.LogWarning("═══════════════════════════════════════");
        Debug.LogWarning("🔔 LLM RESULT RECEIVED!");
        Debug.LogWarning($"Result is null: {result == null}");
        Debug.LogWarning($"Result is empty: {string.IsNullOrEmpty(result)}");
        Debug.LogWarning($"Result length: {(result == null ? "null" : result.Length.ToString())}");
        Debug.LogWarning("═══════════════════════════════════════");
        
        lastResult = result;
        
        // Display to console
        if (string.IsNullOrEmpty(result))
        {
            Debug.LogError("❌ LLM RESULT IS EMPTY OR NULL!");
        }
        else
        {
            Debug.LogWarning("LLM RESULT:");
            Debug.LogWarning(result);
            Debug.LogWarning("═══════════════════════════════════════");
            
            // Convert to JSON
            string json = ConvertToJSON(result);
            Debug.LogWarning("📄 JSON OUTPUT:");
            Debug.LogWarning(json);
            Debug.LogWarning("═══════════════════════════════════════");
            
            // Save to file if enabled
            if (saveToFile)
            {
                SaveJSONToFile(json);
            }
        }
    }
    
    /// <summary>
    /// Converts the LLM result to JSON format
    /// </summary>
    private string ConvertToJSON(string result)
    {
        LLMResponseData data = new LLMResponseData
        {
            summary = result
        };
        
        return JsonUtility.ToJson(data, true); // true = pretty print
    }
    
    /// <summary>
    /// Saves JSON to file
    /// </summary>
    private void SaveJSONToFile(string json)
    {
        try
        {
            string fullPath = System.IO.Path.Combine(Application.dataPath, "..", jsonFilePath);
            System.IO.File.WriteAllText(fullPath, json);
            Debug.Log($"✅ JSON saved to: {fullPath}");
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"❌ Failed to save JSON: {ex.Message}");
        }
    }
    
    /// <summary>
    /// Alternative method if Building Block uses different parameter
    /// </summary>
    public void OnPromptSent(string response)
    {
        OnLLMResult(response);
    }
    
    /// <summary>
    /// Display on screen as well
    /// </summary>
    void OnGUI()
    {
        if (!string.IsNullOrEmpty(lastResult))
        {
            GUIStyle style = new GUIStyle();
            style.fontSize = 24;
            style.normal.textColor = Color.green;
            style.wordWrap = true;
            
            GUI.Label(new Rect(10, 10, Screen.width - 20, Screen.height - 20), 
                "LLM Result:\n\n" + lastResult, 
                style);
        }
    }
}
