using System;

[Serializable]
public class RecallResponse
{
    public string status;
    public string person_id;
    public float confidence;
    public string summary;
    public string enrolled_at;
    public string message;
    
    public bool IsMatch => status == "match";
    public bool IsNoMatch => status == "no_match";
    public bool IsError => status == "error";
}
