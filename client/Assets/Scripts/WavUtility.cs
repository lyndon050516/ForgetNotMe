// WavUtility.cs
// A helper class to convert Unity's AudioClip to a WAV file byte array
// Based on: https://github.com/Unity-Technologies/UnityWav/

using System;
using System.IO;
using UnityEngine;

public static class WavUtility
{
    private const int HEADER_SIZE = 44;

    public static byte[] FromAudioClip(AudioClip clip)
    {
        if (clip == null) return null;

        using (var memoryStream = new MemoryStream())
        {
            // Write the WAV header
            memoryStream.Write(new byte[HEADER_SIZE], 0, HEADER_SIZE);

            // Get audio data
            float[] data = new float[clip.samples * clip.channels];
            clip.GetData(data, 0);

            // Convert to 16-bit PCM
            Int16[] intData = new Int16[data.Length];
            byte[] byteData = new byte[data.Length * 2];

            for (int i = 0; i < data.Length; i++)
            {
                intData[i] = (short)(data[i] * Int16.MaxValue);
                BitConverter.GetBytes(intData[i]).CopyTo(byteData, i * 2);
            }

            memoryStream.Write(byteData, 0, byteData.Length);

            // Write the final header
            WriteHeader(memoryStream, clip.channels, clip.frequency);

            return memoryStream.ToArray();
        }
    }

    private static void WriteHeader(MemoryStream stream, int channels, int sampleRate)
    {
        int samples = ((int)stream.Length - HEADER_SIZE) / 2;

        stream.Seek(0, SeekOrigin.Begin);

        // RIFF chunk
        stream.Write(System.Text.Encoding.UTF8.GetBytes("RIFF"), 0, 4);
        stream.Write(BitConverter.GetBytes(stream.Length - 8), 0, 4);
        stream.Write(System.Text.Encoding.UTF8.GetBytes("WAVE"), 0, 4);

        // "fmt " sub-chunk
        stream.Write(System.Text.Encoding.UTF8.GetBytes("fmt "), 0, 4);
        stream.Write(BitConverter.GetBytes(16), 0, 4); // Subchunk1Size (16 for PCM)
        stream.Write(BitConverter.GetBytes((ushort)1), 0, 2); // AudioFormat (1 for PCM)
        stream.Write(BitConverter.GetBytes((ushort)channels), 0, 2);
        stream.Write(BitConverter.GetBytes(sampleRate), 0, 4);
        stream.Write(BitConverter.GetBytes(sampleRate * channels * 2), 0, 4); // ByteRate
        stream.Write(BitConverter.GetBytes((ushort)(channels * 2)), 0, 2); // BlockAlign
        stream.Write(BitConverter.GetBytes((ushort)16), 0, 2); // BitsPerSample

        // "data" sub-chunk
        stream.Write(System.Text.Encoding.UTF8.GetBytes("data"), 0, 4);
        stream.Write(BitConverter.GetBytes(samples * channels * 2), 0, 4); // Subchunk2Size
    }
}