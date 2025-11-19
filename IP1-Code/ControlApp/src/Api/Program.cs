using Microsoft.AspNetCore.Mvc;
using System;
using static NonSpecific.ErrorHandler;
using static NonSpecific.Logger;
using NonSpecific; // For Helper
using PinController;

// Start API server and define endpoints
public static class ApiHost
{
    // Start the API server
    public static void Start(string port)
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

        // Endpoint: Get full status (sensors, lights, pump, time)
        app.MapGet("/status", () =>
        {
            var status = PinControl.GetLatestStatus();
            if (status == null)
            {
                return Results.Problem("Could not retrieve status from Pico.");
            }
            return Results.Ok(status);
        });

        // Endpoint: Get logs
        app.MapGet("/logs", () =>
        {
            var logs = PinControl.GetLogs();
            return Results.Ok(logs);
        });

        // Endpoint: Set pump speed
        app.MapGet("/set-pump-speed", (int value) =>
        {
            HandleError(() =>
            {
                PinControl.SendCommand("CHANGE_POMP_SPEED", value);
                Log("Api", $"Set pump speed to {value}");
            });
            return Results.Ok(new { message = $"Pump speed set to {value}" });
        });

        // Endpoint: Set Daylight brightness
        app.MapGet("/set-lamp-dl", (int value) =>
        {
            HandleError(() =>
            {
                PinControl.SendCommand("SET_LAMP_DL_BRIGHTNESS", value);
                Log("Api", $"Set Daylight brightness to {value}");
            });
            return Results.Ok(new { message = $"Daylight brightness set to {value}" });
        });

        // Endpoint: Set Blooming brightness
        app.MapGet("/set-lamp-bloom", (int value) =>
        {
            HandleError(() =>
            {
                PinControl.SendCommand("SET_LAMP_BLOOM_BRIGHTNESS", value);
                Log("Api", $"Set Blooming brightness to {value}");
            });
            return Results.Ok(new { message = $"Blooming brightness set to {value}" });
        });

        // Endpoint: Set Infrared brightness
        app.MapGet("/set-lamp-ir", (int value) =>
        {
            HandleError(() =>
            {
                PinControl.SendCommand("SET_LAMP_IR_BRIGHTNESS", value);
                Log("Api", $"Set Infrared brightness to {value}");
            });
            return Results.Ok(new { message = $"Infrared brightness set to {value}" });
        });

        Log("Api", $"Trying to start API server on http://ip75-pi3.netbird.cloud:{port}");
        app.Run();
    }
}