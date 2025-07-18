using backend;
using Microsoft.AspNetCore.Http.Features;
using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi.Models;
using Swashbuckle.AspNetCore.SwaggerGen;

var builder = WebApplication.CreateBuilder(args);

// Добавление контроллеров
builder.Services.AddControllers();
builder.Services.AddHttpClient();
// Добавление Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "GeoImages API",
        Version = "v1",
        Description = "API для получения геоданных GeoImages с использованием PostGIS"
    });
    
});


// Подключение к PostgreSQL + NetTopologySuite
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(
        builder.Configuration.GetConnectionString("DefaultConnection"),
        x => x.UseNetTopologySuite()
    ));

// CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
            .AllowAnyHeader()
            .AllowAnyMethod();
    });
});

// Регистрация MoveFilesToProductFolder
builder.Services.AddScoped<backend.Service.MoveFilesToProductFolder>();
builder.Services.Configure<FormOptions>(options =>
{
    options.MultipartBodyLengthLimit = 2_000_000_000; // 2 ГБ, например
});

builder.WebHost.ConfigureKestrel(serverOptions =>
{
    serverOptions.Limits.MaxRequestBodySize = 2_000_000_000; // 2 ГБ
});

var app = builder.Build();

app.UseRouting();

app.UseCors("AllowAll");

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseAuthorization();

app.MapControllers();

app.Run();
