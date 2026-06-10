# {{ProjectName}} Gateway (Traefik)

API Gateway basado en Traefik para el proyecto {{ProjectName}}.

## Stack
- Traefik v3.1
- Auto-discovery de servicios via Docker labels
- Dashboard en http://localhost:8080

## Configuracion
- `traefik.yml` — Config estatica (entrypoints, providers)
- `dynamic.yml` — Config dinamica (middlewares, routes manuales)
- Los servicios se registran via Docker labels en docker-compose.dev.yml

## Como agregar un servicio al gateway
En docker-compose.dev.yml, agregar labels al servicio:
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.{servicio}.rule=PathPrefix(`/api/{servicio}`)"
  - "traefik.http.services.{servicio}.loadbalancer.server.port=8080"
```

## Comandos
- Levantar: `docker compose -f docker-compose.gateway.yml up -d`
- Dashboard: http://localhost:8080
- Gateway: http://localhost:5000
