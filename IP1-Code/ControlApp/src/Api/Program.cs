using Microsoft.AspNetCore.Mvc;
using Api;
using System;
using static NonSpecific.ErrorHandler;
using static NonSpecific.Logger;

// Start API server and define endpoints
public static class ApiHost
{
    // Start the API server with a shared HatchController instance
    public static void Start(HatchController hatch, string port)
    {
        // Setup web server
        var builder = WebApplication.CreateBuilder();
        builder.Logging.ClearProviders(); // Removes Console logger and others

        builder.WebHost.UseUrls($"https://0.0.0.0:{port}");
        var app = builder.Build();
        app.UseHttpsRedirection();

        // Root endpoint
        app.MapGet("/", () => "The API is online");

        // Get shared helpers
        Helper apiHelper = Helper.Instance;

        // Endpoint: move lampen
        app.MapGet("/move-lampen", () =>
        {
            HandleError(() =>
            {
                //! move lampen up or down (rotation of motor)
            });
            //return Results.Ok(new { });
        });

        app.MapGet("/start-pomp", () =>
        {
            HandleError(() =>
            {
                //! Start de pomp
                Log("Api", "Starting pomp");
            });
            return Results.Ok(new { message = "Pomp started" });
        });

        // Endpoint: stop pomp
        app.MapGet("/stop-pomp", () =>
        {
            HandleError(() =>
            {
                //! Stop de pomp
                Log("Api", "Stopping pomp");
            });
            return Results.Ok(new { message = "Pomp stopped" });
        });

        // Endpoint: read sensors
        app.MapGet("/read-vochtigheid", () =>
        {
            //! Read vochtigheid sensor
        });
        app.MapGet("/read-temperatuur", () =>
        {
            //! Read temperatuur sensor
        });
        app.MapGet("/read-licht", () =>
        {
            //! Read lichten sterktes
        });

        Log("Api", $"Trying to start API server on http://ip75-pi3.netbird.cloud:{port}");
        app.Run();
    }
}