using System;
using UnityEngine;
using OVR;

public class ControllerInputHandler : MonoBehaviour
{
    [Header("Controller Settings")]
    public OVRInput.Controller activeController = OVRInput.Controller.RTouch;
    
    [Header("Button Mappings")]
    public OVRInput.Button startEnrollmentButton = OVRInput.Button.One; // A button
    public OVRInput.Button stopEnrollmentButton = OVRInput.Button.Two; // B button
    public OVRInput.Button recallButton = OVRInput.Button.Four; // X button (left controller)
    
    [Header("Debug")]
    public bool enableDebugLogs = true;
    
    // Events
    public event Action OnStartEnrollmentPressed;
    public event Action OnStopEnrollmentPressed;
    public event Action OnRecallPressed;
    
    // Button state tracking
    private bool startEnrollmentPressed = false;
    private bool stopEnrollmentPressed = false;
    private bool recallPressed = false;
    
    private void Update()
    {
        HandleInput();
    }
    
    private void HandleInput()
    {
        // Handle start enrollment button (A button on right controller)
        bool startPressed = OVRInput.GetDown(startEnrollmentButton, OVRInput.Controller.RTouch);
        if (startPressed && !startEnrollmentPressed)
        {
            startEnrollmentPressed = true;
            Log("Start enrollment button pressed");
            OnStartEnrollmentPressed?.Invoke();
        }
        else if (!startPressed)
        {
            startEnrollmentPressed = false;
        }
        
        // Handle stop enrollment button (B button on right controller)
        bool stopPressed = OVRInput.GetDown(stopEnrollmentButton, OVRInput.Controller.RTouch);
        if (stopPressed && !stopEnrollmentPressed)
        {
            stopEnrollmentPressed = true;
            Log("Stop enrollment button pressed");
            OnStopEnrollmentPressed?.Invoke();
        }
        else if (!stopPressed)
        {
            stopEnrollmentPressed = false;
        }
        
        // Handle recall button (X button on left controller)
        bool recallPressedNow = OVRInput.GetDown(recallButton, OVRInput.Controller.LTouch);
        if (recallPressedNow && !recallPressed)
        {
            recallPressed = true;
            Log("Recall button pressed");
            OnRecallPressed?.Invoke();
        }
        else if (!recallPressedNow)
        {
            recallPressed = false;
        }
    }
    
    private void Log(string message)
    {
        if (enableDebugLogs)
        {
            Debug.Log($"[ControllerInputHandler] {message}");
        }
    }
    
    /// <summary>
    /// Check if a specific button is currently pressed
    /// </summary>
    public bool IsButtonPressed(OVRInput.Button button, OVRInput.Controller controller)
    {
        return OVRInput.Get(button, controller);
    }
    
    /// <summary>
    /// Check if a specific button was just pressed this frame
    /// </summary>
    public bool IsButtonDown(OVRInput.Button button, OVRInput.Controller controller)
    {
        return OVRInput.GetDown(button, controller);
    }
    
    /// <summary>
    /// Check if a specific button was just released this frame
    /// </summary>
    public bool IsButtonUp(OVRInput.Button button, OVRInput.Controller controller)
    {
        return OVRInput.GetUp(button, controller);
    }
    
    /// <summary>
    /// Get controller position
    /// </summary>
    public Vector3 GetControllerPosition(OVRInput.Controller controller)
    {
        return OVRInput.GetLocalControllerPosition(controller);
    }
    
    /// <summary>
    /// Get controller rotation
    /// </summary>
    public Quaternion GetControllerRotation(OVRInput.Controller controller)
    {
        return OVRInput.GetLocalControllerRotation(controller);
    }
    
    /// <summary>
    /// Check if controllers are connected
    /// </summary>
    public bool AreControllersConnected()
    {
        return OVRInput.IsControllerConnected(OVRInput.Controller.RTouch) || 
               OVRInput.IsControllerConnected(OVRInput.Controller.LTouch);
    }
    
    /// <summary>
    /// Get haptic feedback intensity
    /// </summary>
    public void TriggerHaptic(OVRInput.Controller controller, float frequency = 0.5f, float amplitude = 0.5f)
    {
        OVRInput.SetControllerVibration(frequency, amplitude, controller);
    }
    
    /// <summary>
    /// Stop haptic feedback
    /// </summary>
    public void StopHaptic(OVRInput.Controller controller)
    {
        OVRInput.SetControllerVibration(0, 0, controller);
    }
    
    /// <summary>
    /// Get button mapping info for debugging
    /// </summary>
    public string GetButtonMappingInfo()
    {
        return $"Start Enrollment: {startEnrollmentButton} (Right Controller)\n" +
               $"Stop Enrollment: {stopEnrollmentButton} (Right Controller)\n" +
               $"Recall: {recallButton} (Left Controller)";
    }
}
