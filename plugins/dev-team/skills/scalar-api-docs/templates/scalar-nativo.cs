// ============================================================================
// PLANTILLA — Rama B: generador nativo Microsoft.AspNetCore.OpenApi (net9+)
// Skill: scalar-api-docs
//
// El caso simple: MapOpenApi() sirve en /openapi/{documentName}.json, que es
// exactamente el default de Scalar. No hace falta WithOpenApiRoutePattern.
//
// Precedente real en la flota: faast-identidad-y-acceso (net10, Scalar 2.0.0).
// ============================================================================

using Scalar.AspNetCore;

var appVersion = VersionInfo.Current;   // version.txt, la MISMA de /health

// ─────────────────────────────────────────────────────────────────────────────
// 1) GENERACIÓN DEL DOCUMENTO
//
//    info.version dinámico: si se deja como literal (document.Info.Version = "1.0.0"),
//    Scalar muestra esa cadena fija para siempre. appVersion se captura por closure,
//    no hace falta resolverlo del DI dentro del transformer.
// ─────────────────────────────────────────────────────────────────────────────
builder.Services.AddOpenApi(options =>
{
    options.AddDocumentTransformer((document, context, cancellationToken) =>
    {
        document.Info.Version = appVersion;
        return Task.CompletedTask;
    });

    // ── SEGURIDAD: con el generador NATIVO, tener AddJwtBearer en el DI NO
    //    agrega nada al documento. Sin esto, Scalar no muestra ningún botón de
    //    autenticación y "Try it" siempre da 401 (E-SC-04).
    //    Solo si el componente usa JWT Bearer:
    options.AddDocumentTransformer((document, _, _) =>
    {
        var securityScheme = new OpenApiSecurityScheme
        {
            Type   = SecuritySchemeType.Http,
            In     = ParameterLocation.Header,
            Scheme = "bearer"
        };
        document.Components ??= new OpenApiComponents();
        document.Components.SecuritySchemes.Add(JwtBearerDefaults.AuthenticationScheme, securityScheme);
        return Task.CompletedTask;
    });
});

var app = builder.Build();

// ─────────────────────────────────────────────────────────────────────────────
// 2) LA UI
//
//    ── CASO SIMPLE (sin política de auth global cerrada):
// ─────────────────────────────────────────────────────────────────────────────
app.MapOpenApi();
app.MapScalarApiReference();

// ─────────────────────────────────────────────────────────────────────────────
//    ── CASO CON FallbackPolicy GLOBAL CERRADO (RequireAuthenticatedUser):
//
//    Los dos endpoints necesitan permiso, y el de Scalar NO se resuelve con
//    .AllowAnonymous() encadenado: MapScalarApiReference registra DOS endpoints
//    (el HTML y los assets .js) pero solo DEVUELVE el builder del primero, así
//    que los .js quedan detrás del login y la UI carga EN BLANCO con
//    "getBasePath is not defined" en consola. Ver E-SC-02.
//
//    El fix es envolver en un grupo propio ANTES de mapear, con prefijo vacío
//    para no terminar en /scalar/scalar/...:
// ─────────────────────────────────────────────────────────────────────────────
// app.MapOpenApi().AllowAnonymous();
//
// var scalarGroup = app.MapGroup("/scalar").AllowAnonymous();
// scalarGroup.MapScalarApiReference(string.Empty);

// ─────────────────────────────────────────────────────────────────────────────
// 3) VARIOS DOCUMENTOS (API versionada) — un AddOpenApi por versión y un
//    AddDocument por versión. Las rutas ya coinciden, no hace falta patrón.
//
//    foreach (var version in new[] { "v1", "v2" })
//        builder.Services.AddOpenApi(version, o => { /* transformers */ });
//
//    app.MapScalarApiReference(options => options
//        .AddDocument("v1", "API v1", isDefault: true)
//        .AddDocument("v2", "API v2"));
// ─────────────────────────────────────────────────────────────────────────────

// ─────────────────────────────────────────────────────────────────────────────
// 4) EXPOSICIÓN POR AMBIENTE — decisión abierta D-2.
//    Varios componentes de la flota hoy envuelven todo esto en
//    if (app.Environment.IsDevelopment()) { ... }. Mantené lo que el componente
//    ya hacía y registralo en el checklist; no lo cambies en este PR.
// ─────────────────────────────────────────────────────────────────────────────
