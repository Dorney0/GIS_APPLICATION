using Microsoft.AspNetCore.Mvc;
using System.Net.Http;
using System.Threading.Tasks;
using System;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using System.Linq;

namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class MaskController : ControllerBase
    {
        private readonly HttpClient _httpClient;
        private readonly AppDbContext _dbContext;

        public MaskController(IHttpClientFactory httpClientFactory, AppDbContext dbContext)
        {
            _httpClient = httpClientFactory.CreateClient();
            _dbContext = dbContext;
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

                // Парсим JSON
                var jsonDoc = JsonDocument.Parse(content);
                var root = jsonDoc.RootElement;

                // Предполагаем, что Python возвращает { "fire": true/false }
                if (root.TryGetProperty("fire", out var fireProperty))
                {
                    bool fire = fireProperty.GetBoolean();

                    // Обновляем поле Fire для всех записей с ImagePath, содержащим folderPath
                    await UpdateFireStatusForFolderAsync(folderPath, fire);
                }

                return Ok(content);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ERROR] CreateFullMask: {ex}");
                return StatusCode(500, $"Ошибка при вызове Python-сервиса: {ex.Message}");
            }
        }

        private async Task UpdateFireStatusForFolderAsync(string folderPath, bool fire)
        {
            var records = await _dbContext.GeoImages
                .Where(img => img.ImagePath.Contains(folderPath))
                .ToListAsync();

            foreach (var record in records)
            {
                record.Fire = fire;
            }

            await _dbContext.SaveChangesAsync();
        }
    }
}
