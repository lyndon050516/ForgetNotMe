using System;

[Serializable]
public class APIError
{
    public string status;
    public string message;
    public int error_code;
    
    public APIError()
    {
        status = "error";
        message = "Unknown error";
        error_code = -1;
    }
    
    public APIError(string errorMessage, int code = -1)
    {
        status = "error";
        message = errorMessage;
        error_code = code;
    }
}
