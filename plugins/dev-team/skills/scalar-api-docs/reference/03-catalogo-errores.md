# Catálogo de errores — Scalar

`síntoma → causa → fix → cómo verificar que el fix funcionó`.

**Leyenda:** **[V]** verificado contra la fuente o contra un repo de FaaST ·
**[G]** conocimiento general / razonado, a confirmar en el piloto.

**Regla:** si el error que tenés enfrente no está acá, se agrega cuando se resuelve.

---

## `E-SC-01` — La UI carga pero está vacía

**Síntoma.** `/scalar` devuelve la página de Scalar, con su barra lateral y todo,
pero sin un solo endpoint. A veces un cartel tipo *"Failed to fetch the OpenAPI
document"*. La consola del navegador muestra un **404** a la URL del documento.

**Causa.** El `OpenApiRoutePattern` no apunta a donde el generador sirve el JSON.
Es **el error más común de esta skill** y tiene una razón estructural: el default de
Scalar es `/openapi/{documentName}.json` [V] y el default de Swashbuckle es
`/swagger/{documentName}/swagger.json`. **No coinciden.** Quien viene de un proyecto
net9 nativo (donde sí coinciden) asume que no hay nada que configurar.

Sub-causas, en orden de frecuencia:

| | Detalle |
|---|---|
| (a) | No se llamó a `WithOpenApiRoutePattern` en un proyecto Swashbuckle |
| (b) | El `RouteTemplate` del `UseSwagger` es custom y nadie lo leyó |
| (c) | El `documentName` tiene otras mayúsculas (`backoffice` vs `BackOffice`) — Scalar lo pasa tal cual [V] |
| (d) | Se borró `app.UseSwagger()` junto con `UseSwaggerUI()` — ya no hay JSON que servir |

**Fix.** Averiguar la ruta real y declararla:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:18080/swagger/BackOffice/swagger.json
```

```csharp
options.WithOpenApiRoutePattern("/swagger/{documentName}/swagger.json")
```

**Verificación.** El `curl` de arriba da **200**, y en la pestaña Network del
navegador con `/scalar/` abierto, la petición al documento también da 200.

---

## `E-SC-02` — La UI queda en blanco · `getBasePath is not defined`

**[V] — verificado en `faast-identidad-y-acceso`, encontrado por QA el 2026-07-23.**

**Síntoma.** `/scalar/v1` devuelve **200**, pero la página queda **en blanco**. En la
consola: `getBasePath is not defined`. En Network: `scalar.js` y
`scalar.aspnetcore.js` devuelven **302** al login.

**Causa (confirmada decompilando el paquete).** `MapScalarApiReference()` registra
**dos** endpoints en el mismo grupo de rutas: el documento HTML (`/{documentName?}`)
y los **assets estáticos** (patrón `{path:regex(^scalar.*\.js$)}`). Pero el método
solo **devuelve el builder del primero**. Entonces un `.AllowAnonymous()` encadenado
sobre el valor de retorno marca **únicamente el HTML**; el endpoint de los assets,
al que no hay forma de llegar desde afuera, se queda sin marca y cae bajo el
`FallbackPolicy` global cerrado como cualquier otro endpoint sin marcar.

```csharp
// ❌ NO alcanza: marca el HTML, deja los .js detrás del login
app.MapScalarApiReference().AllowAnonymous();
```

**Fix.** Envolver la ruta en un **grupo propio** con `AllowAnonymous()` **antes** de
llamar a `MapScalarApiReference("")` sobre ese grupo — con prefijo vacío, para no
terminar en `/scalar/scalar/...`. Las convenciones del grupo externo se propagan a
los grupos anidados que la librería crea por dentro, así que los dos endpoints
quedan anónimos.

```csharp
// ✅ Correcto
var scalarGroup = app.MapGroup("/scalar").AllowAnonymous();
scalarGroup.MapScalarApiReference(string.Empty);
```

**Verificación.** Sin sesión iniciada, los **tres** dan 200:

```bash
curl -s -o /dev/null -w "%{http_code} %{url_effective}\n" -L http://localhost:18080/scalar/v1
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:18080/scalar/scalar.js
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:18080/scalar/scalar.aspnetcore.js
```

Antes del fix: el primero 200 y los otros dos **302**. Ese patrón (200 + 302 + 302)
**es la firma del bug** — si lo ves, es este.

**Aplica a:** cualquier componente con `FallbackPolicy` global que exija usuario
autenticado. En FaaST son varios. `MapOpenApi()` necesita su propio
`.AllowAnonymous()` aparte [V].

---

## `E-SC-03` — `/scalar` devuelve 301/302 y el script lo marca como fallo

**Síntoma.** El checklist pide "`/scalar` responde 200 con HTML real" y `curl` da
3xx. Parece roto; no lo está.

**Causa.** Scalar **redirige a la barra final**: sin ella, `ShouldRedirectToTrailingSlash`
manda a `/scalar/` [V] (`ScalarEndpointRouteBuilderExtensions.cs`).

**Fix.** Usar `-L`, o pedir `/scalar/` directamente. En `verificar-scalar.sh` ya está.

**Verificación.**

```bash
curl -sL -o /dev/null -w "%{http_code}\n" http://localhost:18080/scalar   # 200
```

**No confundir con E-SC-02**, donde el 302 va **al login** y no a la barra final.
Mirá el `Location`: `/scalar/` es esto; `/login` o `/Account/...` es E-SC-02.

---

## `E-SC-04` — No aparece ningún botón de autenticación

**Síntoma.** La UI muestra los endpoints, pero no hay dónde poner el JWT y "Try it"
devuelve 401.

**Causa.** El documento OpenAPI **no declara security schemes**. Scalar solo muestra
lo que está en el documento — textual de la doc [V]. **El problema no está en
Scalar**, y ahí se pierde el tiempo: se configuran opciones de Scalar cuando lo que
falta está en el generador.

**Fix.** Según la rama:

- **Swashbuckle (A):** que exista `AddSecurityDefinition("Bearer", ...)` +
  `AddSecurityRequirement(...)` en el `AddSwaggerGen`. Test rápido: si SwaggerUI
  mostraba el botón "Authorize", el esquema ya está y esto **no** es tu error [G].
- **Nativo (B):** agregarlo con un `AddDocumentTransformer`. Tener `AddJwtBearer` en
  el DI **no** alcanza [V]. Código en `02-api-verificada.md` §6.

**Verificación.** El documento trae el esquema:

```bash
curl -s http://localhost:18080/swagger/BackOffice/swagger.json | jq '.components.securitySchemes'
```

No debe ser `null`. Después, en la UI: botón de auth visible, se pega un JWT real y
un endpoint protegido devuelve 200 (no 401).

---

## `E-SC-05` — Scalar muestra una versión distinta a `/health`

**[V] — encontrado en apiback el 2026-09-22.**

**Síntoma.** `/health` dice `2.0.34` y el encabezado de la documentación dice otra
cosa (o `1.0.0`, o una versión vieja congelada).

**Causa.** **Dos fuentes para el mismo número.** En apiback, `Info.Version` de los
dos `SwaggerDoc(...)` leía `File.ReadAllText(..., "version.txt")` por su cuenta
mientras `/health` resolvía la versión por otro mecanismo. También pasa con
`Version = "1.0.0"` hardcodeado, que deja la UI congelada para siempre.

**Fix.** La regla dura de la skill: **todo** lo que muestre la versión lee del mismo
`version.txt`, vía un helper cacheado.

```csharp
var appVersion = VersionInfo.Current;      // una lectura, cacheada
// health  → appVersion
// OpenApiInfo.Version (cada SwaggerDoc)   → appVersion
// document.Info.Version (transformer)     → appVersion
```

Un `ARG VERSION` en el Dockerfile, si existe, es solo para **taguear la imagen**;
nunca la fuente que lee la app.

**Verificación.** Los tres valores coinciden:

```bash
docker build -t local/<repo>:test .
docker run -d --rm -p 18080:8080 --name t local/<repo>:test
curl -s localhost:18080/health | jq -r .version
curl -s localhost:18080/swagger/BackOffice/swagger.json | jq -r .info.version
docker exec t cat /app/version.txt
```

Las tres cadenas **idénticas**. Automatizado en `templates/verificar-scalar.sh`.

---

## `E-SC-06` — CORS al cargar un documento externo

**Síntoma.** UI vacía y la consola dice *blocked by CORS policy*. El documento vive
en **otro host** que la UI.

**Causa.** `AddDocument(..., routePattern: "https://otro-host/openapi.json")` hace
que el **navegador** pida el documento a ese host; si no manda
`Access-Control-Allow-Origin`, se bloquea. [V] que Scalar acepta URLs externas ·
[G] la consecuencia CORS.

**Fix.** En orden de preferencia: (1) servir el documento desde el mismo origen
(lo normal en FaaST); (2) habilitar CORS en el host que lo sirve; (3)
`WithProxy(...)` [V] — no probado acá.

**Verificación.** Documento y UI comparten esquema+host+puerto, o la respuesta del
documento trae `Access-Control-Allow-Origin`.

> En la configuración recomendada (documento local, mismo host) **CORS no se toca.**
> Si estás configurando CORS para que Scalar funcione, revisá si no estás en E-SC-01.

---

## `E-SC-07` — Conflicto de rutas con SwaggerUI o ReDoc conviviendo

**Síntoma.** Durante la migración, con las dos UIs montadas, una deja de responder
o `/docs` muestra la equivocada. En el arranque puede aparecer una excepción de ruta
duplicada [G].

**Causa.** Dos endpoints con el mismo prefijo. Típico: ReDoc en `/docs` y alguien
monta Scalar en `/docs`; o SwaggerUI con `RoutePrefix = ""` (raíz) tragándose todo.

**Fix.** Prefijos distintos y explícitos mientras dure la convivencia:

| UI | Ruta |
|---|---|
| Scalar | `/scalar` ← convención de la flota |
| SwaggerUI (temporal) | `/swagger` |
| ReDoc (si existe) | la que ya tenía |

Nunca la raíz para ninguna de las tres. Y **`{documentName}` no puede ir en el
prefijo de Scalar: lanza `ArgumentException`** al arrancar [V].

**Verificación.** Las rutas responden cada una lo suyo y el log de arranque no tiene
excepciones de routing.

---

## `E-SC-08` — Funciona en local, 404 detrás del proxy

**Síntoma.** `/scalar` perfecto en `localhost:18080`, 404 o UI rota a través de
Apache/el gateway. [G] — probable en FaaST por el esquema de vhosts, **no
verificado todavía en un ambiente real**.

**Causa.** El componente se sirve bajo un subpath (`/api-back/...`) y el `ProxyPass`
no incluye la ruta de la documentación, o la incluye sin reescribir bien.

**Fix.** Revisar el vhost. Scalar tiene documentación específica de *subpath
deployment* (`integrations/dotnet/aspnetcore/docs/subpath-deployment.md`) [V que
existe] — leerla cuando toque el primer componente detrás de subpath.

**Verificación.** Por el camino real (a través del vhost), no por `localhost`.
Mismo criterio que el smoke de `dockerizar-componente` Paso 6.

**Pendiente:** confirmar en el piloto y volver con el detalle.

---

## `E-SC-10` — `/scalar/{documentName}` sirve documentación vacía, solo `/scalar/` funciona

**Síntoma.** `/scalar/` (o `/scalar/v1`, la ruta base) carga bien y muestra los
endpoints. Pero `/scalar/{OtroDocumento}` — o cualquier link directo a un documento
específico en un A2 con varios `SwaggerDoc` — carga la UI vacía o en blanco, sin
error visible en el navegador.

**Causa [V, verificado en el binario y reproducido en vivo, 2026-09-22].**
`MapScalarApiReference` resuelve `/{documentName?}` por dos caminos distintos:
- `/scalar/` (sin nombre) → SÍ usa los `AddDocument(...)` ya registrados, **incluido**
  cualquier `routePattern` pasado como 3er argumento posicional.
- `/scalar/{nombre}` → **descarta** los `AddDocument` y arma un source sintético con
  `url = options.OpenApiRoutePattern` (el campo GLOBAL, no el de `AddDocument`). Si
  nadie llamó `WithOpenApiRoutePattern(...)`, ese campo vale el default del
  generador nativo de .NET 9+: `/openapi/{documentName}.json` — que en un repo con
  Swashbuckle clásico (rama A1/A2 de esta skill) **no existe**, 404.

Es decir: `AddDocument(name, title, routePattern)` con el 3er argumento **no
sustituye** a `WithOpenApiRoutePattern(...)` global — cubre solo la mitad de las
rutas por las que un usuario real llega a la documentación (bookmarks, links
directos a un documento, o simplemente escribir la URL a mano).

**Fix.** `WithOpenApiRoutePattern(...)` **NO es opcional en A1 ni en A2**, aunque
cada `AddDocument` reciba su propio `routePattern`. Es un fixture global antes de
la cadena de `AddDocument`:

```csharp
options
    .WithOpenApiRoutePattern("/swagger/{documentName}/swagger.json")
    .AddDocument("BackOffice", "API BACK OFFICE", isDefault: true)
    .AddDocument("GestionCobranza", "API BACK GESTION COBRANZA");
```

Los templates de esta skill (`templates/scalar-swashbuckle.cs`) ya mostraban este
patrón correcto — el error real fue una implementación que se desvió del template
usando el 3er argumento de `AddDocument` en su lugar, creyendo (razonablemente,
por el nombre del parámetro) que alcanzaba.

**Verificación (agregar SIEMPRE al checklist, no solo `/scalar/`).** Probar
explícitamente **cada** `/scalar/{documentName}` de la lista de documentos, no solo
la ruta base:

```bash
for doc in BackOffice GestionCobranza; do
  curl -s "https://<host>/scalar/${doc}" | grep -o '"url":"[^"]*"'
done
# Debe mostrar la ruta REAL del swagger.json (/swagger/...), nunca openapi/...
```

**Componentes ya corregidos:** `micro-api-back`, `micro-backoffice` (2026-09-22,
commits `f9e406a` y `3fefdc3`). Cualquier otro componente que haya adoptado Scalar
antes de esta fecha con el patrón de `AddDocument(name, title, routePattern)` sin
`WithOpenApiRoutePattern` global tiene el mismo defecto — auditar.

---

## `E-SC-09` — La tipografía se ve distinta / tarda en un ambiente cerrado

**Síntoma.** La UI funciona pero se ve con otra fuente, o tarda en pintar, en un
ambiente sin salida a internet.

**Causa.** Las fuentes se cargan de un CDN por default [V]. El **bundle JS no**: va
embebido en el assembly [V], así que la UI no se rompe, solo cambia la tipografía.

**Fix.** `options.DisableDefaultFonts()` [V] en ambientes cerrados.

**Verificación.** Con la red externa bloqueada, `/scalar/` sigue dando 200 y pintando
los endpoints.
