# Árbol de decisión, rama por rama

La pregunta única: **¿qué genera hoy el documento OpenAPI de este componente?**

```bash
grep -n "AddSwaggerGen\|UseSwagger\|MapSwagger\|AddOpenApi\|MapOpenApi\|SwaggerForOcelot\|AddOpenApiDocument\|UseReDoc" \
  $(find . -name Program.cs -o -name Startup.cs | grep -v /obj/)
```

```
¿Hay AddOpenApi() + MapOpenApi()?            → B    (nativo net9+)
¿Hay AddSwaggerForOcelot?                    → C1   (Ocelot agregador)
¿Hay AddSwaggerGen?
   ├─ ¿cuántos SwaggerDoc(name:...)?
   │     1 o ninguno  → A1
   │     2 o más      → A2
   └─ ¿el proyecto es un gateway?            → C2   (= A1/A2, con caveat de alcance)
¿Hay AddOpenApiDocument (NSwag)?             → D
¿No hay ninguno de los anteriores?           → C3   N/A — PARAR
```

---

## Rama A1 — Swashbuckle clásico, un documento

**Cómo se reconoce:** `AddSwaggerGen()` sin `SwaggerDoc`, o con uno solo. El
documento se llama `v1` por default.

**Lo que hay que averiguar antes de escribir una línea: la ruta real del JSON.**

| Si el código dice | La ruta es |
|---|---|
| `app.UseSwagger();` (sin opciones) | `/swagger/{documentName}/swagger.json` |
| `app.UseSwagger(o => o.RouteTemplate = "webapi/swagger/{documentName}/swagger.yaml")` | esa, tal cual |
| `app.MapSwagger("/openapi/{documentName}.json")` | esa (y coincide con el default de Scalar) |

No se adivina: se lee. **La ruta mal puesta es el error E-SC-01** y se manifiesta
como una UI que carga perfecta y está vacía.

```csharp
// ── QUEDA COMO ESTÁ: la generación del documento
builder.Services.AddSwaggerGen(c => { /* ... sin tocar ... */ });
app.UseSwagger();                          // ← NO borrar: es el que sirve el JSON

// ── SE BORRA: la UI vieja
// app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "v1"));

// ── SE AGREGA: la UI nueva
app.MapScalarApiReference(options => options
    .WithOpenApiRoutePattern("/swagger/{documentName}/swagger.json")
    .WithTitle("<Componente> API"));
```

Con un solo documento no hace falta `AddDocument`: Scalar usa `v1` por default [V].
Si el documento se llama distinto (ej. `BackOffice`), **sí** hace falta declararlo.

---

## Rama A2 — Swashbuckle, varios documentos

**El caso de apiback**, y el que más cuidado necesita.

**Cómo se reconoce:** dos o más `SwaggerDoc(name: "...")`, y el `UseSwaggerUI` viejo
con un `SwaggerEndpoint` por documento — esa lista **es** el mapa que hay que
traducir.

```csharp
// ANTES — la UI vieja declaraba los documentos así:
// app.UseSwaggerUI(c =>
// {
//     c.SwaggerEndpoint(url: "/swagger/BackOffice/swagger.json",      name: "BackOffice");
//     c.SwaggerEndpoint(url: "/swagger/GestionCobranza/swagger.json", name: "GestionCobranza");
// });

// DESPUÉS — el mismo mapa, en el vocabulario de Scalar:
app.MapScalarApiReference(options => options
    .WithOpenApiRoutePattern("/swagger/{documentName}/swagger.json")
    .AddDocument("BackOffice",      "BackOffice",          isDefault: true)
    .AddDocument("GestionCobranza", "Gestión de Cobranza"));
```

La traducción es mecánica: **un `SwaggerEndpoint` → un `AddDocument`**. El
`documentName` es el segmento que varía en la URL (`BackOffice`), **no** el `name`
que se mostraba en el combo — ese va en el segundo parámetro, el título.

**Mayúsculas exactas.** Scalar pasa el nombre al generador tal cual [V]; si en el
código el documento es `BackOffice` y acá se escribe `backoffice`, Swashbuckle puede
devolver 404 y la UI queda vacía (E-SC-01).

**`isDefault` en el primero**, para que la UI abra donde abría SwaggerUI.

**Si el componente sirve el documento en más de una ruta** (apiback tiene además un
`UseSwagger` con `RouteTemplate = "webapi/swagger/{documentName}/swagger.yaml"`):
se apunta a **una sola** — la de JSON, la canónica. Las otras se dejan intactas
porque las consume alguien más.

---

## Rama B — Generador nativo `Microsoft.AspNetCore.OpenApi` (net9+)

**Cómo se reconoce:** `builder.Services.AddOpenApi()` + `app.MapOpenApi()`.

El caso simple, porque las rutas ya coinciden: `MapOpenApi()` sirve en
`/openapi/{documentName}.json`, que es el default de Scalar [V].

```csharp
builder.Services.AddOpenApi(options =>
{
    options.AddDocumentTransformer((document, context, ct) =>
    {
        document.Info.Version = VersionInfo.Current;   // ← version.txt (regla dura)
        return Task.CompletedTask;
    });
});

// ...
app.MapOpenApi();
app.MapScalarApiReference();
```

**Dos cosas que en esta rama son distintas y hay que mirar:**

1. **Los security schemes no se agregan solos.** Tener `AddJwtBearer` en el DI no
   pone nada en el documento [V]. Sin transformer, Scalar no muestra autenticación
   (E-SC-04). Ver `02-api-verificada.md` §6.
2. **Si hay `FallbackPolicy` global cerrado**, tanto `MapOpenApi` como la ruta de
   Scalar quedan detrás del login, y hay una trampa con los assets: **E-SC-02**.

Precedente real y resuelto en la flota: `faast-identidad-y-acceso` (net10,
Scalar 2.0.0). Ver `04-casos-reales.md` §2 — ahí está el código que ya funciona.

---

## Rama C1 — Gateway Ocelot con `SwaggerForOcelot`

**Cómo se reconoce:** `AddSwaggerForOcelot(...)` + `UseSwaggerForOcelotUI(...)`.

Este gateway **sí tiene documentos OpenAPI para mostrar**, pero no son suyos: MMLib
va a buscar el `swagger.json` de cada downstream declarado en `SwaggerEndPoints` del
`ocelot.json`, lo reescribe con las rutas *upstream* del gateway y lo republica.

```jsonc
// ocelot.json de gw-contabilidad — el mapa de documentos
"SwaggerEndPoints": [
  { "Key": "contabilidad", "Config": [ { "Name": "Contabilidad API", "Version": "v1", "Url": "http://localhost:5175/swagger/v1/swagger.json" } ] },
  { "Key": "reversas",     "Config": [ { "Name": "Reversas API",     "Version": "v1", "Url": "http://localhost:5063/swagger/v1/swagger.json" } ] }
]
```

**Cada `Key` es un documento**, servido bajo el `DownstreamSwaggerEndPointBasePath`
que configure el gateway (en gw-contabilidad, `/swagger/docs`).

```csharp
app.MapScalarApiReference(options => options
    .WithOpenApiRoutePattern("/swagger/docs/v1/{documentName}")
    .AddDocument("contabilidad", "Contabilidad API", isDefault: true)
    .AddDocument("reversas",     "Reversas API"));
```

> **La ruta exacta de los documentos agregados hay que confirmarla contra el gateway
> corriendo**, no contra la documentación de MMLib: depende de
> `PathToSwaggerGenerator`, `DownstreamSwaggerEndPointBasePath` y de cómo esa versión
> del paquete compone `{version}/{key}`. [G] Es un `curl` de 30 segundos:
>
> ```bash
> curl -s http://<gw>/swagger/docs | head -40          # el índice que arma MMLib
> curl -s http://<gw>/swagger/docs/v1/contabilidad | head -5
> ```
>
> Se mira **la red del navegador** con la UI vieja abierta: las URLs que pide
> SwaggerForOcelotUI son exactamente las que hay que darle a Scalar.

**Esta rama tiene la decisión abierta D-3.** `UseSwaggerForOcelotUI` no es solo una
UI: es la UI *más* el mecanismo de agregación y reescritura. Reemplazarla por Scalar
significa quedarse con la agregación (`UseSwagger` + los endpoints de MMLib) y
cambiar solo el dibujo — verificable, pero hay que probarlo en un gateway antes de
prometerlo para los cuatro. **Recomendación: no es candidato para la primera ola.**

---

## Rama C2 — Gateway con su propio `AddSwaggerGen`

**Cómo se reconoce:** es un gateway (YARP/Ocelot) **y** tiene `AddSwaggerGen` con sus
propios `SwaggerDoc`.

Técnicamente es A1/A2 y se aplica igual. **El caveat es de alcance, no técnico:** ese
documento describe los controllers **del gateway**, no lo que el gateway proxea. Una
UI hermosa que muestra 3 endpoints propios, sobre un componente que enruta 200.

Caso real: `gw-backoffice` (net8, YARP) tiene
`SwaggerDoc("v1", new OpenApiInfo { Version = "v1", Title = "Gateway Backoffice" })`.

**Antes de aplicar la rama, se pregunta:** ¿alguien usa esa documentación? Si el
documento cubre 3 endpoints residuales, el trabajo correcto puede ser **C3** (no
instalar nada) y no A1. Se anota en el informe y se decide con el lead.

---

## Rama C3 — Gateway sin OpenAPI propio → **N/A**

**Cómo se reconoce:** el `grep` no devuelve nada.

**No se instala Scalar. Se para acá y se reporta "N/A" con la evidencia del grep.**

Un gateway que solo enruta no tiene documento que dibujar. Instalarle Scalar deja una
UI vacía sobre una API que sí existe — peor que no tener documentación, porque miente.

En el inventario caen acá los Ocelot net5 sin swagger (`gw-crm`, `gw-reporting`,
`gw-security` — `asis-repos-legado.md` §3.1, familia D3) y `gw-app` (net8), que no
tiene generador. Si alguno adopta un generador al migrar, vuelve a entrar por A o B.

---

## Rama D — NSwag

**Cómo se reconoce:** `AddOpenApiDocument()` + `UseOpenApi()`.

Soportado, patrón oficial [V]:

```csharp
app.UseOpenApi(options => { options.Path = "/openapi/{documentName}.json"; });
app.MapScalarApiReference();
```

**No hay ningún componente NSwag identificado en la flota hoy.** Queda documentado
por si aparece.

---

## Resumen para el informe

| Rama | Cuántos en la flota (estimado, `asis-repos-legado.md`) | Esfuerzo |
|---|---|---|
| A1 | mayoría de micros y gateways net6/7/8 | 30 min |
| A2 | pocos (apiback y los que tengan API versionada) | 45 min |
| B | 1 confirmado (`faast-identidad-y-acceso`, ya hecho) | 15 min |
| C1 | 1 (`gw-contabilidad`) | a evaluar — D-3 |
| C2 | los gateways con swagger propio (`gw-backoffice`…) | 30 min + decisión de alcance |
| C3 | los Ocelot net5 y `gw-app` | 0 — se reporta y se cierra |

El conteo exacto por repo **no está hecho**: requiere correr el `grep` del Paso 1 en
los 38 backends. Es una tarea de una tarde y debería ser el primer entregable cuando
la skill se apruebe.
