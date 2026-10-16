# Checklist de migración a Scalar — `<componente>`

**Repo:** · **Rama:** · **Rama del árbol (A1/A2/B/C1/C2/C3/D):** · **Responsable:** · **Fecha:**

Cualquier "no" bloquea el PR. Se adjunta al handoff.

> Si la clasificación dio **C3 (gateway sin OpenAPI propio)**: se completa solo la
> sección 1, se marca **N/A** con la salida del `grep` como evidencia, y se cierra.
> No se instala el paquete.

## 1. Clasificación

- [ ] `grep` del Paso 1 corrido y **pegado en el informe** (es la evidencia de la rama).
- [ ] Generador de OpenAPI identificado (Swashbuckle / nativo / SwaggerForOcelot / NSwag / ninguno).
- [ ] **Ruta real del documento** leída del `RouteTemplate`/`MapSwagger`, no asumida.
- [ ] Nombres de los documentos anotados **con sus mayúsculas exactas**.
- [ ] Verificado si existe ReDoc u otra UI (decisión D-1: se deja intacta).
- [ ] Verificado si hay `FallbackPolicy` global cerrado (si sí → E-SC-02 aplica).
- [ ] Componente con auth/firma/cifrado: marcado para review de cybersec.

## 2. Cambio

- [ ] `Scalar.AspNetCore` agregado **con versión pineada** (no flotante).
- [ ] `app.UseSwagger()` / `MapOpenApi()` **intactos** — solo se quitó la UI.
- [ ] `UseSwaggerUI(...)` eliminado (o convivencia con fecha de corte — decisión D-4).
- [ ] Rutas de los documentos OpenAPI **sin cambios** (las consumen gateways y Postman).
- [ ] ReDoc y otras vistas existentes **sin tocar**.
- [ ] Ruta de la UI = **`/scalar`** (o desvío justificado por escrito).
- [ ] `WithOpenApiRoutePattern` declarado **siempre** que el generador no sirva en `/openapi/{documentName}.json` — **incluso si cada `AddDocument` ya recibe su propio `routePattern`** (E-SC-10: ese 3er argumento no cubre `/scalar/{documentName}`, solo `/scalar/`).
- [ ] Un `AddDocument(...)` por cada documento, con `isDefault` en el principal.
- [ ] Probado `/scalar/{documentName}` para **cada** documento (no solo `/scalar/` a secas) — ver E-SC-10.
- [ ] **Sin credenciales precargadas** (`auth.Token = "..."`) fuera de local — Regla 5.
- [ ] Sin tema ni dark mode forzado, salvo decisión explícita de flota.
- [ ] Un solo cambio en el PR: la UI. Nada de generador, contrato ni refactors.

## 3. Versión única (regla dura)

- [ ] La app lee la versión **de `version.txt`**, en runtime, vía helper cacheado.
- [ ] `version.txt` **se copia al output de publish / a la imagen**.
- [ ] `Info.Version` de **cada** documento usa ese mismo valor.
- [ ] `/health` usa **ese mismo valor** (la misma propiedad, no otra lectura).
- [ ] **Ninguna** versión hardcodeada (`Version = "1.0.0"`, `"v1"`, …).
- [ ] **Ninguna** versión desde `AssemblyInformationalVersion` / `ARG VERSION` como fuente de la app.
- [ ] Si hay `ARG VERSION` en el Dockerfile: se usa **solo para taguear la imagen**.

## 4. Verificación (con el componente corriendo)

- [ ] `dotnet build` limpio, sin warnings nuevos.
- [ ] `curl -sL /scalar` → **200** y el cuerpo es **HTML real** (no JSON, no 3xx sin seguir).
- [ ] La UI **pinta los endpoints** en el navegador (no una página vacía — E-SC-01).
- [ ] **Cada** documento carga desde el selector de la UI.
- [ ] `scalar.js` y `scalar.aspnetcore.js` → **200** en las mismas condiciones que un usuario real (E-SC-02).
- [ ] Botón de autenticación visible; con un JWT real, **"Try it" devuelve 200** en un endpoint protegido.
- [ ] `/health.version` == `info.version` del documento == contenido de `version.txt`. **Las tres iguales.**
- [ ] **Diff de contrato OpenAPI antes/después: vacío.** Si cambió, se cambió algo que no era la UI.
- [ ] Verificado **por el camino real** (a través del vhost/proxy), no solo `localhost` (E-SC-08).
- [ ] `templates/verificar-scalar.sh` pasa entero.

## 5. Cierre

- [ ] Errores del catálogo que aparecieron, anotados (y los nuevos, **agregados al catálogo**).
- [ ] Decisión sobre SwaggerUI: quitada / convive hasta `<fecha>`.
- [ ] Decisión sobre ReDoc registrada (D-1).
- [ ] Ambientes donde queda expuesto `/scalar`, registrado (D-2).
- [ ] Informe en `{coordinacion}/inventario/migracion/<repo>.md` con la sección de Scalar.
- [ ] Handoff al lead. Si toca auth → handoff a cybersec **antes** del cutover.
