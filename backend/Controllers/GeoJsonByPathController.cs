using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using NetTopologySuite.Features;
using NetTopologySuite.IO;
using backend.Models;

namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class GeoJsonByPathController : ControllerBase
    {
        private readonly AppDbContext _context;

        public GeoJsonByPathController(AppDbContext context)
        {
            _context = context;
        }

        [HttpGet]
        public async Task<IActionResult> GetByPath([FromQuery] string path)
        {
            if (string.IsNullOrWhiteSpace(path))
                return BadRequest("Query parameter 'path' is required.");

            var data = await _context.GeoImages
                .Where(g => g.ImagePath.Contains(path))
                .ToListAsync();

            if (!data.Any())
                return NotFound("No images found for the specified path.");

            var features = new FeatureCollection();

            foreach (var item in data)
            {
                var attributes = new AttributesTable
                {
                    { "productid", item.ProductId },
                    { "entityid", item.EntityId },
                    { "tipo", item.Tipo },
                    { "pr", item.Pr },
                    { "imagepath", item.ImagePath },
                    { "fire", item.Fire }
                };

                var feature = new Feature(item.Footprint, attributes);
                features.Add(feature);
            }

            var writer = new GeoJsonWriter();
            var geoJson = writer.Write(features);

            return Content(geoJson, "application/json");
        }
    }
}