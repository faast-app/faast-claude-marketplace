# API real de `Scalar.AspNetCore` — verificado contra la fuente

**Fecha de verificación:** 2026-09-22.
**Leyenda:** **[V]** verificado contra la fuente que se cita · **[G]** conocimiento
general, sin verificar contra la fuente.

Fuentes consultadas:

| Fuente | Qué se sacó de ahí |
|---|---|
| `nuget.org/packages/Scalar.AspNetCore` | Versión, licencia, dependencias, TFMs |
| `github.com/scalar/scalar` → `integrations/dotnet/aspnetcore/src/.../Extensions/ScalarEndpointRouteBuilderExtensions.cs` | Overloads de `MapScalarApiReference`, ruta default, redirect |
| `github.com/scalar/scalar` → `integrations/dotnet/shared/src/Scalar.Shared/Extensions/ScalarOptionsExtensions.cs` | Firma de `AddDocument`/`AddDocuments`, auth, `WithOpenApiRoutePattern` |
| `github.com/scalar/scalar` → `.../Extensions/ScalarOptionsFluentExtensions.cs` | `ForceDarkMode`, `EnableDarkMode`, layout |
| `github.com/scalar/scalar` → `.../Options/ScalarOptions.cs` | Default de `OpenApiRoutePattern` |
| `github.com/scalar/scalar` → `documentation/integrations/aspnetcore/integration.md` y `integrations/dotnet/aspnetcore/docs/{authentication,multiple-openapi-documents}.md` | Ejemplos oficiales |
| `scalar.com/scalar/scalar-api-references/net-integration` | Doc publicada (redirige desde `guides.scalar.com`) |

---

## 1. El paquete

| Dato | Valor | |
|---|---|---|
| Id | `Scalar.AspNetCore` | [V] |
| Versión al 2026-09-22 | **2.17.8** (publicada 2026-09-22; 2.17.7 el 21, 2.17.6 el 19) | [V] nuget.org |
| Licencia | **MIT** | [V] nuget.org |
| Dependencias | **ninguna** | [V] nuget.org |
| TFMs | **`net8.0;net9.0;net10.0`** en el mismo paquete | [V] `Scalar.AspNetCore.csproj` |

**Sobre net8/net9/net10: es el mismo paquete, no hay variantes.** El `.csproj` del
paquete declara los tres TFMs y nuget lo publica como "compatible con .NET 8.0 o
superior" [V]. La doc agrega que Scalar sigue la política oficial de soporte de
Microsoft [V] — o sea que cuando net8/net9 mueran (2026-11-10), el soporte del
paquete para esos TFMs sigue esa misma política.

**Implicancia para la flota:** un componente que todavía está en net8 puede adoptar
Scalar **antes** de migrar a net10, y el `PackageReference` no cambia al migrar. Eso
permite desacoplar los dos cambios si conviene.

> **Cadencia de release alta.** Hubo 4 versiones en 6 días [V]. **Se pinea la
> versión** en el `.csproj` y se anota en el informe; no se deja flotar. Precedente
> en la flota: `faast-identidad-y-acceso` está pineado en `2.0.0` [V].

```xml
<PackageReference Include="Scalar.AspNetCore" Version="2.17.8" />
```

---

## 2. Registro — el patrón simple (rama B, nativo net9+)

Ejemplo oficial, textual [V] (`documentation/integrations/aspnetcore/integration.md`):

```csharp
builder.Services.AddOpenApi();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.MapScalarApiReference();
}
```

Con el generador nativo **no hay que configurar la ruta**: `MapOpenApi()` sirve en
`/openapi/{documentName}.json`, que es exactamente el default de Scalar [V]. Por eso
la rama B es de dos líneas y la rama A necesita una tercera.

`MapScalarApiReference` es extensión de **`IEndpointRouteBuilder`** [V]
(`ScalarEndpointRouteBuilderExtensions.cs`), así que funciona tanto sobre
`WebApplication` como dentro de `UseEndpoints(endpoints => ...)` en apps con
`Startup.cs` clásico [G — la extensión aplica por tipo; no se probó en un Startup
real de la flota].

Devuelve `IEndpointConventionBuilder`, así que acepta `.AllowAnonymous()`,
`.RequireAuthorization()`, etc. [V] — **con una trampa importante: ver E-SC-02.**

### Ruta y redirect

| Dato | Valor | |
|---|---|---|
| Prefijo default | `/scalar` | [V] `DefaultEndpointPrefix = "/scalar"` |
| Ruta interna | `/{documentName?}` sobre ese prefijo → `/scalar/v1` funciona | [V] |
| Ruta custom | `app.MapScalarApiReference("/api-docs")` | [V] |
| `{documentName}` en el prefijo | **lanza `ArgumentException`** | [V] |
| Sin barra final | **redirige a `/scalar/`** (`ShouldRedirectToTrailingSlash`) | [V] |

El redirect es la causa de E-SC-03: `curl /scalar` sin `-L` devuelve 3xx, no 200.

---

## 3. Múltiples documentos con Swashbuckle (rama A2) — el caso de apiback

**Firma real [V]** (`ScalarOptionsExtensions.cs` línea 94):

```csharp
public static TOptions AddDocument<TOptions>(
    this TOptions options,
    string documentName,
    string? title = null,
    string? routePattern = null,
    bool isDefault = false,
    string? agentKey = null) where TOptions : ScalarOptions
```

Y las dos sobrecargas de `AddDocuments` [V] (líneas 110 y 126):

```csharp
public static TOptions AddDocuments<TOptions>(this TOptions options, params IEnumerable<string> documentNames)
public static TOptions AddDocuments<TOptions>(this TOptions options, params IEnumerable<ScalarDocument> documents)
```

**Lo que hay que entender, y es el corazón de esta skill:** `AddDocument` **no
genera nada**. Solo le dice a la UI *"existe un documento que se llama X, su título
es Y, y lo vas a encontrar en la URL Z"*. El documento lo sigue produciendo
Swashbuckle exactamente como antes.

**El default no coincide con Swashbuckle.** `ScalarOptions.OpenApiRoutePattern` vale
`"/openapi/{documentName}.json"` [V] (`ScalarOptions.cs` línea 31), mientras que
Swashbuckle sirve en `/swagger/{documentName}/swagger.json`. Hay que decírselo:

```csharp
public static TOptions WithOpenApiRoutePattern<TOptions>(this TOptions options, string pattern)  // [V] línea 644
```

Dos formas, las dos válidas [V]:

```csharp
// (a) patrón global + documentos por nombre  ← recomendado para la flota
app.MapScalarApiReference(options => options
    .WithOpenApiRoutePattern("/swagger/{documentName}/swagger.json")
    .AddDocument("BackOffice", "BackOffice", isDefault: true)
    .AddDocument("GestionCobranza", "Gestión de Cobranza"));

// (b) ruta explícita por documento (si cada uno se sirve distinto)
app.MapScalarApiReference(options => options
    .AddDocument("v1", "Production API", "api/v1/openapi.json")
    .AddDocument("v2-beta", "Beta API", "api/v2-beta/openapi.json", isDefault: true));
```

Se prefiere **(a)**: una sola ruta que declarar, y si el `RouteTemplate` de
`UseSwagger` cambia alguna vez, se toca en un solo lugar.

- `isDefault` elige cuál se abre primero; si ninguno lo declara, gana el primero [V].
- `routePattern` acepta **URLs externas absolutas** (`https://api.example.com/...`) [V]
  — útil para un agregador, pero levanta CORS (ver E-SC-06).
- Los nombres se pasan al generador **respetando mayúsculas** [V]. En apiback los
  documentos se llaman `BackOffice` y `GestionCobranza`, con esas mayúsculas exactas.
- `/scalar/{documentName}` en la URL **pisa** lo declarado en `AddDocument` [V].

---

## 4. `Info.Version` dinámico con el generador nativo

Para la rama B, el `Info.Version` se setea con un document transformer [V]
(patrón oficial en `multiple-openapi-documents.md`, y uso real en
`faast-identidad-y-acceso`):

```csharp
builder.Services.AddOpenApi(options =>
{
    options.AddDocumentTransformer((document, context, cancellationToken) =>
    {
        document.Info.Version = VersionInfo.Current;   // ← version.txt, la MISMA de /health
        return Task.CompletedTask;
    });
});
```

En la rama A (Swashbuckle) es más directo: el `Version` del `OpenApiInfo` de cada
`SwaggerDoc(...)`. Ver `templates/scalar-swashbuckle.cs`.

---

## 5. Tema, dark mode y layout

Todas extensiones fluidas sobre `ScalarOptions`, verificadas en
`ScalarOptionsFluentExtensions.cs` [V]:

| Método | Efecto | |
|---|---|---|
| `ForceDarkMode()` | Fuerza oscuro, sin toggle para el usuario | [V] línea 214 |
| `ForceLightMode()` | Fuerza claro | [V] línea 204 |
| `EnableDarkMode()` | Arranca en oscuro, el usuario puede cambiar | [V] línea 163 |
| `HideDarkModeToggle()` | Esconde el selector | [V] línea 43 |
| `WithTheme(ScalarTheme theme)` | Paleta | [V] línea 278 |
| `WithClassicLayout()` | Layout clásico (el default es Modern) | [V] línea 194 |
| `WithTitle(string)` | Título de la página | [V] |
| `HideSearch()`, `HideModels()` | Esconden secciones | [V] |
| `WithFavicon(string)` | Favicon propio | [V] |

**`ScalarTheme` — valores reales** [V] (`Enums/ScalarTheme.cs`): `None`, `Alternate`,
`Default`, `Moon`, `Purple`, `Solarized`, `BluePlanet`, `Saturn`, `Kepler`, `Mars`,
`DeepSpace`, `Laserwave`.

> **Recomendación para la flota:** **no fijar tema ni forzar dark mode.** El default
> ya trae toggle y respeta la preferencia del usuario; fijarlo es una decisión
> estética que después hay que mantener en 38 repos. Si Plataforma quiere identidad
> visual FaaST, es una decisión aparte y se aplica igual en todos (`WithTitle` +
> `WithFavicon` alcanzan para eso). [G — criterio de arquitectura, no de la doc]

Nota: **`WithDarkMode(bool)`, `WithDarkModeToggle(bool)` y `WithLayout(...)` están
marcados `[Obsolete]`** en el código actual, con el reemplazo indicado en el propio
mensaje [V]. No usarlos en código nuevo.

---

## 6. Autenticación en la UI (Bearer)

**Lo primero, y es lo que más confunde:** Scalar **no inventa** esquemas de
seguridad. Lee los que estén **en el documento OpenAPI**. Si el documento no declara
ninguno, la UI no muestra ningún botón de autenticación — textual de la doc: *"If the
OpenAPI document does not specify any security schemes, Scalar will not display any
authentication options"* [V] (`docs/authentication.md`).

Eso es E-SC-04, y **el fix no está en Scalar sino en el generador**:

- **Swashbuckle (rama A):** el `AddSecurityDefinition` / `AddSecurityRequirement` que
  ya debería existir en el `AddSwaggerGen`. Si SwaggerUI mostraba el botón
  "Authorize", el esquema ya está en el documento y Scalar lo va a ver también [G].
- **Nativo (rama B):** hay que agregarlo con un document transformer — el generador
  nativo **no** lo agrega solo por tener `AddJwtBearer` en el DI [V]. Ejemplo oficial:

```csharp
options.AddDocumentTransformer((document, _, _) =>
{
    var securityScheme = new OpenApiSecurityScheme
    {
        Type = SecuritySchemeType.Http,
        In = ParameterLocation.Header,
        Scheme = "bearer"
    };
    document.Components ??= new OpenApiComponents();
    document.Components.SecuritySchemes.Add(JwtBearerDefaults.AuthenticationScheme, securityScheme);
    return Task.CompletedTask;
});
```

Con el esquema en el documento, la UI ya deja pegar el token y usar "Try it" — **eso
solo alcanza**. Lo de abajo es opcional y **no se usa en FaaST fuera de local**:

```csharp
app.MapScalarApiReference(options => options
    .AddPreferredSecuritySchemes("BearerAuth")          // [V] línea 418
    .AddHttpAuthentication("BearerAuth", auth =>        // [V] línea 605
    {
        auth.Token = "ey...";                           // ⚠ queda visible en el navegador
    })
    .EnablePersistentAuthentication());                 // [V] línea 153 — guarda en localStorage
```

La doc lo marca como *CAUTION: "Pre-filled authentication details are visible in the
browser and should **never** be used in production environments"* [V], y marca
`EnablePersistentAuthentication` como riesgo de localStorage [V]. De ahí sale la
Regla 5 de la skill.

También existen, verificados [V]: `AddApiKeyAuthentication`,
`AddOAuth2Authentication`, `AddClientCredentialsFlow`, `AddAuthorizationCodeFlow`
(con `Pkce.Sha256`), `AddImplicitFlow`, `AddPasswordFlow`, `AddOAuth2Flows`,
`AddDefaultScopes`. Ninguno hace falta para el JWT Bearer de FaaST.

---

## 7. Middleware: ¿hace falta algo más?

| ¿Hace falta? | Respuesta | |
|---|---|---|
| **Routing** | Sí, pero ya está. `MapScalarApiReference` es un endpoint; en minimal hosting (`WebApplication`) el routing se registra solo. En apps con `Startup.cs`, va dentro de `UseEndpoints` | [V] la extensión es de `IEndpointRouteBuilder` · [G] lo del Startup |
| **Static files** | **No.** Los assets JS van **embebidos en el assembly** (`EmbeddedResource StaticAssets/*`) y los sirve el propio endpoint. No hace falta `UseStaticFiles()` | [V] `Scalar.AspNetCore.csproj` + `MapStaticAssetsEndpoint` |
| **CORS** | **No**, en el caso normal: la UI y el documento salen del mismo origen. **Sí** si `routePattern` apunta a un host distinto | [V] la doc contempla URLs externas · [G] la consecuencia CORS |
| **Auth** | Depende de la política del componente. Con `FallbackPolicy` global cerrado, hay que marcar la ruta — y hay una trampa: **E-SC-02** | [V] caso real de `faast-identidad-y-acceso` |
| **HTTPS redirect / compresión** | Sin interacción conocida | [G] |
| **Fuentes** | Se cargan de un CDN por default; `DisableDefaultFonts()` lo evita | [V] — relevante si el ambiente no tiene salida a internet |

Ese último punto merece atención en FaaST: si un ambiente cerrado no tiene salida a
internet, la UI funciona igual pero con la tipografía de fallback [G]. El bundle JS
sí es local (embebido), así que la UI **no** depende del CDN para funcionar [V].
