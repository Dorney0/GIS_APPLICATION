using Microsoft.AspNetCore.Mvc;
using System.Net.Http;
using System.Threading.Tasks;
using System;

namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class FireMaskController : ControllerBase
    {
        private readonly HttpClient _httpClient;

        public FireMaskController(IHttpClientFactory httpClientFactory)
        {
            _httpClient = httpClientFactory.CreateClient();
        }

        [HttpGet("detect")]
        public async Task<IActionResult> DetectFireMask([FromQuery] string maskPath)
        {
            if (string.IsNullOrWhiteSpace(maskPath))
                return BadRequest("maskPath is required");

            var encodedPath = Uri.EscapeDataString(maskPath);
            var pythonUrl = $"http://127.0.0.1:8000/detect-fire-mask/?mask_path={encodedPath}";

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
                Console.WriteLine($"[ERROR] DetectFireMask: {ex}");
                return StatusCode(500, $"Ошибка при вызове Python-сервиса: {ex.Message}");
            }
        }
    }
}