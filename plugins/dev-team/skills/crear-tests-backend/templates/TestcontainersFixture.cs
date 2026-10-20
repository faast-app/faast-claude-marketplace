// ─────────────────────────────────────────────────────────────────────────────
// TestcontainersFixture.cs — motores reales (MySQL y SQL Server) en Docker.
//
// ANTES DE USAR ESTO, CONTESTAR: ¿de dónde sale el esquema?
//   · Migraciones de EF en el repo      → db.Database.Migrate() y listo
//   · Dump de estructura versionado     → se aplica acá (Esquema/*.sql)
//   · Ninguna de las dos                → ESTE FIXTURE NO SIRVE. El contenedor
//     arranca vacío y los tests fallan con "Invalid object name". Es T-DB-04:
//     se pide el dump al dba y mientras tanto se usa la familia (d), contrato
//     contra QA en solo lectura.
//
// UNA instancia por SUITE (ICollectionFixture), nunca por test (T-TC-02).
// La imagen de SQL Server es pesada y su arranque no es inmediato.
//
// Licencia de la imagen de SQL Server: revisar sus términos de uso antes de
// meterla en el CI [G].
// ─────────────────────────────────────────────────────────────────────────────

using Testcontainers.MsSql;
using Testcontainers.MySql;

namespace <Namespace>.Tests.Integracion;

/// <summary>
/// Se comparte con [Collection("bases")] en las clases de test que lo necesiten.
/// </summary>
public sealed class BasesDeDatosFixture : IAsyncLifetime
{
    // Tags desde templates/parametros-tests.env. Fijos, nunca "latest" sin versión:
    // un tag flotante hace que la suite de hoy no sea la de mañana (mismo espíritu
    // que E-NU-03).
    private readonly MsSqlContainer _sqlServer = new MsSqlBuilder()
        .WithImage("mcr.microsoft.com/mssql/server:2022-latest")
        .Build();

    private readonly MySqlContainer _mysql = new MySqlBuilder()
        .WithImage("mysql:8.0")
        .WithDatabase("fintec_test")
        .WithUsername("test")
        .WithPassword("test-solo-local")     // valor de contenedor efímero, no es un secreto
        .Build();

    public string CadenaSqlServer => _sqlServer.GetConnectionString();
    public string CadenaMySql => _mysql.GetConnectionString();

    public async Task InitializeAsync()
    {
        // En paralelo: son dos imágenes y dos arranques independientes.
        await Task.WhenAll(_sqlServer.StartAsync(), _mysql.StartAsync());

        await AplicarEsquemaAsync();
    }

    /// <summary>
    /// Siembra la estructura. Elegir UNA de las tres opciones según el repo.
    /// </summary>
    private async Task AplicarEsquemaAsync()
    {
        // OPCIÓN A — hay migraciones de EF:
        //   using var scope = ...;
        //   await scope.ServiceProvider.GetRequiredService<Contexto>().Database.MigrateAsync();

        // OPCIÓN B — hay dump de estructura entregado por el dba (sin datos):
        //   foreach (var archivo in Directory.GetFiles("Esquema", "*.sql").OrderBy(x => x))
        //       await EjecutarScriptAsync(archivo);

        // OPCIÓN C — EnsureCreated() a partir del modelo de EF.
        //   ATENCIÓN: NO es el esquema de producción. Tipos, colaciones, índices y
        //   constraints pueden no coincidir. Sirve para probar TU LINQ, no para
        //   afirmar que la consulta anda contra la base real (01-analisis §5).

        await Task.CompletedTask;
    }

    public async Task DisposeAsync()
    {
        await Task.WhenAll(_sqlServer.DisposeAsync().AsTask(),
                           _mysql.DisposeAsync().AsTask());
    }
}

[CollectionDefinition("bases")]
public class ColeccionBases : ICollectionFixture<BasesDeDatosFixture>
{
    // Sin cuerpo: xUnit solo necesita la declaración.
    // Todas las clases con [Collection("bases")] comparten UNA instancia y NO
    // corren en paralelo entre sí — que es justo lo que hace falta cuando
    // comparten una base (T-DB-05 / T-FLAKE-01).
}

// ── Cómo se usa ──────────────────────────────────────────────────────────────
//
// [Collection("bases")]
// [Trait("categoria", "integracion")]
// public class CarteraIntegracionTests
// {
//     private readonly HttpClient _cliente;
//
//     public CarteraIntegracionTests(BasesDeDatosFixture bases)
//     {
//         var factory = new FaastWebApplicationFactory();
//         factory.ConexionesDeTest["conexion-backoffice"] = bases.CadenaSqlServer;
//         factory.ConexionesDeTest["conexion-fintex"]     = bases.CadenaMySql;
//         factory.ConexionesDeTest["conexion-buros"]      = bases.CadenaMySql;
//         _cliente = factory.CreateClient();
//     }
// }
//
// Si Docker no está disponible, la suite falla con un mensaje claro (T-TC-01).
// En CI eso se maneja condicionando el job, no salteando los tests en silencio.
