# Checklist de dockerización — `<componente>`

**Repo:** · **Rama:** · **Familia:** · **Instancia:** · **Responsable:** · **Fecha:**

Cualquier "no" bloquea el cutover. Se adjunta al handoff de la ola.

## 1. Análisis

- [ ] Familia asignada y justificada (D1-D7 / F1-F4 / N1 / P1).
- [ ] `TargetFramework` leído del `.csproj` — **no** del `FROM` de un Dockerfile existente.
- [ ] Nombre exacto del `.dll` de entrada verificado (no asumir `MicroservicesSolution.dll`).
- [ ] Ubicación del `.sln` y estructura multi-proyecto identificadas.
- [ ] Puerto actual del vhost y del proceso PM2 anotado (se conserva como `HOST_PORT`).
- [ ] Dependencias de SO identificadas: `System.Drawing` / Skia / Chromium / LDAP / fuentes / GemBox.
- [ ] **¿`System.Drawing` se usa de verdad?** En .NET 7+ lanza `PlatformNotSupported` en Linux.
- [ ] **`UseUrls(...)` hardcodeado: verificado que no existe** (o corregido antes de continuar).
- [ ] Rutas de disco resueltas: `cert/`, `Templates/`, `Assets/`, `FileServer/`, `Logs/`, rutas tipo `C:\` o `D:`.
- [ ] Hangfire: identificado si es host y cuál es su base de storage.
- [ ] Consumidores del componente listados (orden de cutover).
- [ ] Licencias de terceros verificadas para entorno contenedor.

## 2. Configuración

- [ ] `appsettings` real del servidor capturado en `{coordinacion}/env-reales/` (gitignored) (nunca en el repo).
- [ ] `appsettings.json` del repo **sin un solo valor real**: estructura + placeholders.
- [ ] Todas las claves mapeadas a `Seccion__Clave` y documentadas por nombre (sin valores).
- [ ] `.env.<instancia>` creado en la carpeta de instancia, permisos `600`, fuera de git.
- [ ] Certificados y credenciales de terceros montados como volumen `:ro`.
- [ ] Componente de auth: **aborta el arranque** si falta la clave de firma (+ review de cybersec).

## 3. Imagen

- [ ] Multi-stage; el SDK no está en la imagen final.
- [ ] **El Dockerfile NO crea usuario, NO hace `chown` y NO tiene `USER`** (regla dura #2).
- [ ] **`user: "${RUN_UID:-1000}:${RUN_GID:-1000}"` en el `docker-compose.yml`**, con `RUN_UID`/`RUN_GID` en el `.env.<instancia>`.
- [ ] **`id <usuario-deploy>` (en Amazon Linux suele ser `ec2-user`) ejecutado en el servidor destino** y su salida adjunta como evidencia (no se asume `1000:1000`; un default confirmado en un servidor vale solo para ese servidor).
- [ ] Verificado en caliente: `docker exec <contenedor> id` devuelve ese UID/GID y **nunca `uid=0`**.
- [ ] Frontend (F1-F4): nginx preparado para UID arbitrario — sin directiva `user`, pid y temp paths en `/tmp`, `env.js`/`health.json` generados en `/tmp` y servidos con `alias`. Verificado que arranca con `-u <uid>:<gid>` sin errores de permisos.
- [ ] D4 / N1 / P1: `HOME` (y cache) redirigidos a `/tmp` — un UID arbitrario no tiene home escribible.
- [ ] Puerto interno 8080.
- [ ] `HEALTHCHECK` real y `curl`/`wget` presente en la imagen final.
- [ ] `.dockerignore` presente y correcto.
- [ ] `docker history` sin secretos; `docker image inspect` sin `appsettings` con valores.
- [ ] Peso razonable y justificado (D1 ≈ 220 MB · D4 con Chromium 1-2 GB).
- [ ] Arranca en local y llega a `(healthy)`.

## 4. Despliegue

- [ ] `docker-compose.yml` sin literales de ambiente.
- [ ] `HOST_PORT` = el puerto que ya usa el vhost actual.
- [ ] Bind correcto según tier (loopback en público / `0.0.0.0` + SG en privado).
- [ ] Carpeta canónica `$HOME/deploy/<repo>/<instancia>/` (home del usuario de despliegue) con los 3 archivos de ADR-002 §4.3.
- [ ] `ENV_FILE_PATH` absoluto exportado por CI.
- [ ] Workflow `build-push` con `provenance: false` y tag `sha-<sha>`.
- [ ] `deploy-history.log` registrando el despliegue.

## 5. Cutover

- [ ] Contenedor `healthy` **antes** de tocar el vhost.
- [ ] Smoke por el camino real (vhost/DNS), comparado contra el proceso PM2.
- [ ] `ProxyPass` cambiado a la IP del servidor nuevo; `reload` de Apache (no restart).
- [ ] PM2 anterior **detenido, carpeta intacta**, y `pm2 save` ejecutado: el `~/.pm2/dump.pm2` lo muestra en `stopped` (si no, el arranque diario lo resucita y entra en bucle `EADDRINUSE`).
- [ ] Tras el siguiente arranque del servidor: `restart_time` del proceso PM2 detenido sin crecer y sin `EADDRINUSE` en su log de error.
- [ ] **Rollback probado en el mismo momento** y documentado.
- [ ] Hangfire: verificado que hay **una sola** instancia registrada en la base.
- [ ] QA valida con **capturas de pantalla**.

## 6. Cierre

- [ ] Handoff a lead con evidencia.
- [ ] Wiki actualizada (la mantiene el tech-writer).
- [ ] Pendientes anotados (endpoint `/health` propio, retarget, limpieza de `bin/` versionado).


## Reglas duras 2026-09-21 (Plataforma FAAST)
- [ ] Todo el appsettings a variables de entorno; diff de claves appsettings vs .env vacío (solo nombres); arranca sano sin appsettings con valores.
- [ ] /health/live y /health devuelven JSON {component, version, status, environment, commit, timestamp, checks} sin datos sensibles; versión leída de version.txt en runtime (misma fuente que Scalar/Swagger, no --build-arg); HEALTHCHECK de Docker usa /health/live; con BD caída /health = 503 y /health/live = 200.
