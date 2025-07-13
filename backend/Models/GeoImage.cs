using NetTopologySuite.Geometries;
using System;

namespace backend.Models
{
    public class GeoImage
    {
        public int Id { get; set; }
        public string? ProductId { get; set; }
        public string? EntityId { get; set; }
        public DateTime AcquisitionDate { get; set; }
        public float CloudCover { get; set; }
        public string? ProcessingLevel { get; set; }
        public int Path { get; set; }
        public int Row { get; set; }
        public double MinLat { get; set; }
        public double MinLon { get; set; }
        public double MaxLat { get; set; }
        public double MaxLon { get; set; }
        public string? Pr { get; set; }
        public string? Tipo { get; set; }
        public Geometry Footprint { get; set; } = default!;
    }
}