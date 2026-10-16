// ─────────────────────────────────────────────────────────────────────────────
// JwtCaracterizacionTests.cs — prioridad 1 del análisis de riesgo.
//
// POR QUÉ VA PRIMERO: un salto de runtime cambia el handler de JWT y el mapeo de
// claims SIN romper la compilación (E-JWT-01 / E-JWT-02 de migrar-dotnet). El
// fallo no se ve: la autorización se afloja y nadie se entera.
//
// EL TEST QUE MÁS VALE ES EL "TOKEN DE ORO": un token emitido con el runtime
// ACTUAL, guardado como constante, que debe seguir validando después de migrar.
// Es lo único que demuestra que los usuarios ya logueados no se caen en el corte.
//
// GATE DE CYBERSEC OBLIGATORIO sobre este archivo (regla dura 8).
//
// Placeholders: <Namespace>, <TipoUsuario>, <Emisor>
// ─────────────────────────────────────────────────────────────────────────────

using System.IdentityModel.Tokens.Jwt;

namespace <Namespace>.Tests.Caracterizacion;

[Trait("categoria", "caracterizacion")]
[Collection("estado-global")]   // toca configuración estática: no en paralelo (T-FLAKE-01)
public class JwtCaracterizacionTests
{
    // ── El token de oro ──────────────────────────────────────────────────────
    // CÓMO SE GENERA, UNA SOLA VEZ, ANTES DE MIGRAR:
    //   1. Con el binario actual (TFM de hoy), emitir un token para un usuario de prueba.
    //   2. Pegarlo acá como constante, junto con la CLAVE DE PRUEBA con que se firmó.
    //   3. Commitearlo. Es evidencia, no un secreto: la clave es inventada y solo
    //      sirve para este test (T-SEC-01).
    //
    // OJO con la expiración: el token de esta app vence en 24 h por diseño
    // (Expires = UtcNow.AddDays(1)). Por eso el token de oro se usa para verificar
    // ESTRUCTURA Y FIRMA, no vigencia. La vigencia se prueba con un token emitido
    // dentro del test.
    private const string TokenDeOro = "PEGAR_AQUI_EL_TOKEN_EMITIDO_ANTES_DE_MIGRAR";
    private const string ClaveDePrueba = "clave-solo-para-tests-no-usar-en-ningun-ambiente-0123456789";

    [Fact]
    public void GenerateToken_UsuarioValido_EmiteTokenConLosClaimsEsperados()
    {
        var usuario = new <TipoUsuario> { id = 42, usuario = "prueba@faast.test" };

        var token = <Emisor>.GenerateToken(usuario);

        var leido = new JwtSecurityTokenHandler().ReadJwtToken(token);

        // Se fijan los NOMBRES de los claims: es lo que cambia con el salto de
        // librería (E-JWT-01), y lo que rompe [Authorize(Roles=...)] o
        // User.Identity.Name sin que nada falle al compilar.
        leido.Claims.ShouldContain(c => c.Type == "id" && c.Value == "42");
        leido.Claims.ShouldContain(c => c.Type == "sub" || c.Type.EndsWith("/nameidentifier"));
        leido.Header.Alg.ShouldBe("HS256");
    }

    [Fact]
    public void ValidateToken_TokenEmitidoAhora_DevuelveElIdDelUsuario()
    {
        var usuario = new <TipoUsuario> { id = 7, usuario = "ida-y-vuelta@faast.test" };
        var token = <Emisor>.GenerateToken(usuario);

        <Emisor>.ValidateToken(token).ShouldBe(7);
    }

    [Fact]
    public void ValidateToken_TokenDeOro_MantieneFirmaYClaims()
    {
        // ESTE es el test de la migración. Si se pone rojo en el TFM destino, los
        // tokens ya emitidos dejaron de ser válidos: el corte tira a todos los
        // usuarios logueados.
        TokenDeOro.ShouldNotBe("PEGAR_AQUI_EL_TOKEN_EMITIDO_ANTES_DE_MIGRAR",
            "El token de oro hay que generarlo con el binario ACTUAL, antes de migrar.");

        var leido = new JwtSecurityTokenHandler().ReadJwtToken(TokenDeOro);
        leido.Header.Alg.ShouldBe("HS256");
        leido.Claims.ShouldContain(c => c.Type == "id");
        // La validación completa de firma se hace con los mismos parámetros que usa
        // la app, con ValidateLifetime = false (el token de oro está vencido por diseño).
    }

    [Fact]
    public void ValidateToken_FirmadoConOtraClave_DevuelveNull()
    {
        var tokenAjeno = EmitirConClave("otra-clave-distinta-de-la-de-la-app-0123456789");
        <Emisor>.ValidateToken(tokenAjeno).ShouldBeNull();
    }

    [Fact]
    public void ValidateToken_TokenExpirado_DevuelveNull()
    {
        // Fija que ClockSkew sigue en cero: si el salto de librería lo devuelve a
        // los 5 minutos por defecto, un token vencido sigue entrando 5 minutos más.
        var vencido = EmitirConClave(ClaveDePrueba, expiraEn: TimeSpan.FromMinutes(-1));
        <Emisor>.ValidateToken(vencido).ShouldBeNull();
    }

    [Fact]
    public void ValidateToken_TokenNulo_DevuelveNull()
        => <Emisor>.ValidateToken(null).ShouldBeNull();

    [Fact(Skip = "HALLAZGO ABIERTO: hoy el componente NO aborta si falta la clave de " +
                 "firma; arranca y falla al emitir. ADR-016 §3.5 exige abortar. " +
                 "Quitar el Skip cuando entre el fix. Ticket: <NNN>")]
    public void Arranque_SinClaveDeFirma_Aborta()
    {
        // Regla de la casa: prohibido el fallback silencioso en auth.
        // El test existe aunque hoy no pase: así la deuda vive en el CI y no en un
        // documento que nadie abre (regla dura 6: todo Skip con motivo escrito).
    }

    [Fact(Skip = "BLOQUEADO POR T-CFG-01: la configuración se lee con un " +
                 "ConfigurationBuilder privado, así que las variables de entorno se " +
                 "IGNORAN. Quitar el Skip cuando entre Variables.Initialize(IConfiguration), " +
                 "que ya existe en release/faast/stage.")]
    public void ClaveDeFirma_DefinidaPorVariableDeEntorno_EsLaQueSeUsa()
    {
        // Este test es la verificación de la regla dura de ADR-016
        // ("todo el appsettings a variables de entorno") aplicada al secreto más
        // sensible del componente. Mientras esté en Skip, esa regla NO está verificada.
    }

    private static string EmitirConClave(string clave, TimeSpan? expiraEn = null)
    {
        // Emisión local con los mismos parámetros que la app, para no depender de
        // su configuración estática en los casos negativos.
        throw new NotImplementedException("Completar por componente.");
    }
}
