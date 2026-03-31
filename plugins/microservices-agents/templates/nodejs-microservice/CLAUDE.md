# {{ServiceName}}

{{ServiceDescription}}

## Stack
- Node.js 20, TypeScript, Fastify
- PostgreSQL 16 (BD propia: {{DbName}})
- Zod para validacion, Pino para logging

## Comandos
- Dev: `npm run dev`
- Build: `npm run build`
- Test: `npm test`
- Lint: `npm run lint`
- Format: `npm run format`
- Levantar BD local: `docker compose -f docker-compose.service.yml up -d`

## Dependencias con otros servicios
{{ServiceDependencies}}

## Endpoints
- GET /health — Health check

## BD propia
- Solo este servicio lee/escribe en {{DbName}}
- Ningun otro servicio accede a esta BD directamente
