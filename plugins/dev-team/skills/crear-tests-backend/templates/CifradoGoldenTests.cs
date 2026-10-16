// ─────────────────────────────────────────────────────────────────────────────
// CifradoGoldenTests.cs — prioridad 3 del análisis de riesgo.
//
// POR QUÉ IMPORTA MÁS DE LO QUE PARECE: si una migración cambia la derivación de
// clave o el algoritmo, el código sigue compilando, sigue cifrando y sigue
// descifrando... pero NO PUEDE LEER LO QUE YA ESTÁ EN LA BASE. No hay rollback
// que arregle eso; hay que restaurar datos.
//
// EL TEST QUE VALE ES EL DE VUELTA: un valor cifrado con el runtime de HOY tiene
// que descifrarse igual con el runtime de mañana.
//
// CONTEXTO DE PLATAFORMA (aplica a varios componentes de la flota):
//   · RijndaelManaged está obsoleto desde .NET 6 (SYSLIB0022)
//   · Rfc2898DeriveBytes(string, byte[]) es SYSLIB0060 en .NET 10
// Los warnings se leen, NO se silencian con NoWarn (regla 7 de migrar-dotnet).
// Este test no arregla nada: congela el comportamiento y se lo entrega a cybersec
// con evidencia.
//
// GATE DE CYBERSEC OBLIGATORIO.
// Placeholders: <Namespace>, <Cifrador>
// ─────────────────────────────────────────────────────────────────────────────

namespace <Namespace>.Tests.Caracterizacion;

[Trait("categoria", "caracterizacion")]
public class CifradoGoldenTests
{
    // ── Vectores ─────────────────────────────────────────────────────────────
    // CÓMO SE GENERAN, ANTES DE MIGRAR:
    //   1. Con el binario actual, cifrar cada texto de la lista.
    //   2. Pegar el resultado exacto acá.
    //   3. Sumar AL MENOS UN VALOR REAL SACADO DE LA BASE (el cifrado, no el
    //      texto claro), para probar contra el formato que existe de verdad.
    //      Si el texto claro es dato de cliente, se usa un registro de prueba:
    //      nunca datos personales en el repo (T-SEC-01).
    public static TheoryData<string, string> Vectores => new()
    {
        // { textoClaro, cifradoEsperadoEnBase64 }
        { "hola",                      "PEGAR_CIFRADO_GENERADO_HOY" },
        { "1234567890",                "PEGAR_CIFRADO_GENERADO_HOY" },
        { "texto con ñ, tildes y ü",   "PEGAR_CIFRADO_GENERADO_HOY" },
        { "",                          "(este caso va aparte: hoy lanza)" },
    };

    [Theory]
    [MemberData(nameof(Vectores))]
    public void Encriptar_TextoConocido_ProduceElMismoCifradoQueSiempre(string claro, string esperado)
    {
        if (esperado.StartsWith("PEGAR") || esperado.StartsWith("("))
            return; // vector sin completar: se completa antes de cerrar la suite

        <Cifrador>.Encriptar(claro).ShouldBe(esperado);
    }

    [Theory]
    [MemberData(nameof(Vectores))]
    public void Desencriptar_CifradoExistente_DevuelveElTextoOriginal(string claro, string cifrado)
    {
        if (cifrado.StartsWith("PEGAR") || cifrado.StartsWith("("))
            return;

        // ESTE es el test que protege los datos que ya están en la base.
        <Cifrador>.Desencriptar(cifrado).ShouldBe(claro);
    }

    [Fact]
    public void IdaYVuelta_CualquierTexto_DevuelveElOriginal()
    {
        const string texto = "Operación 12345 — cliente ñandú";
        <Cifrador>.Desencriptar(<Cifrador>.Encriptar(texto)).ShouldBe(texto);
    }

    [Fact]
    public void Encriptar_TextoVacio_LanzaArgumentNullException()
    {
        // Caracterización pura: documenta el contrato ACTUAL, no el deseable.
        Should.Throw<ArgumentNullException>(() => <Cifrador>.Encriptar(""));
    }

    [Fact]
    public void Desencriptar_TextoQueNoEsBase64_Lanza()
    {
        Should.Throw<Exception>(() => <Cifrador>.Desencriptar("esto no es base64 !!"));
    }

    [Fact]
    public void Encriptar_DosVeces_DaElMismoResultado()
    {
        // Fija que el esquema es DETERMINISTA (IV fijo). No es una buena propiedad
        // criptográfica, pero es la de hoy, y cualquier cambio rompe los datos
        // existentes. El hallazgo va a cybersec; el test solo lo deja por escrito.
        var a = <Cifrador>.Encriptar("mismo texto");
        var b = <Cifrador>.Encriptar("mismo texto");
        a.ShouldBe(b);
    }
}
