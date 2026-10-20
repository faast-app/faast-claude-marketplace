// ============================================================================
// PLANTILLA — Helper de versión única
// Skill: scalar-api-docs · también aplica a dockerizar-componente Paso 4.5
//
// REGLA DURA (Plataforma FAAST, 2026-09-22):
//   TODO lo que muestre la versión del componente — /health, el Info.Version del
//   documento OpenAPI que dibuja Scalar, y cualquier otra vista — lee del MISMO
//   version.txt del repo, en runtime, a través de esta propiedad.
//
//   NUNCA un string hardcodeado.
//   NUNCA AssemblyInformationalVersion / ARG VERSION como fuente de la app.
//   NUNCA dos File.ReadAllText separados sobre el mismo archivo.
//
// El ARG VERSION del Dockerfile, si existe, sirve SOLO para taguear la imagen en
// el registro/CI. No es la fuente que lee la app.
//
// Precedente real: Cloud.Faast.Back.Common.VersionInfo.Current (apiback).
// ============================================================================

namespace <Namespace>.Common;

/// <summary>
/// Versión interna del componente. Fuente única: el archivo <c>version.txt</c>
/// del repo, copiado al output de publish. Se lee una sola vez y se cachea.
/// </summary>
public static class VersionInfo
{
    // Lazy: una sola lectura de disco por proceso, thread-safe, y sin costo si
    // nadie pregunta. Un File.ReadAllText en cada request al documento OpenAPI
    // o a /health es I/O de disco en el camino caliente, sin ninguna ganancia:
    // el archivo no cambia mientras el proceso vive.
    private static readonly Lazy<string> _current = new(ReadVersionFile);

    /// <summary>
    /// La versión del componente, ej. <c>"2.0.34"</c>.
    /// Devuelve <c>"unknown"</c> si el archivo no está o no se puede leer.
    /// </summary>
    public static string Current => _current.Value;

    private static string ReadVersionFile()
    {
        try
        {
            // AppContext.BaseDirectory, NO Directory.GetCurrentDirectory():
            // dentro del contenedor el working directory puede no ser el de la
            // app, y la lectura falla de una forma difícil de diagnosticar.
            var path = Path.Combine(AppContext.BaseDirectory, "version.txt");
            return File.Exists(path)
                ? File.ReadAllText(path).Trim()
                : "unknown";
        }
        catch
        {
            // Que no se pueda leer la versión NO puede tumbar el arranque ni
            // devolver 500 en /health: el health es justamente lo que se
            // consulta cuando algo anda mal.
            return "unknown";
        }
    }
}

// ============================================================================
// PARA QUE version.txt LLEGUE AL OUTPUT (en el .csproj del proyecto de entrada):
//
//   <ItemGroup>
//     <None Update="version.txt">
//       <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
//     </None>
//   </ItemGroup>
//
// Verificación: docker exec <contenedor> cat /app/version.txt
// Si no está, Current devuelve "unknown" y el checklist §3 falla.
// ============================================================================

// ============================================================================
// USO — los tres lugares leen la MISMA propiedad:
//
//   var appVersion = VersionInfo.Current;
//
//   // /health
//   new { component = "<repo>", version = appVersion, status = "Healthy", ... }
//
//   // Swashbuckle
//   c.SwaggerDoc("<Doc>", new OpenApiInfo { Title = "...", Version = appVersion });
//
//   // Generador nativo
//   options.AddDocumentTransformer((document, _, _) =>
//   {
//       document.Info.Version = appVersion;
//       return Task.CompletedTask;
//   });
// ============================================================================
