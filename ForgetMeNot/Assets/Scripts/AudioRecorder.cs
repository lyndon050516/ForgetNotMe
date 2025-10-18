using System;
using System.Collections;
using UnityEngine;

public class AudioRecorder : MonoBehaviour
{
    [Header("Audio Settings")]
    public int sampleRate = Config.SAMPLE_RATE;
    public int channels = Config.CHANNELS;
    public int maxRecordingTime = Config.MAX_RECORDING_TIME;
    
    [Header("Debug")]
    public bool enableDebugLogs = true;
    
    private AudioClip recordingClip;
    private string microphoneName;
    private bool isRecording = false;
    private float recordingStartTime;
    
    private void Start()
    {
        InitializeMicrophone();
    }
    
    private void InitializeMicrophone()
    {
        // Get the default microphone
        if (Microphone.devices.Length > 0)
        {
            microphoneName = Microphone.devices[0];
            Log($"Microphone initialized: {microphoneName}");
        }
        else
        {
            LogError("No microphone devices found");
        }
    }
    
    private void Log(string message)
    {
        if (enableDebugLogs)
        {
            Debug.Log($"[AudioRecorder] {message}");
        }
    }
    
    private void LogError(string message)
    {
        Debug.LogError($"[AudioRecorder] {message}");
    }
    
    /// <summary>
    /// Start recording audio from the microphone
    /// </summary>
    public bool StartRecording()
    {
        if (isRecording)
        {
            Log("Already recording");
            return false;
        }
        
        if (string.IsNullOrEmpty(microphoneName))
        {
            LogError("No microphone available");
            return false;
        }
        
        try
        {
            // Start recording
            recordingClip = Microphone.Start(microphoneName, false, maxRecordingTime, sampleRate);
            isRecording = true;
            recordingStartTime = Time.time;
            
            Log($"Recording started with {microphoneName}");
            return true;
        }
        catch (Exception e)
        {
            LogError($"Failed to start recording: {e.Message}");
            return false;
        }
    }
    
    /// <summary>
    /// Stop recording and get the audio data as WAV bytes
    /// </summary>
    public byte[] StopRecordingAndGetData()
    {
        if (!isRecording)
        {
            Log("Not currently recording");
            return null;
        }
        
        try
        {
            // Stop recording
            Microphone.End(microphoneName);
            isRecording = false;
            
            float recordingDuration = Time.time - recordingStartTime;
            Log($"Recording stopped after {recordingDuration:F1} seconds");
            
            if (recordingClip == null)
            {
                LogError("No recording clip available");
                return null;
            }
            
            // Convert AudioClip to WAV bytes
            byte[] wavData = ConvertToWAV(recordingClip);
            
            // Clean up
            DestroyImmediate(recordingClip);
            recordingClip = null;
            
            Log($"Audio data converted to WAV: {wavData.Length} bytes");
            return wavData;
        }
        catch (Exception e)
        {
            LogError($"Failed to stop recording: {e.Message}");
            isRecording = false;
            return null;
        }
    }
    
    /// <summary>
    /// Get the current recording duration
    /// </summary>
    public float GetRecordingDuration()
    {
        if (!isRecording)
            return 0f;
        
        return Time.time - recordingStartTime;
    }
    
    /// <summary>
    /// Check if currently recording
    /// </summary>
    public bool IsRecording()
    {
        return isRecording;
    }
    
    /// <summary>
    /// Check if recording is ready
    /// </summary>
    public bool IsReady()
    {
        return !string.IsNullOrEmpty(microphoneName);
    }
    
    /// <summary>
    /// Convert AudioClip to WAV format
    /// </summary>
    private byte[] ConvertToWAV(AudioClip clip)
    {
        float[] samples = new float[clip.samples * clip.channels];
        clip.GetData(samples, 0);
        
        // Convert float samples to 16-bit PCM
        byte[] pcmData = new byte[samples.Length * 2];
        for (int i = 0; i < samples.Length; i++)
        {
            short sample = (short)(samples[i] * short.MaxValue);
            pcmData[i * 2] = (byte)(sample & 0xFF);
            pcmData[i * 2 + 1] = (byte)((sample >> 8) & 0xFF);
        }
        
        // Create WAV header
        byte[] header = CreateWAVHeader(pcmData.Length, clip.frequency, clip.channels);
        
        // Combine header and data
        byte[] wavData = new byte[header.Length + pcmData.Length];
        Array.Copy(header, 0, wavData, 0, header.Length);
        Array.Copy(pcmData, 0, wavData, header.Length, pcmData.Length);
        
        return wavData;
    }
    
    /// <summary>
    /// Create WAV file header
    /// </summary>
    private byte[] CreateWAVHeader(int dataLength, int sampleRate, int channels)
    {
        byte[] header = new byte[44];
        
        // RIFF header
        header[0] = (byte)'R';
        header[1] = (byte)'I';
        header[2] = (byte)'F';
        header[3] = (byte)'F';
        
        // File size
        int fileSize = dataLength + 36;
        header[4] = (byte)(fileSize & 0xFF);
        header[5] = (byte)((fileSize >> 8) & 0xFF);
        header[6] = (byte)((fileSize >> 16) & 0xFF);
        header[7] = (byte)((fileSize >> 24) & 0xFF);
        
        // WAVE format
        header[8] = (byte)'W';
        header[9] = (byte)'A';
        header[10] = (byte)'V';
        header[11] = (byte)'E';
        
        // fmt chunk
        header[12] = (byte)'f';
        header[13] = (byte)'m';
        header[14] = (byte)'t';
        header[15] = (byte)' ';
        
        // fmt chunk size
        header[16] = 16;
        header[17] = 0;
        header[18] = 0;
        header[19] = 0;
        
        // Audio format (PCM)
        header[20] = 1;
        header[21] = 0;
        
        // Number of channels
        header[22] = (byte)channels;
        header[23] = 0;
        
        // Sample rate
        header[24] = (byte)(sampleRate & 0xFF);
        header[25] = (byte)((sampleRate >> 8) & 0xFF);
        header[26] = (byte)((sampleRate >> 16) & 0xFF);
        header[27] = (byte)((sampleRate >> 24) & 0xFF);
        
        // Byte rate
        int byteRate = sampleRate * channels * 2;
        header[28] = (byte)(byteRate & 0xFF);
        header[29] = (byte)((byteRate >> 8) & 0xFF);
        header[30] = (byte)((byteRate >> 16) & 0xFF);
        header[31] = (byte)((byteRate >> 24) & 0xFF);
        
        // Block align
        header[32] = (byte)(channels * 2);
        header[33] = 0;
        
        // Bits per sample
        header[34] = 16;
        header[35] = 0;
        
        // data chunk
        header[36] = (byte)'d';
        header[37] = (byte)'a';
        header[38] = (byte)'t';
        header[39] = (byte)'a';
        
        // Data size
        header[40] = (byte)(dataLength & 0xFF);
        header[41] = (byte)((dataLength >> 8) & 0xFF);
        header[42] = (byte)((dataLength >> 16) & 0xFF);
        header[43] = (byte)((dataLength >> 24) & 0xFF);
        
        return header;
    }
    
    private void OnDestroy()
    {
        // Stop recording if still active
        if (isRecording)
        {
            Microphone.End(microphoneName);
        }
        
        // Clean up audio clip
        if (recordingClip != null)
        {
            DestroyImmediate(recordingClip);
        }
    }
}
