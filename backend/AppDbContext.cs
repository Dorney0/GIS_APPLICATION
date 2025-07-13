using Microsoft.EntityFrameworkCore;
using backend.Models;

namespace backend
{
    public class AppDbContext : DbContext
    {
        public DbSet<GeoImage> GeoImages { get; set; }

        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<GeoImage>(entity =>
            {
                entity.ToTable("geo_images"); 
        
                entity.Property(e => e.Id).HasColumnName("id");
                entity.Property(e => e.ProductId).HasColumnName("productid");
                entity.Property(e => e.EntityId).HasColumnName("entityid");
                entity.Property(e => e.AcquisitionDate).HasColumnName("acquisitiondate");
                entity.Property(e => e.CloudCover).HasColumnName("cloudcover");
                entity.Property(e => e.ProcessingLevel).HasColumnName("processinglevel");
                entity.Property(e => e.Path).HasColumnName("path");
                entity.Property(e => e.Row).HasColumnName("row");
                entity.Property(e => e.MinLat).HasColumnName("min_lat");
                entity.Property(e => e.MinLon).HasColumnName("min_lon");
                entity.Property(e => e.MaxLat).HasColumnName("max_lat");
                entity.Property(e => e.MaxLon).HasColumnName("max_lon");
                entity.Property(e => e.Pr).HasColumnName("pr");
                entity.Property(e => e.Tipo).HasColumnName("tipo");
                entity.Property(e => e.Footprint).HasColumnName("footprint");
            });
        }

    }
}