# {{ServiceName}}

{{ServiceDescription}}

## Stack
- .NET 8, C# 12, ASP.NET Core
- PostgreSQL 16 (BD propia: {{DbName}})
- Entity Framework Core 8
- Serilog para logging estructurado

## Comandos
- Build: `dotnet build src/`
- Test: `dotnet test tests/`
- Run: `dotnet run --project src/`
- Format: `dotnet format src/`
- Levantar BD local: `docker compose -f docker-compose.service.yml up -d`

## Dependencias con otros servicios
{{ServiceDependencies}}

## Endpoints
- GET /health — Health check

## BD propia
- Solo este servicio lee/escribe en {{DbName}}
- Ningun otro servicio accede a esta BD directamente
