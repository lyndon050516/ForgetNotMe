using System;

[Serializable]
public class EnrollResponse
{
    public string status;
    public string person_id;
    public string summary;
    public string message;
    public string enrolled_at;
    
    public bool IsSuccess => status == "success";
    public bool IsAlreadyEnrolled => status == "already_enrolled";
    public bool IsError => status == "error";
}
