// File helper functions
namespace FileModifyDLL
{
    public class FileHelper
    {
        // Get string from user
        public static string? GetString(string? message)
        {
            System.Console.WriteLine($"{message}: ");
            return Console.ReadLine();
        }
        // Read file content
        public static string? ReadFile(string path)
        {
            return File.ReadAllText(path);
        }
        // Append text to file
        public static string? AppendToFile(string path, string value)
        {
            string error;
            try
            {
                // Append text
                File.AppendAllText(path, value);
                return "True"; // Success
            }
            catch (Exception ex)
            {
                error = ex.Message; // Capture the error message
                return error; // Indicate failure
            }
        }
        // Write text to file
        public static string? WriteFile(string path, string value)
        {
            string error;
            try
            {
                File.WriteAllText(path, value);
                return "True"; // Success
            }
            catch (Exception ex)
            {
                error = ex.Message; // Capture the error message
                return error; // Indicate failure
            }
        }
    }
}