// ============================================================================
// PLANTILLA — Rama C1: gateway Ocelot con MMLib.SwaggerForOcelot
// Skill: scalar-api-docs
//
// ⚠ DECISIÓN ABIERTA D-3 — NO aplicar sin aprobación del responsable de plataforma (preguntar al usuario).
//   UseSwaggerForOcelotUI hace DOS cosas: (1) agrega y reescribe los documentos
//   de los downstream, (2) los dibuja. Scalar reemplaza solo (2). Que (1) siga
//   funcionando sin la UI de MMLib hay que PROBARLO contra el gateway corriendo.
//
// Caso de referencia: gw-contabilidad (net8, Ocelot 24.0.1, MMLib 9.0.0).
// ============================================================================

using Scalar.AspNetCore;

// ─────────────────────────────────────────────────────────────────────────────
// 1) AGREGACIÓN — NO SE TOCA NADA DE ESTO
//    AddSwaggerGen() acá no genera un documento de negocio: lo necesita MMLib.
// ─────────────────────────────────────────────────────────────────────────────
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddOcelot();
builder.Services.AddSwaggerForOcelot(builder.Configuration, o =>
{
    o.GenerateDocsForAggregates = true;
});

var app = builder.Build();

app.UseSwagger();   // ← NO BORRAR: parte del mecanismo de agregación

// ─────────────────────────────────────────────────────────────────────────────
// 2) ANTES DE ESCRIBIR LA CONFIG DE SCALAR: AVERIGUAR LAS RUTAS REALES
//
//    NO se deducen de la documentación de MMLib. Dependen de
//    PathToSwaggerGenerator, DownstreamSwaggerEndPointBasePath y de cómo esa
//    versión del paquete compone {version}/{key}.
//
//    Con el gateway corriendo:
//      curl -s http://<gw>/swagger/docs | head -40
//      curl -s http://<gw>/swagger/docs/v1/<key> | head -5
//
//    O más rápido: abrir la UI vieja y mirar la pestaña Network. Las URLs que
//    pide SwaggerForOcelotUI son EXACTAMENTE las que hay que darle a Scalar.
//
//    Los <key> salen del ocelot.json → SwaggerEndPoints[].Key
//    (en gw-contabilidad: "contabilidad" y "reversas").
// ─────────────────────────────────────────────────────────────────────────────

// ─── OPCIÓN A (D-3 = reemplazar): se borra UseSwaggerForOcelotUI y se pone Scalar
//
// app.MapScalarApiReference(options => options
//     .WithOpenApiRoutePattern("/swagger/docs/v1/{documentName}")   // ← CONFIRMAR
//     .WithTitle("Gateway <Nombre>")
//     .AddDocument("<key1>", "<Nombre API 1>", isDefault: true)
//     .AddDocument("<key2>", "<Nombre API 2>"));
//
//   ⚠ Si la UI de MMLib hacía reescritura de los documentos (gw-contabilidad
//     fuerza https en servers[*].url con ReConfigureUpstreamSwaggerJson), hay que
//     verificar que esa reescritura sigue ocurriendo del lado del servidor y no
//     dependía de la UI. Si dependía, Scalar va a mostrar servers en http y el
//     "Try it" va a pegar al lugar equivocado.

// ─── OPCIÓN B (D-3 = convivir): se deja la UI de MMLib y Scalar se suma aparte,
//     en /scalar, apuntando a los mismos documentos agregados.
//     Es la opción de menor riesgo para una primera ola: no se pierde nada y se
//     puede comparar lado a lado antes de decidir.
//
// app.UseSwaggerForOcelotUI(opt => { /* ... tal cual estaba ... */ });
// app.MapScalarApiReference(options => options
//     .WithOpenApiRoutePattern("/swagger/docs/v1/{documentName}")
//     .AddDocument("<key1>", "<Nombre API 1>", isDefault: true));
//
//   Ojo con E-SC-07 (conflicto de rutas): la UI de MMLib vive en su propio
//   prefijo; Scalar en /scalar. No solaparlos.

await app.UseOcelot();
