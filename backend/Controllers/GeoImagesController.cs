using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using NetTopologySuite.IO;
using NetTopologySuite.Features;


namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class GeoImagesController : ControllerBase
    {
        private readonly AppDbContext _context;

        public GeoImagesController(AppDbContext context)
        {
            _context = context;
        }

        [HttpGet("geojson")]
        public async Task<IActionResult> GetGeoJson()
        {
            var features = new NetTopologySuite.Features.FeatureCollection();
            var data = await _context.GeoImages.ToListAsync();

            foreach (var item in data)
            {
                var attributes = new AttributesTable
                {
                    { "productid", item.ProductId },
                    { "entityid", item.EntityId },
                    { "tipo", item.Tipo },
                    { "pr", item.Pr }
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