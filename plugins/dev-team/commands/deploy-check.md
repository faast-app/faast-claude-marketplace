---
description: Verifica que un servicio esta listo para deploy (Dockerfile, tests, health check, CI/CD)
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


Verifica readiness para deploy del servicio actual, contra el estandar FAAST (skill
`deployment-standard`; para desplegar u operar el servidor usa `/dev-team:deploy`):

1. **Dockerfile (reglas duras R1–R9):**
   - Multi-stage (R5)? HEALTHCHECK real (R3)? Non-root por UID del host (R2)? Imagen pinneada (no `latest`)?
   - Un solo puerto interno `8080` (R1)? `.dockerignore` presente (R6)? `init:true` y logs a stdout (R7,R9)?
   - `docker history` sin secretos en capas (R4)? `provenance:false` + tag `sha-<sha>` (R8)?
   - `version.txt` como fuente unica de version? `appsettings` mapeado a variables de entorno?

2. **Tests:**
   - Ejecutar suite de tests del stack detectado
   - Todos pasan? Cobertura aceptable?

3. **Health check:**
   - Endpoint `/health` implementado?
   - Responde correctamente?

4. **CI/CD:**
   - Existe `.github/workflows/`?
   - El workflow incluye build + test + push?

5. **Configuracion:**
   - `.env.example` existe y documenta todas las variables?
   - No hay secrets hardcodeados?

6. **OpenAPI:**
   - `docs/openapi.yml` existe y esta actualizado?

7. **Resumen:**
   - Servicio: {nombre}
   - Dockerfile: OK/FALTA
   - Tests: X passed / Y total
   - Health check: OK/FALTA
   - CI/CD: OK/FALTA
   - Secrets: OK/ENCONTRADOS
   - Veredicto: LISTO PARA DEPLOY / CORREGIR ANTES
