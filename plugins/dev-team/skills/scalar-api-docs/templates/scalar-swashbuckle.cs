// ============================================================================
// PLANTILLA — Ramas A1 / A2: Swashbuckle clásico (1 o N documentos)
// Skill: scalar-api-docs · plugin dev-team, skill scalar-api-docs
//
// REGLA: esto reemplaza SOLO la UI. La generación del documento OpenAPI
//        (AddSwaggerGen + UseSwagger) queda EXACTAMENTE como estaba.
//
// Reemplazá <...> y borrá lo que no aplique. Verificado contra Scalar.AspNetCore
// (ver reference/02-api-verificada.md para qué es [V] y qué es [G]).
// ============================================================================

using Scalar.AspNetCore;   // ← el único using nuevo

// ─────────────────────────────────────────────────────────────────────────────
// 1) VERSIÓN — una sola fuente: version.txt, cacheada. Ver templates/VersionInfo.cs
//    La MISMA propiedad que usa /health. No leer el archivo dos veces.
// ─────────────────────────────────────────────────────────────────────────────
var appVersion = VersionInfo.Current;

// ─────────────────────────────────────────────────────────────────────────────
// 2) GENERACIÓN DEL DOCUMENTO — NO SE TOCA (salvo el Version, punto 3)
// ─────────────────────────────────────────────────────────────────────────────
builder.Services.AddSwaggerGen(c =>
{
    // 3) El Version de CADA documento sale de la misma fuente que /health.
    //    Nunca "1.0.0" a mano: deja la documentación congelada para siempre.
    c.SwaggerDoc("<Documento1>", new OpenApiInfo
    {
        Title   = "<Título 1>",
        Version = appVersion,        // ← version.txt
    });

    // --- Solo rama A2 (varios documentos) ---
    c.SwaggerDoc("<Documento2>", new OpenApiInfo
    {
        Title   = "<Título 2>",
        Version = appVersion,        // ← la MISMA
    });

    // El resto del AddSwaggerGen (security definitions, filtros, XML comments…)
    // queda igual. Si había AddSecurityDefinition/AddSecurityRequirement, DEJALO:
    // es lo que hace que Scalar muestre el botón de autenticación (ver E-SC-04).
});

var app = builder.Build();

// ─────────────────────────────────────────────────────────────────────────────
// 4) EL QUE SIRVE EL JSON — NO BORRAR. Scalar lo consume.
//    Borrar esto junto con UseSwaggerUI es el error (d) de E-SC-01 y además
//    rompe a los consumidores del contrato (gateways, Postman, snapshot-contrato).
// ─────────────────────────────────────────────────────────────────────────────
app.UseSwagger();

// ─────────────────────────────────────────────────────────────────────────────
// 5) LA UI VIEJA — SE BORRA.
//    Dejá el bloque comentado en el PR: el reviewer necesita ver el mapa de
//    documentos del que salieron los AddDocument de abajo.
// ─────────────────────────────────────────────────────────────────────────────
// app.UseSwaggerUI(c =>
// {
//     c.SwaggerEndpoint(url: "/swagger/<Documento1>/swagger.json", name: "<Documento1>");
//     c.SwaggerEndpoint(url: "/swagger/<Documento2>/swagger.json", name: "<Documento2>");
// });

// ─────────────────────────────────────────────────────────────────────────────
// 6) LA UI NUEVA
//
//    WithOpenApiRoutePattern es OBLIGATORIO acá: el default de Scalar es
//    "/openapi/{documentName}.json" y el de Swashbuckle es
//    "/swagger/{documentName}/swagger.json". NO COINCIDEN → E-SC-01.
//    Poné la ruta REAL, leída del RouteTemplate de tu UseSwagger.
//
//    Un SwaggerEndpoint de arriba = un AddDocument acá.
//    El primer parámetro es el documentName (el segmento de la URL), con sus
//    MAYÚSCULAS EXACTAS. El segundo es el título que ve el usuario.
// ─────────────────────────────────────────────────────────────────────────────
app.MapScalarApiReference(options => options
    .WithOpenApiRoutePattern("/swagger/{documentName}/swagger.json")
    .WithTitle("<Componente> API")

    // --- Rama A2: un AddDocument por documento ---
    .AddDocument("<Documento1>", "<Título 1>", isDefault: true)
    .AddDocument("<Documento2>", "<Título 2>")

    // --- Rama A1 con un solo documento llamado "v1": no hace falta AddDocument.
    //     Si se llama distinto, SÍ hace falta declararlo.
);

// ─────────────────────────────────────────────────────────────────────────────
// 7) SI EL COMPONENTE TIENE FallbackPolicy GLOBAL CERRADO — leer E-SC-02.
//    .AllowAnonymous() encadenado NO alcanza: deja los assets .js detrás del
//    login y la UI queda EN BLANCO. Hay que envolver en un grupo:
//
//    var scalarGroup = app.MapGroup("/scalar").AllowAnonymous();
//    scalarGroup.MapScalarApiReference(string.Empty);   // prefijo vacío
//
//    (y MapOpenApi()/UseSwagger necesita su propio permiso aparte)
// ─────────────────────────────────────────────────────────────────────────────

// ─────────────────────────────────────────────────────────────────────────────
// 8) LO QUE NO SE PONE:
//    - credenciales precargadas (auth.Token = "ey...") → visibles en el navegador
//    - tema / ForceDarkMode → decisión de flota, no por componente
//    - CORS → no hace falta si el documento sale del mismo origen (lo normal)
//    - UseStaticFiles() → los assets de Scalar van embebidos en el assembly
// ─────────────────────────────────────────────────────────────────────────────
