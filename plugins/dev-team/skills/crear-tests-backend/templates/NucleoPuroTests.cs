// ─────────────────────────────────────────────────────────────────────────────
// NucleoPuroTests.cs — el primer bloque de trabajo y el de mejor retorno.
//
// QUÉ VA ACÁ: las clases estáticas puras del componente (formateo, utilidades,
// conversiones, validadores). Entra un valor, sale un valor: sin DI, sin base,
// sin Docker, sin red. Son tests en verde el primer día.
//
// EN UN LEGADO SE ESCRIBEN COMO CARACTERIZACIÓN, NO COMO ESPECIFICACIÓN:
// se fija lo que el método HACE HOY, incluidos sus bugs. Si aparece un bug, se
// congela con un test que lo documenta y se abre un ticket aparte. Arreglarlo en
// el mismo PR es cambiar comportamiento mientras se construye la red que debía
// vigilarlo.
//
// Placeholders: <Namespace>, <Utilidades>
// ─────────────────────────────────────────────────────────────────────────────

namespace <Namespace>.Tests.Unit;

[Trait("categoria", "unit")]
public class NucleoPuroTests
{
    // ── Caso normal ──────────────────────────────────────────────────────────

    [Theory]
    [InlineData("  hola   mundo  ", " hola mundo ")]
    [InlineData("sin espacios", "sin espacios")]
    public void EliminarEspaciosVacios_TextoConEspaciosRepetidos_LosColapsa(string entrada, string esperado)
        => <Utilidades>.EliminarEspaciosVacios(entrada).ShouldBe(esperado);

    // ── Bordes: son los que encuentran bugs de verdad ────────────────────────

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    public void EliminarEspaciosVacios_EntradaVacia_DevuelveCadenaVaciaSinLanzar(string entrada)
    {
        // Contrato real de muchos helpers de esta flota: se tragan la excepción y
        // devuelven vacío. Los llamadores dependen de eso, así que se congela.
        <Utilidades>.EliminarEspaciosVacios(entrada).ShouldBe(string.Empty);
    }

    // ── Bug preexistente: se DOCUMENTA, no se arregla ────────────────────────

    [Fact]
    public void TipoContenidoExtension_Json_DevuelveJsonnConDosEnes()
    {
        // BUG PREEXISTENTE, congelado a propósito: la extensión de JSON sale
        // "jsonn". Arreglarlo cambia el nombre de los archivos que descargan los
        // consumidores. Ticket: <NNN>. Cuando se arregle, este test cambia EN EL
        // PR DEL ARREGLO, nunca en el de la migración (regla dura 2).
        <Utilidades>.tipoContenidoExtension("json").ShouldBe("jsonn");
    }

    // ── Entrada sucia ────────────────────────────────────────────────────────

    [Theory]
    [InlineData("Ñandú")]
    [InlineData("Peña & Cía")]
    [InlineData("texto con 'comillas'")]
    [InlineData("  ")]
    public void Utilidades_EntradaSucia_NoLanzan(string entrada)
    {
        // Un solo test que recorre la entrada rara evita media docena de 500 en
        // producción, y cuesta dos minutos.
        Should.NotThrow(() => <Utilidades>.FormatStringIsNullOrEmpty(entrada));
    }

    // ── Todo bug reportado deja un test ──────────────────────────────────────
    //
    // [Fact]
    // public void Metodo_EscenarioDelTicketNNN_NoVuelveAPasar() { ... }
    //
    // Es la única regla de crecimiento de la suite que funciona sola.
}
