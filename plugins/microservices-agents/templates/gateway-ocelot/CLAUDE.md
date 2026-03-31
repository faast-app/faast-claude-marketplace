# {{ProjectName}} Gateway (Ocelot)

API Gateway basado en Ocelot (.NET) para el proyecto {{ProjectName}}.

## Stack
- .NET 8, Ocelot
- Configuracion en ocelot.json

## Como agregar una ruta
En `src/ocelot.json`, seccion Routes:
```json
{
  "UpstreamPathTemplate": "/api/users/{everything}",
  "UpstreamHttpMethod": ["GET", "POST", "PUT", "DELETE"],
  "DownstreamPathTemplate": "/api/users/{everything}",
  "DownstreamScheme": "http",
  "DownstreamHostAndPorts": [
    { "Host": "user-service", "Port": 8080 }
  ]
}
```

## Comandos
- Build: `dotnet build src/`
- Run: `dotnet run --project src/`
