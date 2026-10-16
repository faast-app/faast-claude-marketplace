// ─────────────────────────────────────────────────────────────────────────────
// ContratoQaTests.cs — familia (d): contrato contra un ambiente REAL.
//
// ES EL EQUIVALENTE AUTOMATIZADO de comparar-respuestas.sh de migrar-dotnet.
// Sirve para lo que NO se puede reproducir localmente: stored procedures, datos
// reales, integraciones de terceros. Y para tomar la LÍNEA BASE antes de migrar.
//
// ┌─────────────────────────────────────────────────────────────────────────┐
// │ REGLAS DURAS — si una se rompe, se para y se avisa                      │
// │                                                                         │
// │ 1. SOLO LECTURA. Solo GET. Esta clase no expone ningún otro verbo.      │
// │ 2. SOLO QA. Nunca Puente, Demo, preprod ni producción de cliente,      │
// │    aunque sea un GET.                                                   │
// │ 3. FUERA DEL CI por defecto. Trait categoria=contrato, excluido del     │
// │    filtro del pipeline. Un test que depende de un ambiente ajeno        │
// │    vuelve el CI intermitente y deja a todos ciegos (T-FLAKE-02).        │
// │ 4. SIN URL POR DEFECTO. Sin variable de entorno, los tests se SALTEAN.  │
// │    Nunca fallan por no estar configurados, nunca corren por accidente   │
// │    contra lo que hubiera quedado en el entorno (T-SEC-02).              │
// │ 5. SIN SECRETOS EN EL REPO. URL y token salen del entorno (T-SEC-01).   │
// └─────────────────────────────────────────────────────────────────────────┘
//
// Uso:
//   export QA_BASE_URL="http://<host de QA>"     # solo QA
//   export QA_TOKEN="..."                        # token de lectura
//   dotnet test --filter "categoria=contrato"
//
// Placeholders: <Namespace>
// ─────────────────────────────────────────────────────────────────────────────

namespace <Namespace>.Tests.Contrato;

[Trait("categoria", "contrato")]
public class ContratoQaTests
{
    private static string? BaseUrl => Environment.GetEnvironmentVariable("QA_BASE_URL");
    private static string? Token => Environment.GetEnvironmentVariable("QA_TOKEN");

    /// <summary>
    /// Guardarraíl de la regla 2. Si la URL apunta a algo que no es QA, el test
    /// FALLA — no se saltea. Es la diferencia entre "no está configurado" y
    /// "está configurado mal", y la segunda tiene que doler.
    /// </summary>
    private static void ExigirAmbientePermitido(string url)
    {
        string[] prohibidos = { "puente", "demo", "preprod", "prod", "prd", "cliente" };
        foreach (var p in prohibidos)
            if (url.Contains(p, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException(
                    $"QA_BASE_URL apunta a '{p}'. Esta suite corre SOLO contra QA (regla dura 5 de la skill).");
    }

    private static HttpClient? CrearCliente()
    {
        if (string.IsNullOrWhiteSpace(BaseUrl)) return null;   // → Skip
        ExigirAmbientePermitido(BaseUrl!);

        var cliente = new HttpClient { BaseAddress = new Uri(BaseUrl!), Timeout = TimeSpan.FromSeconds(30) };
        if (!string.IsNullOrWhiteSpace(Token))
            cliente.DefaultRequestHeaders.Authorization = new("Bearer", Token);
        return cliente;
    }

    public static TheoryData<string, string> EndpointsDeSoloLectura => new()
    {
        { "openapi-backoffice",   "/swagger/BackOffice/swagger.json" },
        { "openapi-cobranza",     "/swagger/GestionCobranza/swagger.json" },
        { "core-parametros",      "/api/v2/core/obtener-parametros" },
        // Agregar SOLO GET, y solo endpoints sin efecto.
    };

    [SkippableTheory]
    [MemberData(nameof(EndpointsDeSoloLectura))]
    public async Task Endpoint_EnQa_RespondeIgualQueLaLineaBase(string caso, string ruta)
    {
        using var cliente = CrearCliente();
        Skip.If(cliente is null,
            "QA_BASE_URL no está definida: la suite de contrato no corre. Es lo correcto en CI.");

        var respuesta = await cliente!.GetAsync(ruta);
        var cuerpo = await respuesta.Content.ReadAsStringAsync();

        await Verify(new { status = (int)respuesta.StatusCode, cuerpo })
              .UseParameters(caso)
              .UseDirectory("LineaBaseQa");
    }

    // ── Cómo se usa en una migración ─────────────────────────────────────────
    //
    //  ANTES de tocar el .csproj:
    //      dotnet test --filter "categoria=contrato"     → genera LineaBaseQa/*.verified.*
    //      git add tests/**/LineaBaseQa && git commit     → la línea base queda versionada
    //
    //  DESPUÉS de migrar y desplegar en QA:
    //      dotnet test --filter "categoria=contrato"     → compara contra la línea base
    //
    //  Los .verified.* de LineaBaseQa NO se regeneran durante la migración
    //  (regla dura 2 / T-SNAP-01). Si cambian, cambió el contrato.
    //
    // NOTA: `SkippableTheory`/`Skip.If` vienen de Xunit.SkippableFact. Si no se
    // quiere esa dependencia, se reemplaza por un `if (cliente is null) return;`
    // — pero entonces el test aparece como "pasó" sin haber corrido, que es
    // justo lo que T-CI-01 enseña a no hacer. Recomendado: el paquete.
}
