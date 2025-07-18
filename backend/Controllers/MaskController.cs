using Microsoft.AspNetCore.Mvc;
using System.Net.Http;
using System.Threading.Tasks;
using System;

namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class MaskController : ControllerBase
    {
        private readonly HttpClient _httpClient;

        public MaskController(IHttpClientFactory httpClientFactory)
        {
            _httpClient = httpClientFactory.CreateClient();
        }

        [HttpGet("create")]
        public async Task<IActionResult> CreateFullMask([FromQuery] string folderPath)
        {
            if (string.IsNullOrWhiteSpace(folderPath))
                return BadRequest("folderPath is required");

            var encodedPath = Uri.EscapeDataString(folderPath);
            var pythonUrl = $"http://127.0.0.1:8000/create-full-mask/?folder_path={encodedPath}";

            try
            {
                var response = await _httpClient.GetAsync(pythonUrl);
                var content = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                    return StatusCode((int)response.StatusCode, content);

                return Ok(content);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ERROR] CreateFullMask: {ex}");
                return StatusCode(500, $"Ошибка при вызове Python-сервиса: {ex.Message}");
            }
        }
    }
}