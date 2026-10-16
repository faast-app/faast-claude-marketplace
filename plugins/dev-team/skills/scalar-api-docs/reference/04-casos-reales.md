# El árbol aplicado a componentes reales de la flota

Cuatro componentes, cuatro ramas distintas, **con la evidencia leída del repo**
(solo lectura, sin tocar nada). Sirven para validar que el árbol cubre los casos que
existen, y como referencia cuando toque el componente parecido.

**Leyenda:** **[V]** leído del repo, con archivo y línea · **[G]** razonado.

---

## 1. `micro-api-back` (apiback) — **rama A2**, Swashbuckle multi-documento

> Migrándose **en paralelo** en `develop_docker_net10` por el agente de backend. Acá
> solo se documenta lo leído; **este documento no propone tocar ese repo**.

**Evidencia** [V] — `Cloud.Faast.Back/Cloud.Faast.Back/Program.cs`, rama
`develop_docker_net10`:

| Línea | Qué hay |
|---|---|
| 73 | `var appVersion = Cloud.Faast.Back.Common.VersionInfo.Current;` |
| 75 | `builder.Services.AddSwaggerGen(c => ...)` |
| 78 / 92 | `c.SwaggerDoc(name: "BackOffice", ...)` y `c.SwaggerDoc(name: "GestionCobranza", ...)` |
| 81 / 95 | `Version = appVersion` en los dos `OpenApiInfo` |
| 191 | `app.UseSwagger();` |
| 195-198 | `app.UseSwaggerUI(c => { c.SwaggerEndpoint("/swagger/BackOffice/swagger.json", ...); c.SwaggerEndpoint("/swagger/GestionCobranza/swagger.json", ...); })` |
| 217 | un segundo `app.UseSwagger(o => o.RouteTemplate = "webapi/swagger/{documentName}/swagger.yaml")`, OpenAPI 2.0 |

También existe `Cloud.Faast.Back/Cloud.Faast.Back/version.txt` en el repo [V].

**Clasificación: A2.** Dos documentos, servidos en el patrón default de Swashbuckle.

**Configuración que corresponde:**

```csharp
app.UseSwagger();   // intacto

app.MapScalarApiReference(options => options
    .WithOpenApiRoutePattern("/swagger/{documentName}/swagger.json")
    .AddDocument("BackOffice",      "BackOffice",          isDefault: true)
    .AddDocument("GestionCobranza", "Gestión de Cobranza")
    .WithTitle("API Back"));
```

**Tres cosas específicas de este componente:**

1. **El segundo `UseSwagger` (línea 217) no se toca.** Sirve YAML en OpenAPI 2.0 bajo
   `webapi/swagger/...` — es una ruta distinta, con otro formato, y casi seguro tiene
   un consumidor. Scalar apunta **solo** a la de JSON.
2. **Las mayúsculas son exactamente `BackOffice` y `GestionCobranza`** [V]. Ver E-SC-01(c).
3. **La versión ya está unificada**: el comentario de la línea 70 dice *"(version.txt,
   leído una sola vez y cacheado). NUNCA leer version.txt por separado aquí"*, y la
   73 usa `VersionInfo.Current` [V]. **Ese es el patrón que la skill generaliza** —
   antes de ese cambio, este componente era el caso E-SC-05.

**Pendiente de retro-aplicación:** Stage / Puente / Demo (ver pendientes del proyecto).

---

## 2. `faast-identidad-y-acceso` — **rama B**, nativo net10 · **ya resuelto**

**El componente más valioso de esta lista: ya tiene Scalar en producción de su
flujo, y ya se comió los dos errores difíciles.**

**Evidencia** [V] — `src/Identidad.Api/Program.cs`, rama `develop`:

| Línea | Qué hay |
|---|---|
| csproj:19 | `<PackageReference Include="Scalar.AspNetCore" Version="2.0.0" />` |
| 407 | `builder.Services.AddOpenApi(options => ...)` |
| ~409 | `options.AddDocumentTransformer((document, context, ct) => { document.Info.Version = appVersion.Version; ... })` |
| 470 | `app.MapOpenApi().AllowAnonymous();` |
| 497 | `var scalarGroup = app.MapGroup("/scalar").AllowAnonymous(); scalarGroup.MapScalarApiReference(string.Empty);` |

TFM: `net10.0` [V].

**Clasificación: B.** Generador nativo, rutas ya alineadas, nada que configurar en
`WithOpenApiRoutePattern`.

**Lo que este repo aporta a la skill — dos hallazgos que valen más que la teoría:**

1. **La versión** (comentario propio del repo, textual [V]):
   > *"si se dejara como literal escrito a mano (ej. `document.Info.Version = "1.0.0"`),
   > Scalar mostraría para siempre esa cadena fija. `appVersion` es el mismo valor ya
   > calculado arriba (mismo que usa `GET /version` — **un solo punto de lectura de
   > version.txt, nunca dos mecanismos leyendo el mismo archivo por separado**)"*

   Es, palabra por palabra, la regla dura que fijó Plataforma FAAST el 2026-09-22. **Ya estaba
   descubierta acá.** La skill la convierte en regla de flota en vez de dejarla como
   comentario de un repo.

2. **El bug de los assets (E-SC-02).** Encontrado por QA el 2026-07-23, causa raíz
   confirmada decompilando el paquete, fix verificado antes contra un proyecto mínimo
   aislado. Todo el detalle está en `03-catalogo-errores.md` E-SC-02 — es la entrada
   mejor verificada del catálogo y **le va a pasar a cualquier componente con
   `FallbackPolicy` global cerrado**.

**Acción sugerida:** ninguna sobre el código. Sí **alinear la versión del paquete**
(2.0.0 → la pineada por la flota) cuando se defina, y revisar la decisión D-2: hoy
la documentación está solo bajo `IsDevelopment()` [V].

---

## 3. `gw-contabilidad` — **rama C1**, Ocelot + SwaggerForOcelot

**Evidencia** [V] — `GWContabilidad/Program.cs`, rama `release/faast/demo/co`:

| Línea | Qué hay |
|---|---|
| 5-6 | `using Ocelot.DependencyInjection; / Ocelot.Middleware;` |
| 35 | `builder.Services.AddSwaggerGen();` (sin `SwaggerDoc` propio) |
| 44 | `builder.Services.AddSwaggerForOcelot(builder.Configuration, o => { o.GenerateDocsForAggregates = true; });` |
| 128 | `app.UseSwagger();` |
| 129-148 | `app.UseSwaggerForOcelotUI(opt => { ... opt.PathToSwaggerGenerator = "/swagger/docs"; opt.DownstreamSwaggerEndPointBasePath = "/swagger/docs"; })` |

Paquetes [V]: `Ocelot 24.0.1`, `MMLib.SwaggerForOcelot 9.0.0`,
`Swashbuckle.AspNetCore 9.0.4`, `Microsoft.AspNetCore.OpenApi 8.0.22`. TFM `net8.0`.

`ocelot.json` → `SwaggerEndPoints` [V]: dos keys, `contabilidad` (downstream
`:5175/swagger/v1/swagger.json`) y `reversas` (`:5063/swagger/v1/swagger.json`).

**Clasificación: C1.** Tiene documentos para mostrar, pero son **agregados de los
downstream**, no propios. El `AddSwaggerGen()` de la línea 35 es el que MMLib
necesita para funcionar, no genera un documento de negocio.

**Configuración candidata** (la ruta exacta **hay que confirmarla contra el gateway
corriendo**, ver `01-arbol-decision.md` rama C1):

```csharp
app.MapScalarApiReference(options => options
    .WithOpenApiRoutePattern("/swagger/docs/v1/{documentName}")
    .AddDocument("contabilidad", "Contabilidad API", isDefault: true)
    .AddDocument("reversas",     "Reversas API"));
```

**Por qué no es candidato para la primera ola.** `UseSwaggerForOcelotUI` hace dos
cosas: agrega+reescribe los documentos downstream (incluyendo un
`ReConfigureUpstreamSwaggerJson` propio que fuerza `https` en los `servers[*].url`
[V]) **y** los dibuja. Scalar reemplaza solo lo segundo. Es viable, pero **hay que
probar que los documentos agregados siguen sirviéndose sin la UI de MMLib** — y eso
es una prueba de gateway, no una edición de `Program.cs`. **Decisión D-3.**

---

## 4. `gw-backoffice` — **rama C2**, YARP con swagger propio

**Evidencia** [V] — `gwSolution/Program.cs`, rama `release/faast/preprod/co`:

| Línea | Qué hay |
|---|---|
| 7 | `using Yarp.ReverseProxy;` |
| 148-150 | `builder.Services.AddSwaggerGen(c => { c.SwaggerDoc("v1", new OpenApiInfo { Version = "v1", Title = "Gateway Backoffice" }); })` |
| 184-200 | `builder.Services.AddReverseProxy()` con rutas y clusters en código |
| 225 | `app.UseSwagger();` |

TFM `net8.0` [V].

**Clasificación: C2** (= A1 técnicamente, con caveat de alcance).

**Dos cosas que este caso deja ver, y por eso está en la lista:**

1. **`Version = "v1"` hardcodeado** [V]. Es E-SC-05 en su forma más pura: la
   documentación nunca va a decir qué versión del gateway está desplegada. Al aplicar
   la skill, eso pasa a `VersionInfo.Current`. **Y este gateway hoy no tiene
   `version.txt`** [G, a confirmar] — o sea que el paso de la versión única llega
   antes que el de Scalar, y probablemente junto con el `/health` de
   `dockerizar-componente` Paso 4.5.
2. **El documento cubre los controllers del gateway, no lo que YARP proxea.** Antes
   de invertir el trabajo, la pregunta del alcance (rama C2): ¿esa documentación le
   sirve a alguien? Si la respuesta es no, el trabajo correcto es **C3**, no A1.

---

## Lo que estos cuatro casos prueban sobre la skill

| Rama | Cubierta por | ¿El árbol la resolvió? |
|---|---|---|
| A2 (Swashbuckle multi-doc) | apiback | Sí — traducción `SwaggerEndpoint` → `AddDocument` |
| B (nativo net9+) | identidad | Sí — y el repo ya lo había hecho así |
| C1 (Ocelot agregador) | gw-contabilidad | Sí, **con decisión abierta D-3** |
| C2 (gateway con doc propio) | gw-backoffice | Sí, con caveat de alcance |
| C3 (gateway sin OpenAPI) | gw-crm/reporting/security, gw-app | Sí — salida "N/A" explícita |
| A1 (Swashbuckle 1 doc) | el resto de la flota | Sí — es el caso simple |
| D (NSwag) | ninguno hoy | Documentado por si aparece |

**Lo que todavía no está probado y hay que confirmar en el piloto:**

- E-SC-08 (subpath / detrás del vhost de Apache) — [G], ningún caso real verificado.
- La ruta real de los documentos agregados de MMLib en C1 — hace falta el gateway
  corriendo.
- El conteo exacto de cuántos de los 38 backends caen en cada rama — requiere correr
  el `grep` del Paso 1 en todos.
