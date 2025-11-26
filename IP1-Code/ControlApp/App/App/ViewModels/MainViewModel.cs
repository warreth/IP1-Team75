using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using App.Services;
using PinController;
using Avalonia.Threading;
using System.Text.Json;

namespace App.ViewModels;

public partial class MainViewModel : ViewModelBase
{
    [ObservableProperty]
    private string apiUrl = "http://ip75-pi3.netbird.cloud:8080";

    // Add properties for editing and saving settings
    [ObservableProperty]
    private string? editableApiUrl;

    [ObservableProperty]
    private bool logVisible = true;

    [ObservableProperty]
    private bool editableLogVisible;

    [ObservableProperty]
    private float humidity;

    [ObservableProperty]
    private int lamp1;

    [ObservableProperty]
    private int lamp2;

    [ObservableProperty]
    private int lamp3;

    [ObservableProperty]
    private int pumpSpeed;

    [ObservableProperty]
    private string remainingTime = "--:--";

    [ObservableProperty]
    private string currentCycle = "Unknown";

    [ObservableProperty]
    private int targetPumpSpeed;

    [ObservableProperty]
    private int targetLamp1;

    [ObservableProperty]
    private int targetLamp2;

    [ObservableProperty]
    private int targetLamp3;

    public void Log(string message) //TODO: Make the logs scroll down when new log is added
    {
        if (message == null)
        {
            message = "[null log message]";
        }
        string logEntry = $"[{DateTime.Now:HH:mm:ss}] {message}";
        LogMessages.Add(logEntry);
    }





    [RelayCommand]
    private void LoadSettings()
    {
        EditableApiUrl = ApiUrl;
        EditableLogVisible = LogVisible;
        Log("Loaded settings into editable fields");
    }

    [RelayCommand]
    private void ClearLogs()
    {
        LogMessages.Clear();
        Log("Cleared logs");
    }

    [RelayCommand]
    private void SaveSettings()
    {
        if (string.IsNullOrWhiteSpace(EditableApiUrl))
        {
            Log("API URL cannot be empty");
            return;
        }

        ApiUrl = EditableApiUrl;
        LogVisible = EditableLogVisible;
    }

    [RelayCommand]
    private async Task SetPumpSpeed(decimal? speed)
    {
        if (speed.HasValue)
        {
            await _apiService.GetRawJsonAsync(ApiUrl, $"set-pump-speed?value={speed}");
            Log($"Set Pump Speed to {speed}");
        }
    }

    [RelayCommand]
    private async Task SetLamp1(decimal? brightness)
    {
        if (brightness.HasValue)
        {
            await _apiService.GetRawJsonAsync(ApiUrl, $"set-lamp-dl?value={brightness}");
            Log($"Set Lamp 1 (Daylight) to {brightness}");
        }
    }

    [RelayCommand]
    private async Task SetLamp2(decimal? brightness)
    {
        if (brightness.HasValue)
        {
            await _apiService.GetRawJsonAsync(ApiUrl, $"set-lamp-bloom?value={brightness}");
            Log($"Set Lamp 2 (Bloom) to {brightness}");
        }
    }

    [RelayCommand]
    private async Task SetLamp3(decimal? brightness)
    {
        if (brightness.HasValue)
        {
            await _apiService.GetRawJsonAsync(ApiUrl, $"set-lamp-ir?value={brightness}");
            Log($"Set Lamp 3 (Infrared) to {brightness}");
        }
    }

    public ObservableCollection<string> LogMessages { get; } = new ObservableCollection<string>();

    private readonly ApiService _apiService = new ApiService();

    private DispatcherTimer _logTimer;

    partial void OnApiUrlChanged(string value)
    {
        if (string.IsNullOrEmpty(EditableApiUrl))
            EditableApiUrl = value;
    }

    public MainViewModel()
    {
        EditableApiUrl = ApiUrl;
        EditableLogVisible = LogVisible;

        // Start polling timer
        var timer = new System.Timers.Timer(1000);
        timer.Elapsed += async (s, e) =>
        {
            var json = await _apiService.GetRawJsonAsync(ApiUrl, "status");
            if (!string.IsNullOrEmpty(json))
            {
                try
                {
                    var status = System.Text.Json.JsonSerializer.Deserialize<PicoStatus>(json);
                    if (status != null)
                    {
                        await Dispatcher.UIThread.InvokeAsync(() =>
                        {
                            Humidity = status.Humidity;
                            Lamp1 = status.Lamp1;
                            Lamp2 = status.Lamp2;
                            Lamp3 = status.Lamp3;
                            PumpSpeed = status.PumpSpeed;
                            RemainingTime = $"{status.Uren}h {status.Minuten}m";
                            CurrentCycle = status.Cycle ?? "Unknown";
                        });
                    }
                }
                catch (Exception ex)
                {
                    await Dispatcher.UIThread.InvokeAsync(() => Log($"Error parsing status: {ex.Message}"));
                }
            }
        };
        timer.Start();

        _logTimer = new DispatcherTimer
        {
            Interval = TimeSpan.FromSeconds(1)
        };
        _logTimer.Tick += async (sender, e) => await FetchLogs();
        _logTimer.Start();
    }

    private async Task FetchLogs()
    {
        try
        {
            var json = await _apiService.GetRawJsonAsync(ApiUrl, "logs");
            if (!string.IsNullOrEmpty(json))
            {
                var logs = JsonSerializer.Deserialize<string[]>(json);
                if (logs != null)
                {
                    foreach (var log in logs)
                    {
                        Log($"[Pico] {log}");
                    }
                }
            }
        }
        catch { /* Ignore errors */ }
    }
}
