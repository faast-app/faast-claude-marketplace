// ─────────────────────────────────────────────────────────────────────────────
// CaracterizacionOpenApiTests.cs — el snapshot del contrato.
//
// QUÉ AFIRMA: que el documento OpenAPI que la app publica hoy es EXACTAMENTE el
// mismo que publicará después de migrar de TFM, de subir Swashbuckle o de tocar
// cualquier paquete.
//
// REGLA DURA 2: durante una migración este archivo y sus .verified.* NO SE TOCAN.
// Si el test se pone rojo, el veredicto es "el contrato cambió", nunca "hay que
// regenerar el snapshot". Regenerarlo borra la evidencia (T-SNAP-01), y el CI
// lo bloquea.
//
// NORMALIZACIÓN OBLIGATORIA: info.version sale de version.txt y sube en CADA PR
// por regla del repo. Sin quitarlo, el test falla en cada entrega (T-SNAP-02).
//
// Placeholders: <Namespace>, y la lista de documentos del componente.
// ─────────────────────────────────────────────────────────────────────────────

using System.Text.Json;
using System.Text.Json.Nodes;

namespace <Namespace>.Tests.Caracterizacion;

[Trait("categoria", "caracterizacion")]
public class CaracterizacionOpenApiTests : IClassFixture<FaastWebApplicationFactory>
{
    private readonly HttpClient _cliente;

    public CaracterizacionOpenApiTests(FaastWebApplicationFactory factory)
        => _cliente = factory.CreateClient();

    // Un caso por cada documento que la app publica. En micro-api-back son dos
    // JSON y un YAML V2 (que además tiene su propio formato: se caracteriza como texto).
    [Theory]
    [InlineData("BackOffice")]
    [InlineData("GestionCobranza")]
    public async Task Documento_OpenApi_NoCambiaRespectoDeLaLineaBase(string documento)
    {
        var respuesta = await _cliente.GetAsync($"/swagger/{documento}/swagger.json");

        respuesta.StatusCode.ShouldBe(System.Net.HttpStatusCode.OK);

        var json = await respuesta.Content.ReadAsStringAsync();
        var normalizado = Normalizar(json);

        // Verify guarda el .verified.txt la primera vez y compara desde ahí.
        // El .received.txt NO se commitea (T-SNAP-03).
        await Verify(normalizado).UseParameters(documento);
    }

    /// <summary>
    /// Quita lo que cambia legítimamente en cada entrega y ordena las claves, para
    /// que el diff muestre cambios de CONTRATO y no ruido del generador.
    ///
    /// Qué se quita y por qué:
    ///   · info.version   → sale de version.txt, sube en cada PR (T-SNAP-02)
    ///   · servers/host   → depende del ambiente donde corra
    ///   · cualquier fecha u hora generada
    ///
    /// Qué NO se quita, aunque sea tentador: los "format" y los "nullable".
    /// Justamente ahí se ven los cambios de generador que rompen consumidores
    /// (E-SWAG-01 de migrar-dotnet).
    /// </summary>
    private static string Normalizar(string json)
    {
        var raiz = JsonNode.Parse(json)!.AsObject();

        if (raiz["info"] is JsonObject info)
            info.Remove("version");

        raiz.Remove("servers");
        raiz.Remove("host");

        return Ordenar(raiz).ToJsonString(new JsonSerializerOptions { WriteIndented = true });
    }

    private static JsonNode Ordenar(JsonNode nodo)
    {
        switch (nodo)
        {
            case JsonObject obj:
            {
                var ordenado = new JsonObject();
                foreach (var par in obj.OrderBy(p => p.Key, StringComparer.Ordinal))
                    ordenado[par.Key] = par.Value is null ? null : Ordenar(par.Value.DeepClone());
                return ordenado;
            }
            case JsonArray arr:
            {
                // El orden de un array SÍ es parte del contrato en OpenAPI
                // (p. ej. el orden de los parámetros): no se reordena.
                var copia = new JsonArray();
                foreach (var item in arr)
                    copia.Add(item is null ? null : Ordenar(item.DeepClone()));
                return copia;
            }
            default:
                return nodo.DeepClone();
        }
    }
}

// ── Cómo leer un diff de este test ───────────────────────────────────────────
//
// | Cambio                                   | Veredicto                        |
// |------------------------------------------|----------------------------------|
// | Orden de propiedades                     | Ruido. No debería aparecer        |
// | Un "format" que aparece o desaparece     | REVISAR — cambio de generador     |
// | string → object, o un nullable nuevo     | BLOQUEA — rompe consumidores      |
// | Un endpoint que DESAPARECE               | BLOQUEA — un controller dejó de   |
// |                                          | registrarse por convención        |
// | Un "required" nuevo                      | BLOQUEA — rompe a los clientes    |
//
// (Es la misma tabla de migrar-dotnet reference/03-plan-de-pruebas §3.)
