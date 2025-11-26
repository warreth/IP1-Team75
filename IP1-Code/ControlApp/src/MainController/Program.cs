using static NonSpecific.ErrorHandler;
using static NonSpecific.Logger;
using NonSpecific; // For Helper
using PinController; // For PinControl

// Main entry point
public class Program
{
    // Image server and API URLs
    public static string apiUrl = "http://localhost:8080";
    public static void Main(string[] args)
    {
        // Initialize pin controller
        PinControl.Initialize();
        // Set API base URL
        Helper.BaseUrl = apiUrl;

        // Start API in background threads
        Task.Run(() => ApiHost.Start("8080"));

        //! Start video controller to stream video from rpi camV2

        // Keep the application running
        Thread.Sleep(Timeout.Infinite);
    }
}
