using Microsoft.AspNetCore.Mvc;
using System.Net.Http;
using System.Threading.Tasks;
using System;

namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ProcessController : ControllerBase
    {
        private readonly HttpClient _httpClient;

        public ProcessController(IHttpClientFactory httpClientFactory)
        {
            _httpClient = httpClientFactory.CreateClient();
        }

        [HttpGet("start")]
        public async Task<IActionResult> StartProcessing([FromQuery] string path)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                Console.WriteLine("[ERROR] Путь не передан.");
                return BadRequest("Path is required");
            }

            var encodedPath = Uri.EscapeDataString(path);
            var pythonUrl = $"http://127.0.0.1:8000/process-folder?path={encodedPath}";
            Console.WriteLine($"[INFO] Запрос к Python-сервису: {pythonUrl}");

            try
            {
                var response = await _httpClient.GetAsync(pythonUrl);

                Console.WriteLine($"[INFO] Код ответа от Python: {response.StatusCode}");

                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    return StatusCode((int)response.StatusCode, errorContent);
                }

                var content = await response.Content.ReadAsStringAsync();
                return Ok(content);
            }
            catch (HttpRequestException ex)
            {
                Console.WriteLine($"[ERROR] HttpRequestException: {ex}");
                return StatusCode(500, $"Ошибка при обращении к Python-сервису: {ex.Message}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ERROR] Необработанное исключение: {ex}");
                return StatusCode(500, $"Необработанная ошибка: {ex.Message}");
            }
        }
    }
}
