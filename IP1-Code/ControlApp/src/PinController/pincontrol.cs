using System;
using System.IO.Ports;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace PinController;

public class PicoStatus
{
    [JsonPropertyName("humidity")]
    public float Humidity { get; set; }
    [JsonPropertyName("lamp1")]
    public int Lamp1 { get; set; }
    [JsonPropertyName("lamp2")]
    public int Lamp2 { get; set; }
    [JsonPropertyName("lamp3")]
    public int Lamp3 { get; set; }
    [JsonPropertyName("pump_speed")]
    public int PumpSpeed { get; set; }
    [JsonPropertyName("uren")]
    public int Uren { get; set; }
    [JsonPropertyName("minuten")]
    public int Minuten { get; set; }
    [JsonPropertyName("cycle")]
    public string Cycle { get; set; }
}

public static class PinControl
{
    private static SerialPort? _serialPort;
    private static PicoStatus? _latestStatus;
    private static List<string> _logs = new List<string>();
    private static object _logLock = new object();
    private static bool _isRunning = false;
    private static string _devicePath = "/dev/serial0";
    private static int _baudRate = 9600;

    // On Raspberry Pi 3:
    // /dev/serial0 usually maps to GPIO 14 (TX) and 15 (RX)
    //! Bron: https://raspberrypi.stackexchange.com/questions/45570/how-do-i-make-serial-work-on-the-raspberry-pi3-pizerow-pi4-or-later-models#45571
    public static void Initialize(string devicePath = "/dev/serial0", int baudRate = 9600)
    {
        _devicePath = devicePath;
        _baudRate = baudRate;
        _isRunning = true;
        Task.Run(ReadSerialPort);
    }

    private static void ReadSerialPort()
    {
        while (_isRunning)
        {
            try
            {
                if (_serialPort == null || !_serialPort.IsOpen)
                {
                    try
                    {
                        Console.WriteLine($"Connecting to {_devicePath}...");
                        _serialPort = new SerialPort(_devicePath, _baudRate);
                        _serialPort.ReadTimeout = 500;
                        _serialPort.WriteTimeout = 500;
                        _serialPort.Open();
                        Console.WriteLine($"Connected to {_devicePath}");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Connection Error: {ex.Message}");
                        Thread.Sleep(2000);
                        continue;
                    }
                }

                string line = _serialPort.ReadLine();
                if (string.IsNullOrWhiteSpace(line)) continue;

                // Debug: Print received data
                Console.WriteLine($"[Serial RX]: {line}");

                line = line.Trim();
                if (line.StartsWith("{"))
                {
                    try
                    {
                        _latestStatus = JsonSerializer.Deserialize<PicoStatus>(line);
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"[Serial JSON Error]: {ex.Message}");
                    }
                }
                else
                {
                    // Treat everything else as a log message
                    lock (_logLock)
                    {
                        // Remove LOG: prefix if present (for backward compatibility or explicit logging)
                        if (line.StartsWith("LOG:"))
                        {
                            _logs.Add(line.Substring(4));
                        }
                        else
                        {
                            _logs.Add(line);
                        }
                    }
                }
            }
            catch (TimeoutException) { /* Ignore timeout */ }
            catch (Exception ex)
            {
                Console.WriteLine($"Serial Read Error: {ex.Message}");
                if (_serialPort != null)
                {
                    try { _serialPort.Close(); } catch { }
                    _serialPort = null;
                }
                Thread.Sleep(1000); // Wait a bit before retrying
            }
        }
    }

    public static List<string> GetLogs()
    {
        lock (_logLock)
        {
            var logs = new List<string>(_logs);
            _logs.Clear();
            return logs;
        }
    }

    public static PicoStatus GetLatestStatus()
    {
        return _latestStatus;
    }

    // An function to read vochtigheid sensor
    public static float GetHumidity()
    {
        var status = GetLatestStatus();
        return status?.Humidity ?? -1.0f;
    }

    // An function to read lichten sterktes
    public static int[] GetLightValues()
    {
        var status = GetLatestStatus();
        if (status == null) return new int[] { -1, -1, -1 };
        return new int[] { status.Lamp1, status.Lamp2, status.Lamp3 };
    }

    // An function to run a command using a number (start pomp, stop pomp, move lampen)
    public static void SendCommand(string command, int value)
    {
        if (_serialPort == null || !_serialPort.IsOpen)
        {
            Console.WriteLine($"Cannot send command '{command}': Serial port not open.");
            return;
        }

        try
        {
            var cmdObj = new { command = command, value = value };
            string json = JsonSerializer.Serialize(cmdObj);
            _serialPort.WriteLine(json);
            Console.WriteLine($"Sent Command: {json}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Command Error: {ex.Message}");
        }
    }
}
