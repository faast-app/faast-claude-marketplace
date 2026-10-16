# 03 — Stack recomendado, versiones y licencias

**Fase 3 de `crear-tests-backend`.**

Todo lo de este documento se consultó contra la **API de nuget.org el 2026-09-21**
(`api.nuget.org/v3-flatcontainer/<pkg>/index.json` para versiones,
`.../<pkg>/<ver>/<pkg>.nuspec` para licencia y frameworks).

**Leyenda:** **[V]** verificado contra nuget.org hoy · **[G]** conocimiento general de la
plataforma, sin verificar en este ambiente.

> **Por qué este documento existe y no es "usá xUnit y FluentAssertions":** porque
> `FluentAssertions` cambió a licencia comercial, `Moq` tuvo un incidente de privacidad, y
> `AutoMapper` y `MediatR` ya obligaron a `migrar-dotnet` a prohibir `dotnet outdated -u`
> en esta flota (regla 6, `E-LIC-02`). **Un paquete de test también es una dependencia
> legal de la empresa.**

---

## 1. Resumen: lo que se instala

Las versiones exactas viven en `templates/parametros-tests.env`. Esta tabla es el porqué.

| Rol | Paquete | Versión [V] | Licencia | Veredicto |
|---|---|---|---|---|
| Framework de test | **xUnit v2** `xunit` | **2.9.3** | Apache-2.0 [V] | **Default de la flota** |
| Runner VSTest | `xunit.runner.visualstudio` | **3.1.5** | Apache-2.0 [G] | Estable. Existe 4.0.0 [V], sin rodaje |
| Host de test | `Microsoft.NET.Test.Sdk` | **18.10.1** | MIT [G] | Necesario para `dotnet test` con VSTest |
| Aserciones | **`Shouldly`** | **4.3.0** | **BSD-3-Clause** [V] | **Default.** Sin historia de licencias |
| Dobles | **`NSubstitute`** | **6.2.0** | **BSD-3-Clause** [V] | **Default** |
| Snapshots | `Verify.Xunit` | **31.12.5** | MIT [V] | Tiene asset `net10.0` [V] |
| Cobertura | `coverlet.collector` | **10.0.1** | MIT [V] | Recolector para `dotnet test --collect` |
| Integración HTTP | `Microsoft.AspNetCore.Mvc.Testing` | **8.0.31** / **10.0.12** | MIT [G] | **Debe coincidir con el TFM de la app** (§4) |
| Contenedores | `Testcontainers` + `.MySql` + `.MsSql` | **4.15.0** | MIT [V] | Tiene asset `net10.0` [V] |
| Datos falsos | `Bogus` | **35.6.5** | archivo `LICENSE` (MIT [G]) | Opcional |
| Mock de HTTP | `WireMock.Net` | **2.17.0** | Apache-2.0 [V] | Solo si el `HttpClient` es interceptable |
| Limpieza de BD | `Respawn` | **7.0.0** | [G] | Solo con Testcontainers |
| Reporte de cobertura | `ReportGenerator` | **5.5.11** | [G] | Herramienta de CI, no del proyecto |

**Nada de lo anterior entra al artefacto desplegado:** son `PackageReference` de un
proyecto de test que no se publica.

---

## 2. Las tres decisiones que no son obvias

### 2.1 Aserciones: **FluentAssertions ya no es gratis**

| Paquete | Versión | Licencia en el `.nuspec` | Veredicto |
|---|---|---|---|
| `FluentAssertions` | **7.2.0** | `<license type="expression">Apache-2.0</license>` [V] | Última libre |
| `FluentAssertions` | **8.11.0** (última) | `<license type="file">LICENSE</license>` + `<requireLicenseAcceptance>true</requireLicenseAcceptance>` + `projectUrl` = `xceed.com/products/unit-testing/fluent-assertions/` [V] | **Comercial. No se instala sin compra** |
| `AwesomeAssertions` | **9.6.0** | `Apache-2.0` [V] | Fork comunitario de la línea 7 [G] |
| **`Shouldly`** | **4.3.0** | `BSD-3-Clause` [V] | **Recomendado** |

**Recomendación: `Shouldly`.**

Es la opción que no obliga a nadie a leer un contrato. `AwesomeAssertions` es
técnicamente un reemplazo directo para quien ya escribió con la sintaxis de
FluentAssertions, pero es un **fork de un producto que hoy es comercial**: antes de
adoptarlo en repos nuevos conviene un visto bueno explícito, porque la discusión de
titularidad no es nuestra y no queremos heredarla [G]. Para una suite que arranca de
cero, elegir `Shouldly` evita el tema entero.

**Si un repo ya tiene FluentAssertions:** se **fija** en `7.2.0` y no se toca. Subir a 8
durante una migración es exactamente el error que `E-LIC-02` describe.

**Alternativa de costo cero:** el `Assert` nativo de xUnit. Menos legible en cadenas
largas, pero cero dependencias y cero licencias. Es una opción válida y hay que decirlo.

### 2.2 Dobles: NSubstitute, y qué pasó con Moq

- **`NSubstitute` 6.2.0, BSD-3-Clause** [V]. Sintaxis corta, sin `.Object`, sin modo
  estricto por defecto. **Es el default.**
- **`Moq` 4.20.72, BSD-3-Clause** [V]. La polémica fue **SponsorLink**: la versión
  **4.20.0** incorporó un componente que recolectaba el correo del desarrollador desde
  la configuración de git durante el build; se retiró en **4.20.2** [G]. Las versiones
  actuales no lo traen [G, verificar en el `.nuspec`/contenido antes de afirmar nada ante
  Compliance], pero el episodio dejó a muchos equipos fuera.

**Regla para la flota:** repos nuevos → NSubstitute. Repos que ya usan Moq → **se
quedan en Moq**, fijado en una versión ≥ 4.20.2. Migrar dobles no agrega una sola
verificación de negocio y rompe tests que hoy funcionan.

### 2.3 xUnit v2 vs v3

| | xUnit **v2** (`xunit` 2.9.3) [V] | xUnit **v3** (`xunit.v3` 4.0.1) [V] |
|---|---|---|
| Licencia | Apache-2.0 [V] | Apache-2.0 [V] |
| Frameworks del paquete | vía netstandard: corre en net8 y net10 [G] | `net8.0` y `net472` [V] → corre en net10 [G] |
| Modelo de ejecución | ensamblado de librería + runner VSTest | **el proyecto de test es un ejecutable** (`<OutputType>Exe</OutputType>`), con Microsoft.Testing.Platform [G] |
| Kilometraje en la flota | El ecosistema entero (Verify, coverlet, loggers) lo soporta hace años | Más nuevo; integraciones y plantillas todavía se están acomodando [G] |

**Recomendación: v2 para todo lo que se escriba en esta ola.** El objetivo es tener red
de seguridad antes de la migración de TFM, no estrenar runner. **v3 se evalúa después**
del piloto, en un repo nuevo, y con su propia decisión.

> Si alguien crea un proyecto v3 sin `<OutputType>Exe</OutputType>`, no se descubre
> ningún test y `dotnet test` **pasa en verde con 0 tests** [G]. Ver `T-CI-02`: esa es la
> falla más peligrosa de todo el catálogo.

---

## 3. NUnit y MSTest

Existen, funcionan, y sus versiones actuales son `NUnit` **4.6.1** + `NUnit3TestAdapter`
**6.3.0**, y `MSTest` **4.4.1** [V]. **No se usan acá** por una razón operativa, no
técnica: una flota de ~38 componentes con dos frameworks de test distintos duplica las
plantillas, los loggers, la configuración de cobertura y el conocimiento del equipo.
**Un solo framework para toda la flota.** Si un repo ya tiene NUnit, se queda con NUnit y
no se migra.

---

## 4. Compatibilidad con net8 y net10: las dos reglas que rompen el build

### 4.1 `Microsoft.AspNetCore.*` sigue al TFM de la app, siempre

`Microsoft.AspNetCore.Mvc.Testing` es parte del framework compartido: la versión **tiene
que coincidir con la major del runtime de la app**.

| TFM de la app | Versión del paquete [V] |
|---|---|
| `net8.0` | `8.0.31` |
| `net10.0` | `10.0.12` |

En un `.csproj` que multi-targetea, va condicionado:

```xml
<PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="8.0.31"
                  Condition="'$(TargetFramework)' == 'net8.0'" />
<PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="10.0.12"
                  Condition="'$(TargetFramework)' == 'net10.0'" />
```

### 4.2 Los paquetes de EF de test siguen a **EF Core**, no al TFM

En esta flota **EF Core queda en la línea 9 aunque la app vaya a net10**, por el techo de
Pomelo (ADR-017 §4, decisión (c) aceptada). Entonces:

| Paquete | Versión con EF Core 9 [V] |
|---|---|
| `Microsoft.EntityFrameworkCore.Sqlite` | `9.0.20` |
| `Microsoft.EntityFrameworkCore.InMemory` | `9.0.20` (y ver §2 de `02-estrategia`: **no se usa**) |

Poner `10.0.12` en el proyecto de test con la app en EF Core 9 produce `NU1605` y, si se
silencia, `MissingMethodException` en runtime — `E-NU-01` y `E-RT-01` del catálogo de
`migrar-dotnet`, ahora dentro de los tests.

### 4.3 El TFM del proyecto de test **es el mismo** que el de la app

Es `E-CS-03`: `gw-mobile-fintec` tiene app `net8.0` y test `net10.0`, y por eso la
solución no compila [V]. Durante una migración por escalones, el proyecto de test sube en
el **mismo commit** que la app.

---

## 5. Lo que hace falta en la máquina y en el runner

| Requisito | Para qué | Si falta |
|---|---|---|
| SDK del TFM de la app | compilar y correr | nada corre |
| **Docker** | Testcontainers | Integración no corre. **No es un error: es un gap declarado** |
| Nada más | Unit y Caracterización | — |

**Criterio de la skill:** las familias (a) y (b) **tienen que correr sin Docker, sin red y
sin ambiente**. Si un test de esas familias necesita algo más, está mal clasificado.

---

## 6. Versiones fijas, nunca comodines

Todas las referencias van con versión exacta. Nada de `4.*` ni `[4.0,)`.

Es `E-NU-03` de `migrar-dotnet`: 9 repos de la flota tienen comodines y su build no es
reproducible [V]. En un proyecto de test es peor, porque produce el peor de los
resultados posibles: **un test que falla un día y pasa al siguiente sin que nadie haya
cambiado nada**, que es como se entrena a un equipo a ignorar el CI.
