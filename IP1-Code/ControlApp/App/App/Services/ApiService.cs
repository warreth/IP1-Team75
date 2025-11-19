using System;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;

namespace App.Services;

public class ApiService
{
    private readonly HttpClient _client;

    public ApiService()
    {
        // WARNING: This bypasses SSL certificate validation and is INSECURE. Use only for development with self-signed certificates.
        var handler = new HttpClientHandler();
        handler.ServerCertificateCustomValidationCallback = (message, cert, chain, errors) => true;
        _client = new HttpClient(handler);
    }
    public async Task<string> ContactUrlAsync(string pUrl, string endpoint)
    {
        if (string.IsNullOrWhiteSpace(pUrl))
            throw new ArgumentException("API URL cannot be null or empty.", nameof(pUrl));
        if (string.IsNullOrWhiteSpace(endpoint))
            throw new ArgumentException("Endpoint cannot be null or empty.", nameof(endpoint));

        string fullUrl = $"{pUrl.TrimEnd('/')}/{endpoint.TrimStart('/')}";

        try
        {
            HttpResponseMessage response = await _client.GetAsync(fullUrl);

            if (response.IsSuccessStatusCode)
            {
                string jsonContent = await response.Content.ReadAsStringAsync();

                if (string.IsNullOrEmpty(jsonContent))
                {
                    return "Error: Received empty JSON content.";
                }
                //Parse the json
                using (JsonDocument doc = JsonDocument.Parse(jsonContent))
                {
                    JsonElement root = doc.RootElement;

                    if (root.ValueKind == JsonValueKind.Object)
                    {
                        //Use first json property
                        foreach (JsonProperty property in root.EnumerateObject())
                        {
                            JsonElement valueElement = property.Value;

                            switch (valueElement.ValueKind)
                            {
                                case JsonValueKind.String:
                                    return valueElement.GetString() ?? string.Empty;
                                default:
                                    return valueElement.GetRawText();
                            }
                        }
                        // If the foreach loop completes, the JSON object was empty (no properties).
                        return "Error: JSON object is empty (contains no properties).";
                    }
                    else
                    {
                        return "Error: Root of JSON content is not an object.";
                    }
                }
            }
            else
            {
                return $"Error: HTTP request failed with status code {response.StatusCode}";
            }
        }
        catch (JsonException e) // Handles errors from JsonDocument.Parse
        {
            return $"JsonError: Failed to parse JSON content. Message: {e.Message}";
        }
        catch (HttpRequestException e) // Handles network errors or other HTTP issues
        {
            return $"HttpError: Request to {fullUrl} failed. Message: {e.Message}";
        }
        catch (Exception e) // Catch-all for other unexpected errors
        {
            return $"UnexpectedError: An unexpected error occurred. Message: {e.Message}";
        }
    }

    public async Task<string?> GetRawJsonAsync(string pUrl, string endpoint)
    {
        if (string.IsNullOrWhiteSpace(pUrl)) return null;
        string fullUrl = $"{pUrl.TrimEnd('/')}/{endpoint.TrimStart('/')}";
        try
        {
            return await _client.GetStringAsync(fullUrl);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"API Error: {ex.Message}");
            return null;
        }
    }
}
