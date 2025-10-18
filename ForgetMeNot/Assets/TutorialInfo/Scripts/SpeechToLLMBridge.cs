using UnityEngine;
using Meta.XR.BuildingBlocks.AIBlocks;

/// <summary>
/// Bridges Speech-to-Text output to LLM Agent
/// SIMPLE STANDALONE VERSION - Can be on any GameObject
/// </summary>
public class SpeechToLLMBridge : MonoBehaviour
{
    [Header("References")]
    [Tooltip("Drag the GameObject that has the LlmAgent component")]
    public GameObject llmGameObject;
    
    [Tooltip("Drag the GameObject that has the Result component")]
    public GameObject resultHandlerObject;
    
    [Header("Prompt Template")]
    [TextArea(3, 5)]
    [Tooltip("The prompt template. Use {transcript} where you want the transcript inserted.")]
    public string promptTemplate = "Summarize this transcript into 4 sentences so that it is easy to understand:\n\n{transcript}";
    
    private LlmAgent _llmAgent;
    
    void Start()
    {
        Debug.LogWarning("========================================");
        Debug.LogWarning($"SPEECHBRIDGE START() on GameObject: {gameObject.name}");
        Debug.LogWarning($"llmGameObject value: {(llmGameObject == null ? "NULL" : llmGameObject.name)}");
        Debug.LogWarning("========================================");
        
        if (llmGameObject == null)
        {
            Debug.LogError($"[SpeechToLLMBridge on {gameObject.name}] ❌ llmGameObject is not assigned! Drag the LLM GameObject in the Inspector.");
            return;
        }
        
        _llmAgent = llmGameObject.GetComponent<LlmAgent>();
        if (_llmAgent == null)
        {
            Debug.LogError($"[SpeechToLLMBridge] ❌ No LlmAgent found on '{llmGameObject.name}'!");
        }
        else
        {
            Debug.LogWarning($"✅ SpeechToLLMBridge on {gameObject.name} initialized successfully!");
            Debug.LogWarning($"✅ Connected to LlmAgent on {llmGameObject.name}");
        }
    }
    
    /// <summary>
    /// Called by Speech To Text when a transcript is received
    /// </summary>
    public void OnTranscriptReceived(string transcript)
    {
        Debug.LogWarning("═══════════════════════════════════════");
        Debug.LogWarning("🎤 TRANSCRIPT RECEIVED!");
        Debug.LogWarning($"Transcript: '{transcript}'");
        Debug.LogWarning("═══════════════════════════════════════");
        
        if (string.IsNullOrWhiteSpace(transcript))
        {
            Debug.LogWarning("[SpeechToLLMBridge] ⚠️ Received empty transcript");
            return;
        }
        
        if (_llmAgent == null)
        {
            Debug.LogError("[SpeechToLLMBridge] ❌ LLM Agent is null! Check your setup.");
            return;
        }
        
        Debug.LogWarning($"📝 Transcript received: {transcript}");
        
        // Create the prompt
        string prompt = promptTemplate.Replace("{transcript}", transcript);
        
        Debug.LogWarning($"🤖 Sending to LLM:\n{prompt}");
        
        // Send to LLM asynchronously (fire and forget)
        SendToLLMAsync(prompt);
    }
    
    private async void SendToLLMAsync(string prompt)
    {
        try
        {
            Debug.LogWarning("📤 Calling LLM API... (this may take 10-30 seconds)");
            Debug.LogWarning($"Prompt being sent:\n{prompt}");
            
            // Add listeners to capture the response
            _llmAgent.onResponseReceived.AddListener(OnLLMResponseDebug);
            
            await _llmAgent.SendTextOnlyAsync(prompt);
            Debug.LogWarning("✅ LLM request sent! Waiting for response event...");
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"❌ LLM request FAILED: {ex.Message}");
            Debug.LogError($"Exception type: {ex.GetType().Name}");
            Debug.LogError($"Stack trace: {ex.StackTrace}");
            Debug.LogException(ex);
        }
    }
    
    private void OnLLMResponseDebug(string response)
    {
        Debug.LogWarning($"[DEBUG] LLM Raw Response received: '{response}'");
        Debug.LogWarning($"[DEBUG] Response length: {(response == null ? "null" : response.Length.ToString())}");
        
        // Forward to Result component directly
        if (resultHandlerObject != null)
        {
            Result resultComponent = resultHandlerObject.GetComponent<Result>();
            if (resultComponent != null)
            {
                resultComponent.OnLLMResult(response);
            }
            else
            {
                Debug.LogError("[SpeechToLLMBridge] No Result component found on resultHandlerObject!");
            }
        }
        else
        {
            Debug.LogWarning("[SpeechToLLMBridge] resultHandlerObject not assigned - result won't be displayed!");
        }
        
        _llmAgent.onResponseReceived.RemoveListener(OnLLMResponseDebug);
    }
}
