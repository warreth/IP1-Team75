using static NonSpecific.ErrorHandler;
using static NonSpecific.Logger;
using Api;

// Main entry point
public class Program
{
    // Image server and API URLs
    public static string apiUrl = "https://localhost:8080";
    public static void Main(string[] args)
    {
        // Create shared pin controller
        PinController sharedPin = new();
        // Set API base URL
        Helper.BaseUrl = apiUrl;

        // Start API and image server in background threads
        Task.Run(() => ApiHost.Start(sharedHatch, "8080"));

        //! Start video controller to stream video from rpi camV2
    }
}
