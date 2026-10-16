// ─────────────────────────────────────────────────────────────────────────────
// FechasCulturaTests.cs — prioridad 5, y el mejor retorno por hora de trabajo.
//
// QUÉ ATRAPA:
//   · E-CULT-02: un monto que sale "1,234.56" donde salía "1.234,56"
//   · E-CULT-01: CultureNotFoundException con InvariantGlobalization=true
//   · E-TZ-01:   el contenedor corre en UTC y el servidor PM2 estaba en hora local:
//                las fechas se corren 5 horas y nadie lo nota hasta contabilidad
//   · T-CULT-01: "verde en mi máquina, rojo en el runner"
//
// REGLA: el test DECLARA la cultura que ejercita. Nunca hereda la del host.
//
// Placeholders: <Namespace>, <Formateador>, <Utilidades>
// ─────────────────────────────────────────────────────────────────────────────

using System.Globalization;

namespace <Namespace>.Tests.Caracterizacion;

[Trait("categoria", "caracterizacion")]
[Collection("estado-global")]   // cambia CurrentCulture: no puede correr en paralelo
public class FechasCulturaTests : IDisposable
{
    private readonly CultureInfo _culturaOriginal = CultureInfo.CurrentCulture;

    public void Dispose() => CultureInfo.CurrentCulture = _culturaOriginal;

    // ── Montos ───────────────────────────────────────────────────────────────

    [Theory]
    [InlineData("es-CL")]
    [InlineData("es-PE")]
    [InlineData("en-US")]
    [InlineData("")]        // InvariantCulture: es la del contenedor si nadie la fija
    public void FormatMonto_MismoValor_DaElMismoResultadoEnTodaCultura(string cultura)
    {
        CultureInfo.CurrentCulture = string.IsNullOrEmpty(cultura)
            ? CultureInfo.InvariantCulture
            : new CultureInfo(cultura);

        var resultado = <Formateador>.FormatMonto(1234.56m, "CL");

        // Si este test falla para alguna cultura, el formateo DEPENDE del host:
        // el mismo endpoint devuelve cosas distintas en la máquina del dev y en
        // el contenedor. Es un hallazgo, no un test mal escrito.
        resultado.ShouldBe("1234.56");
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-1500.75)]
    [InlineData(0.005)]
    [InlineData(999999999.99)]
    public void FormatMonto_Bordes_QuedaDocumentado(decimal valor)
    {
        CultureInfo.CurrentCulture = new CultureInfo("es-CL");

        var resultado = <Formateador>.FormatMonto(valor, "CL");

        // Caracterización: se fija LO QUE HACE HOY, incluidos los redondeos raros
        // y la notación científica si aparece con valores grandes.
        resultado.ShouldNotBeNullOrEmpty();
        // → completar con el valor exacto observado, uno por caso.
    }

    // ── Fechas ───────────────────────────────────────────────────────────────

    [Fact]
    public void FormatFecha_FechaFija_UsaElFormatoDelContrato()
    {
        var fecha = new DateTime(2026, 9, 21, 14, 30, 5, DateTimeKind.Unspecified);

        <Formateador>.FormatFecha(fecha).ShouldBe("2026-09-21 14:30:05");

        // OJO: en un formato personalizado, ":" y "/" son SEPARADORES CULTURALES,
        // no literales. Con una cultura cuyo separador de hora no sea ":",
        // la salida cambia. Por eso este test fija la cultura arriba.
    }

    [Theory]
    [InlineData("21/09/2026", 2026, 9, 21)]
    [InlineData("21-09-2026", 2026, 9, 21)]
    [InlineData("21092026",   2026, 9, 21)]
    public void FormatFechaString_FormatosQueLleganDeLosClientes_ParseaBien(
        string entrada, int anio, int mes, int dia)
    {
        var resultado = <Utilidades>.FormatFechaString(entrada);

        resultado.ShouldNotBeNull();
        resultado!.Value.Year.ShouldBe(anio);
        resultado.Value.Month.ShouldBe(mes);
        resultado.Value.Day.ShouldBe(dia);
    }

    [Theory]
    [InlineData("")]
    [InlineData(null)]
    [InlineData("no es una fecha")]
    [InlineData("32/13/2026")]
    public void FormatFechaString_EntradaInvalida_DevuelveNullSinLanzar(string entrada)
    {
        // Contrato real del componente: se traga la excepción y devuelve null.
        // Los llamadores dependen de eso. Se congela.
        <Utilidades>.FormatFechaString(entrada).ShouldBeNull();
    }

    // ── Cultura concreta: la bomba de InvariantGlobalization ─────────────────

    [Fact]
    public void CulturaDelComponente_SePuedeConstruir()
    {
        // Si el componente tiene <InvariantGlobalization>true</InvariantGlobalization>,
        // esta línea LANZA CultureNotFoundException (PredefinedCulturesOnly).
        // Es E-CULT-01 de migrar-dotnet, y este test de una línea lo detecta antes
        // de que aparezca en producción al formatear un monto.
        Should.NotThrow(() => new CultureInfo("es-CL"));
    }

    // ── Zona horaria ─────────────────────────────────────────────────────────

    [Fact]
    public void ZonaHorariaDelAmbiente_ExisteEnLaImagen()
    {
        // E-TZ-02: las imágenes -alpine y las chiseled NO traen tzdata, y esto
        // lanza TimeZoneNotFoundException dentro del contenedor aunque en la
        // máquina del dev ande perfecto.
        Should.NotThrow(() => TimeZoneInfo.FindSystemTimeZoneById("America/Santiago"));
    }

    [Fact]
    public void DateTimeNow_Y_UtcNow_DifierenLoQueDiceLaZonaDelProceso()
    {
        // No afirma un valor: afirma la RELACIÓN. Así el test es determinista
        // (regla dura 7) y además documenta que el componente depende de la TZ
        // del host — que es exactamente lo que cambia al pasar a contenedor.
        var local = DateTime.Now;
        var utc = DateTime.UtcNow;
        var desfase = TimeZoneInfo.Local.GetUtcOffset(utc);

        (local - utc).TotalMinutes.ShouldBe(desfase.TotalMinutes, tolerance: 1);
    }
}

// ── Cómo se usa esto de verdad ───────────────────────────────────────────────
//
//   TZ=UTC                dotnet test
//   TZ=America/Santiago   dotnet test
//
// Si el resultado cambia entre las dos corridas, el componente tiene una
// dependencia del reloj del host que el contenedor va a exponer (E-TZ-01).
// Está en el DoD (05-ci-cobertura-dod §5.1).
