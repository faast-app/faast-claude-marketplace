// ─────────────────────────────────────────────────────────────────────────────
// FaastWebApplicationFactory.cs — base de los tests de integración por HTTP.
//
// Levanta la app real (su DI, su pipeline, su middleware) en memoria.
//
// Tres decisiones de diseño, y el porqué de cada una:
//
// 1. LA CONFIGURACIÓN ENTRA POR VARIABLES DE ENTORNO, con el formato Seccion__Clave.
//    Es la regla de la casa (ADR-016 §Paso 4: "todo el appsettings a variables"), y
//    además es la ÚNICA forma de verificar que esa regla se cumple. Si el componente
//    lee su configuración de un ConfigurationBuilder privado (T-CFG-01), estos tests
//    lo van a exponer: es una señal, no una molestia.
//
// 2. NADA SALE A INTERNET. Sin DSN de telemetría (T-OBS-01), sin SMTP, sin Hangfire
//    server (T-HF-01). Un test que manda un correo real es un incidente.
//
// 3. CULTURA Y ZONA HORARIA EXPLÍCITAS. El resultado no puede depender de la máquina
//    de quien corre la suite (T-CULT-01 / T-TIME-01).
//
// REQUISITO: `public partial class Program { }` al final de Program.cs (T-WAF-01).
// Es aditivo: no cambia el pipeline ni el comportamiento en runtime.
//
// Placeholders: <Namespace>, <Contexto>
// ─────────────────────────────────────────────────────────────────────────────

using System.Globalization;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.Extensions.Hosting;

namespace <Namespace>.Tests.Integracion;

public class FaastWebApplicationFactory : WebApplicationFactory<Program>
{
    /// <summary>
    /// Claves que el test inyecta como variables de entorno.
    /// SOLO VALORES INVENTADOS. Ningún secreto real acá dentro (T-SEC-01).
    /// </summary>
    private static readonly Dictionary<string, string> ConfiguracionDeTest = new()
    {
        // ── Obligatorias para que la app arranque ────────────────────────────
        ["ASPNETCORE_ENVIRONMENT"] = "Testing",

        // ── Auth: clave de prueba, generada, nunca la real ───────────────────
        ["AppSettings__JwtSecret"] = "clave-solo-para-tests-no-usar-en-ningun-ambiente-0123456789",

        // ── Servicios externos: apuntados a un agujero negro ─────────────────
        // Si un test hace que el componente llame de verdad a alguno de estos,
        // va a fallar por timeout. Eso es correcto: ese test está mal clasificado.
        ["AppSettings__CRM__url"] = "http://localhost:1/crm",
        ["AppSettings__CRM__apikey"] = "apikey-de-test",
        ["AppSettings__Contabilidad__url"] = "http://localhost:1/contabilidad",
        ["AppSettings__SMTP__SmtpServer"] = "localhost",
        ["AppSettings__SMTP__SmtpPort"] = "1",

        // ── Telemetría apagada (T-OBS-01) ────────────────────────────────────
        ["Sentry__Dsn"] = "",
        ["Faast__Telemetry__Errors__Sink"] = "none",
        ["Faast__Telemetry__Errors__Dsn"] = "",
    };

    /// <summary>
    /// Cadenas de conexión que apuntan a los contenedores. Las setea la suite de
    /// base de datos ANTES de crear el cliente. Si quedan vacías, la app arranca
    /// igual, pero cualquier endpoint que toque datos va a fallar — y eso está bien:
    /// los tests que no tocan datos (contrato OpenAPI) tienen que poder correr solos.
    /// </summary>
    public Dictionary<string, string> ConexionesDeTest { get; } = new();

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        // El orden importa: las variables se definen ANTES de que el host lea la
        // configuración. En el código siempre se usa "Seccion:Clave"; el doble
        // guion bajo existe solo en la variable de entorno (T-WAF-04).
        foreach (var (clave, valor) in ConfiguracionDeTest)
            Environment.SetEnvironmentVariable(clave, valor);

        foreach (var (clave, valor) in ConexionesDeTest)
            Environment.SetEnvironmentVariable($"ConnectionStrings__{clave}", valor);

        // Que una variable heredada del entorno de quien corre la suite no se cuele.
        // Es como termina un error de test en el Sentry del ambiente (T-OBS-01).
        Environment.SetEnvironmentVariable("SENTRY_DSN", null);

        builder.UseEnvironment("Testing");

        // T-WAF-02: sin puerto HTTPS conocido, UseHttpsRedirection responde 307 a todo.
        builder.UseSetting("https_port", "443");

        builder.ConfigureAppConfiguration((_, config) =>
        {
            // Las variables de entorno mandan por encima de cualquier appsettings.
            config.AddEnvironmentVariables();
        });

        builder.ConfigureTestServices(services =>
        {
            // ── 1. Contextos de EF apuntados al contenedor ────────────────────
            // Se quita el registro original y se pone el de test. Si la suite no
            // levantó contenedores, se deja el original: los tests que no tocan
            // datos igual corren.
            // ReemplazarDbContext<<Contexto>>(services, ConexionesDeTest);

            // ── 2. Hangfire: nunca el servidor en tests (T-HF-01) ─────────────
            // services.RemoveAll<IHostedService>();   // ← revisar qué más se lleva puesto
            QuitarHostedServicesDeJobs(services);

            // ── 3. Dobles de fronteras que el test no quiere ejercitar ────────
            // services.RemoveAll<IUserRepository>();
            // services.AddScoped(_ => Substitute.For<IUserRepository>());
        });
    }

    /// <summary>
    /// Fija cultura y zona horaria para que la suite dé el mismo resultado en la
    /// máquina de cada uno y en el runner (T-CULT-01).
    /// Se llama una vez, desde el fixture de colección.
    /// </summary>
    public static void FijarCulturaYZonaHoraria(string cultura = "es-CL")
    {
        var ci = new CultureInfo(cultura);
        CultureInfo.DefaultThreadCurrentCulture = ci;
        CultureInfo.DefaultThreadCurrentUICulture = ci;
        // OJO: si el componente tiene <InvariantGlobalization>true</InvariantGlobalization>,
        // la línea de arriba LANZA CultureNotFoundException. Eso no es un bug del test:
        // es E-CULT-01 del catálogo de migrar-dotnet, y hay que reportarlo.
    }

    private static void QuitarHostedServicesDeJobs(IServiceCollection services)
    {
        // Implementación concreta por componente: quitar solo el servidor de jobs,
        // no todos los IHostedService (que pueden incluir cosas necesarias).
        // Ver T-HF-01.
    }

    // private static void ReemplazarDbContext<TContext>(IServiceCollection services,
    //                                                   IDictionary<string,string> conexiones)
    //     where TContext : DbContext
    // {
    //     services.RemoveAll<DbContextOptions<TContext>>();
    //     services.RemoveAll<TContext>();
    //     services.AddDbContext<TContext>(o => o.UseSqlServer(conexiones["..."]));
    //     // MySQL: usar ServerVersion.Parse(...), NO AutoDetect — T-DB-02.
    // }
}
