// ─────────────────────────────────────────────────────────────────────────────
// CaracterizacionRespuestasTests.cs — golden-file de las respuestas.
//
// QUÉ AFIRMA: que la FORMA de la respuesta de cada endpoint consumido no cambia.
// Casing de las propiedades, nulos emitidos u omitidos, enums como número o como
// string, formato de fechas y de decimales, y el sobre de respuesta del componente.
//
// ES EL TEST QUE ATRAPA E-JSON-01: el front deja de encontrar un campo porque MVC
// cambió de serializador, sin que nadie haya tocado un DTO.
//
// FUNCIONA EN DOS MODOS:
//   A) contra el TestServer, con los repositorios doblados → determinista, en CI
//   B) contra el ambiente QA (familia d) → ver ContratoQaTests.cs
// Este archivo es el modo A.
//
// Placeholders: <Namespace>, <IRepositorio>
// ─────────────────────────────────────────────────────────────────────────────

using System.Net;
using System.Text.Json;
using System.Text.Json.Nodes;
using Microsoft.Extensions.DependencyInjection;
using NSubstitute;

namespace <Namespace>.Tests.Caracterizacion;

[Trait("categoria", "caracterizacion")]
public class CaracterizacionRespuestasTests : IClassFixture<FaastWebApplicationFactory>
{
    private readonly FaastWebApplicationFactory _factory;

    public CaracterizacionRespuestasTests(FaastWebApplicationFactory factory)
        => _factory = factory;

    /// <summary>
    /// Endpoints que entran en la caracterización. NO son todos los del componente:
    /// son los que alguien consume de verdad, según el inventario
    /// (asis-qa-total-apis-micros.md §4.2) y los logs del ambiente.
    /// La lista la valida QA antes de cerrarse.
    /// </summary>
    public static TheoryData<string, string> EndpointsDelContrato => new()
    {
        // { nombre del caso, ruta }
        { "cartera-listar",     "/api/v2/interface/listar-documentos-cartera/11111111-1/A/BO" },
        { "cartera-protestos",  "/api/v2/interface/listar-protestos/11111111-1" },
        { "core-parametros",    "/api/v2/core/obtener-parametros" },
    };

    [Theory]
    [MemberData(nameof(EndpointsDelContrato))]
    public async Task Endpoint_ConDatosFijos_DevuelveLaMismaFormaDeSiempre(string caso, string ruta)
    {
        var cliente = _factory.WithWebHostBuilder(b =>
        {
            b.ConfigureTestServices(services =>
            {
                // El repositorio se sustituye por uno que devuelve SIEMPRE lo mismo.
                // Así el test caracteriza la SERIALIZACIÓN y el SOBRE de respuesta,
                // no los datos del ambiente — y es determinista, que es lo que lo
                // hace apto para el CI.
                var doble = Substitute.For<<IRepositorio>>();
                // doble.ObtenerX(Arg.Any<string>()).Returns(DatosFijos());
                services.AddScoped(_ => doble);
            });
        }).CreateClient();

        var respuesta = await cliente.GetAsync(ruta);
        var cuerpo = await respuesta.Content.ReadAsStringAsync();

        // El status es parte del contrato tanto como el cuerpo.
        var snapshot = new
        {
            status = (int)respuesta.StatusCode,
            contentType = respuesta.Content.Headers.ContentType?.MediaType,
            cuerpo = Normalizar(cuerpo)
        };

        await Verify(snapshot).UseParameters(caso);
    }

    [Fact]
    public async Task EndpointInexistente_Devuelve404_ConElCuerpoDeSiempre()
    {
        var cliente = _factory.CreateClient();
        var respuesta = await cliente.GetAsync("/api/v2/interface/no-existe");
        respuesta.StatusCode.ShouldBe(HttpStatusCode.NotFound);
    }

    [Fact]
    public async Task EndpointAutenticado_SinToken_DevuelveElMismo401DeSiempre()
    {
        // El cuerpo del 401 también es contrato: hay fronts que lo parsean.
        var cliente = _factory.CreateClient();
        var respuesta = await cliente.GetAsync("/api/v2/interface/<ruta-autenticada>");

        respuesta.StatusCode.ShouldBe(HttpStatusCode.Unauthorized);
        var cuerpo = await respuesta.Content.ReadAsStringAsync();
        await Verify(cuerpo);
    }

    /// <summary>
    /// Quita SOLO lo que legítimamente cambia en cada corrida. Todo lo demás se
    /// compara tal cual: el casing, los nulos y el formato de fecha SON el contrato.
    /// </summary>
    private static string Normalizar(string json)
    {
        if (string.IsNullOrWhiteSpace(json)) return json;

        JsonNode? raiz;
        try { raiz = JsonNode.Parse(json); }
        catch { return json; }   // no es JSON (CSV, Excel, texto): se compara crudo
        if (raiz is null) return json;

        // Ejemplos de lo que se neutraliza: ids autogenerados, timestamps de emisión,
        // duraciones. Se hace por RUTA CONCRETA, no por nombre suelto: reemplazar
        // "todo lo que se llame fecha" puede tapar justo el cambio que se busca.
        // if (raiz["data"]?["fechaEmision"] is not null) raiz["data"]!["fechaEmision"] = "<normalizado>";

        return raiz.ToJsonString(new JsonSerializerOptions { WriteIndented = true });
    }
}
