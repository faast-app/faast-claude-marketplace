var builder = WebApplication.CreateBuilder(args);

builder.Configuration.AddJsonFile("ocelot.json", optional: false, reloadOnChange: true);
builder.Services.AddOcelot();
builder.Services.AddHealthChecks();

var app = builder.Build();

app.MapHealthChecks("/health");
await app.UseOcelot();

app.Run();
