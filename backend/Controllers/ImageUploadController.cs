using Microsoft.AspNetCore.Mvc;
using backend.Models;
using backend.Service;
using System.IO;
using System.Text.RegularExpressions;
using NetTopologySuite.Geometries;
using System.Linq;
using System.Collections.Generic;
using System;
using System.Globalization;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;

namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ImageUploadController : ControllerBase
    {
        private readonly AppDbContext _context;
        private readonly MoveFilesToProductFolder _fileMover;
        private readonly string _uploadRoot = "geo-images";

        public ImageUploadController(AppDbContext context, MoveFilesToProductFolder fileMover)
        {
            _context = context;
            _fileMover = fileMover;

            if (!Directory.Exists(_uploadRoot))
                Directory.CreateDirectory(_uploadRoot);
        }

        [HttpPost("upload")]
        [Consumes("multipart/form-data")]
        public async Task<IActionResult> UploadImage([FromForm] List<IFormFile> files)
        {
            Console.WriteLine($"[UploadImage] Получено файлов: {(files?.Count ?? 0)}");

            if (files == null || files.Count == 0)
            {
                Console.WriteLine("[UploadImage] Ошибка: файлы не загружены");
                return BadRequest("No files uploaded.");
            }

            var tempFolder = Path.Combine(Directory.GetCurrentDirectory(), "temp-upload");
            if (!Directory.Exists(tempFolder))
            {
                Console.WriteLine($"[UploadImage] Создаю временную папку: {tempFolder}");
                Directory.CreateDirectory(tempFolder);
            }

            // Сохраняем файлы во временную папку
            foreach (var file in files)
            {
                var filePath = Path.Combine(tempFolder, file.FileName);

                // Получаем путь папки, в которой должен быть файл
                var directory = Path.GetDirectoryName(filePath);
                if (!Directory.Exists(directory))
                    Directory.CreateDirectory(directory);

                using (var memoryStream = new MemoryStream())
                {
                    await file.CopyToAsync(memoryStream);
                    await System.IO.File.WriteAllBytesAsync(filePath, memoryStream.ToArray());
                }
            }

            var mtlFile = Directory.GetFiles(tempFolder, "*MTL.txt", SearchOption.AllDirectories).FirstOrDefault();
            if (mtlFile == null)
            {
                Console.WriteLine("[UploadImage] Ошибка: MTL файл не найден");
                return BadRequest("MTL file not found in uploaded files.");
            }
            Console.WriteLine($"[UploadImage] Найден MTL файл: {mtlFile}");

            var metadata = ParseMtlFile(mtlFile, tempFolder);
            Console.WriteLine($"[UploadImage] Спарсены метаданные: ProductId={metadata.ProductId}, EntityId={metadata.EntityId}");

            _context.GeoImages.Add(metadata);
            await _context.SaveChangesAsync();
            Console.WriteLine("[UploadImage] Метаданные сохранены в базу");

            if (string.IsNullOrEmpty(metadata.ProductId))
            {
                Console.WriteLine("[UploadImage] Ошибка: ProductId пустой");
                return BadRequest("ProductId is null or empty.");
            }

            var finalPath = _fileMover.MoveFiles(tempFolder, metadata.ProductId);
            Console.WriteLine($"[UploadImage] Файлы перемещены в: {finalPath}");

            metadata.ImagePath = finalPath;
            await _context.SaveChangesAsync();
            Console.WriteLine("[UploadImage] Обновлен путь ImagePath и сохранен");

            return Ok(new
            {
                message = "Metadata parsed, saved and files moved",
                productId = metadata.ProductId,
                imagePath = finalPath
            });
        }


        private GeoImage ParseMtlFile(string mtlFile, string imgPath)
        {
            var md = new GeoImage();
            var text = System.IO.File.ReadAllText(mtlFile);

            var rx = new Regex(@"^\s*(\w+)\s*=\s*([^\r\n]+)", RegexOptions.Multiline);

            foreach (Match m in rx.Matches(text))
            {
                var k = m.Groups[1].Value;
                var v = m.Groups[2].Value.Trim().Trim('"');

                switch (k)
                {
                    case "LANDSAT_PRODUCT_ID": md.ProductId = v; break;
                    case "LANDSAT_SCENE_ID": md.EntityId = v; break;
                    case "DATE_ACQUIRED":
                        if (DateTime.TryParse(v, out var dt))
                            md.AcquisitionDate = DateTime.SpecifyKind(dt, DateTimeKind.Utc);
                        break;
                    case "CLOUD_COVER":
                        if (float.TryParse(v, NumberStyles.Float, CultureInfo.InvariantCulture, out var fl))
                            md.CloudCover = fl;
                        break;
                    case "PROCESSING_LEVEL": md.ProcessingLevel = v; break;
                    case "WRS_PATH":
                        if (int.TryParse(v, out var p)) md.Path = p;
                        break;
                    case "WRS_ROW":
                        if (int.TryParse(v, out var r)) md.Row = r;
                        break;
                    case "PR": md.Pr = v; break;
                    case "TIPO": md.Tipo = v; break;
                }
            }

            var corners = new[] { "UL", "UR", "LR", "LL" };
            var coords = new List<Coordinate>();
            foreach (var corner in corners)
            {
                var lat = GetDoubleValue(text, $"CORNER_{corner}_LAT_PRODUCT");
                var lon = GetDoubleValue(text, $"CORNER_{corner}_LON_PRODUCT");
                coords.Add(new Coordinate(lon, lat));
            }
            coords.Add(coords[0]);

            md.Footprint = new Polygon(new LinearRing(coords.ToArray()));
            md.MinLat = coords.Min(c => c.Y);
            md.MaxLat = coords.Max(c => c.Y);
            md.MinLon = coords.Min(c => c.X);
            md.MaxLon = coords.Max(c => c.X);
            md.ImagePath = imgPath;

            return md;
        }

        private double GetDoubleValue(string text, string key)
        {
            var rx = new Regex($"{key}\\s*=\\s*([\\d\\.\\-Ee]+)", RegexOptions.IgnoreCase);
            var match = rx.Match(text);
            if (match.Success && double.TryParse(match.Groups[1].Value, NumberStyles.Float, CultureInfo.InvariantCulture, out var val))
                return val;
            return 0.0;
        }
    }
}
