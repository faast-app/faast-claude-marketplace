# Checklist de dockerizacion y despliegue — {componente}

> Auditoria contra el estandar FAAST (skill `deployment-standard`). Cualquier "no" en un
> item duro BLOQUEA el despliegue. Marca con evidencia (salida de comando, linea del archivo).

## 1. Analisis
- [ ] Familia de Dockerfile correcta para lo que ES el componente (D1–D7 / F1–F4 / N1 / P1)
- [ ] Puerto interno del componente identificado; el estandar lo unifica en `8080` (R1)
- [ ] `version.txt` presente y leido por la app en runtime (fuente unica de version)

## 2. Configuracion
- [ ] Todo el `appsettings` mapeado a variables de entorno (`Seccion__Clave`); repo con `SET_VIA_ENV`
- [ ] Diff vacio entre claves del appsettings y el `.env.<instancia>`
- [ ] `.env` con permisos 600 y fuera de git; secretos por Environment o mount, nunca en imagen (R4)
- [ ] Componente con auth: aborta el arranque si falta la clave de firma (sin fallback silencioso)
- [ ] Certificados / `ocelot.json` / credenciales de terceros montados `:ro`

## 3. Imagen
- [ ] Multi-stage (R5); imagen base pinneada por version, nunca `latest`
- [ ] `.dockerignore` presente con el minimo (`**/bin`, `**/obj`, `**/node_modules`, `.git`, `.env*`) (R6)
- [ ] `docker history` sin secretos en capas (R4)
- [ ] HEALTHCHECK real que usa herramientas que la imagen SI tiene (R3)
- [ ] Logs a stdout/stderr (R7)
- [ ] Frontend/nginx: preparado para UID arbitrario (sin directiva `user`, pid/temp en `/tmp`)

## 4. Compose y ejecucion
- [ ] `user: "${RUN_UID:-1000}:${RUN_GID:-1000}"`, non-root confirmado con `docker exec ... id` (R2)
- [ ] `init: true` (R9); `restart: unless-stopped`; `mem_limit`; logging json-file (10m × 3)
- [ ] Un compose por repo, byte-identico entre ambientes; diferencias solo en `.env.<instancia>`
- [ ] `provenance: false` y tag permanente `sha-<sha>` (R8)
- [ ] Bind correcto: capa publica `127.0.0.1:${HOST_PORT}:8080`; nada interno expuesto a internet

## 5. Despliegue
- [ ] Carpeta en el servidor `~/deploy/<repo>/<instancia>/` (ADR-002), sin subcarpetas de version
- [ ] `deploy-history.log` con una linea por despliegue (`fecha | AMBIENTE | imagen:tag | usuario`)
- [ ] Health verificado tras desplegar; informe de conformidad emitido (sin el, QA no valida)
- [ ] Rollback probado / documentado (a que version se vuelve)

## 6. Cierre
- [ ] Inventario de servidores del proyecto actualizado con este componente/instancia
- [ ] Si el destino es cert/puente/demo/preprod/productivo: pase formal via `/dev-team:pase`
- [ ] Sin cambios fuera del alcance; nada borrado de otros componentes
