---
description: Despliegue y operacion segun el estandar FAAST - probar en local (con BD local Docker o remota), descubrir en SOLO LECTURA que hay en un servidor sin romper nada, desplegar de forma guiada a un servidor, hacer el cutover de PM2 a Docker, o auditar un componente contra el estandar de dockerizacion. Usa el agente infra. Uso - /dev-team:deploy {subcomando}
argument-hint: 'local [servicio] | inventario {servidor|--todos} | servidor {instancia} {servicio} | bd | cutover {servicio} | estandar {servicio}'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Deploy: despliegue y operacion segura (estandar FAAST)

Pedido: $ARGUMENTS

Este comando lo ejecuta el agente `infra` siguiendo la skill `deployment-standard`. Regla
transversal: **descubrir en solo lectura, cambiar solo con plan y confirmacion** (plan
primero). Nunca borrar, nunca tumbar algo compartido, nunca reiniciar el reverse proxy,
nunca editar un vhost sin backup. Todos los valores del proyecto (servidores, registry,
instancias, BD) salen de `config.json` (`deploy`) y del inventario de servidores; si falta
alguno, preguntar una vez y persistirlo.

## `local [servicio]` — probar en la maquina del dev
1. Confirmar el **objetivo de BD** (ver `bd`): local en Docker o remota. Si no esta en config, preguntarlo.
2. Build y run segun el estandar (§9 de la skill):
   ```bash
   docker build -t local/{repo}:test .
   docker history local/{repo}:test | grep -iE "secret|token|password|key" || echo "sin secretos en capas"
   docker run --rm -u 1000:1000 -p 18080:8080 --env-file ./.env.local local/{repo}:test
   curl -fsS localhost:18080/health/live && docker exec {cid} id   # confirmar non-root
   ```
3. Para el stack completo: `docker compose -f docker-compose.dev.yml up -d` y verificar que TODOS
   los servicios estan healthy (es lo que QA exige para validar en desa). Reportar puertos y health.

## `inventario {servidor|--todos}` — que hay en el servidor (SOLO LECTURA)
NO despliega ni cambia nada. Descubre y registra. Antes de cualquier despliegue a un servidor,
corre esto primero para no tocar algo que no era del despliegue en curso.
1. Resolver el/los servidores del `config.json` (`deploy.servers`) o el inventario; si es un host
   nuevo, pedir su acceso (por el metodo del proyecto: runner, SSH, etc.) — nunca inventar credenciales.
2. Ejecutar SOLO comandos de lectura (§10 de la skill):
   ```bash
   ls -la ~/deploy/
   docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
   docker inspect {cid} --format '{{.Config.Image}} | {{.Config.User}} | {{.State.Health.Status}}'
   tail -n 20 ~/deploy/{repo}/{instancia}/deploy-history.log
   curl -fsS localhost:{HOST_PORT}/health | jq .
   docker network ls
   ```
3. Escribir/actualizar el inventario del proyecto (`deploy.inventoryPath`, default
   `.coordination/deploy/inventario-servidores.csv`) desde `templates/deploy/inventario-servidores.csv`:
   una fila por componente/instancia (componente, repo, instancia, ambiente, DNS/IP, puerto,
   carpeta de deploy, comando de logs, comando de health, notas). No escribir secretos: citar que existen.
4. Reportar al usuario: que corre, en que version (de `deploy-history.log`/`/health`), estado de
   salud, y cualquier hallazgo (contenedor unhealthy, imagen vieja, algo fuera del estandar). Sin cambiar nada.

## `servidor {instancia} {servicio}` — desplegar a un servidor (guiado, plan primero)
1. **Inventario primero** (subcomando anterior) para saber que hay y que version corre.
2. Presentar el **plan** y esperar OK: componente, version/tag a desplegar, servidor/instancia,
   que cambia, y el rollback (a que version se vuelve). Riesgos: si toca vhost, BD o afecta a otros.
3. Con el OK, en `~/deploy/{repo}/{instancia}/` (nunca crear otra ruta):
   ```bash
   # verificar .env (permisos 600, existe), NO sobreescribirlo a ciegas
   docker compose pull        # o cargar imagen: docker load < img.tar.gz
   docker compose -p {repo}-{instancia} up -d --force-recreate
   ```
4. Esperar liveness y luego gate por `/health` (readiness). Si no queda healthy: revertir con
   `docker compose up -d` a la imagen previa (del `deploy-history.log`) y reportar bloqueante.
5. Anexar la linea al `deploy-history.log` (`fecha | AMBIENTE | imagen:tag | usuario`) y actualizar el inventario.
6. Emitir el **informe de conformidad** (via handoff a QA y al Lead): componente + version exacta,
   ambiente, fecha/hora, features/fixes incluidos, health verificado. Sin este informe, QA no valida.
7. Si el destino es certificacion/puente/demo/preprod/productivo: el pase formal va por
   `/dev-team:pase` (release-manager); este subcomando NO reemplaza esa solicitud.

## `bd` — elegir base de datos local vs remota
Definir (y persistir en `config.json` → `deploy.db`) el objetivo de BD para dev local:
- **remota**: `.env.local` apunta al host de la BD de desarrollo (mas fiel; requiere acceso; no ensuciar datos compartidos)
- **local-docker**: BD en el `docker-compose.dev.yml` con datos dummy (aislada; ideal para migraciones)
En ambientes reales la BD SIEMPRE es gestionada (nunca contenedor en el servidor) y llega por
`ConnectionStrings__X`. Los tests usan Testcontainers aparte. Guardar la eleccion y explicar el efecto.

## `cutover {servicio}` — pasar de PM2 a Docker (§8 de la skill)
Playbook con plan primero y validacion de QA: contenedor healthy en el mismo puerto → smoke por el
vhost real → backup `.bak-{ts}` del vhost + `httpd -t` + cambiar ProxyPass a la nueva IP/puerto +
`reload` (nunca `restart`) → `pm2 stop` sin borrar la carpeta vieja → probar el rollback en el momento.

## `estandar {servicio}` — auditar contra el estandar de dockerizacion
Revisar el componente contra las 9 reglas duras (R1–R9), la familia de Dockerfile correcta, el
compose, la exposicion de puertos, config por env, versionado por `version.txt` y el `.dockerignore`.
Reportar por bloque (analisis, configuracion, imagen, despliegue, cierre) que cumple y que falta;
cualquier "no" bloquea el despliegue. No modifica el codigo: reporta; el dev/infra corrige.

## Reglas
- Descubrir = solo lectura. Cambiar = plan + confirmacion del usuario.
- Nunca borrar carpetas de deploy, `.env` previos, contenedores/imagenes de otros componentes.
- Nunca `docker compose down` de un servicio compartido; nunca `restart` del reverse proxy.
- Un despliegue a un ambiente real deja informe de conformidad; el pase formal va por `/dev-team:pase`.
- Secretos y `.env` reales fuera de git (permisos 600); en el inventario se cita que existen, no su valor.
