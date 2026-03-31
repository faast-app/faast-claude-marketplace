# {{ProjectName}} Gateway (YARP)

API Gateway basado en YARP (.NET) para el proyecto {{ProjectName}}.

## Stack
- .NET 8, YARP (Yet Another Reverse Proxy)
- Configuracion en appsettings.json

## Como agregar una ruta
En `src/appsettings.json`, seccion ReverseProxy:
```json
{
  "Routes": {
    "user-route": {
      "ClusterId": "user-cluster",
      "Match": { "Path": "/api/users/{**catch-all}" }
    }
  },
  "Clusters": {
    "user-cluster": {
      "Destinations": {
        "default": { "Address": "http://user-service:8080" }
      }
    }
  }
}
```

## Comandos
- Build: `dotnet build src/`
- Run: `dotnet run --project src/`
