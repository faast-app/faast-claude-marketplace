# 02 — Ruta de migración por saltos

**Fase 2 de `migrar-dotnet`.** Leyenda: **[V]** verificado contra los repos de FaaST ·
**[G]** conocimiento general de la plataforma, confirmar en el piloto.

Este documento **no** es la lista completa de breaking changes de Microsoft. Es la
lista de los que **esta flota va a encontrar**, filtrada por lo que los repos
realmente usan. Para la lista completa:
`learn.microsoft.com/dotnet/core/compatibility/<version>`.

---

## 1. El camino

```
netcoreapp3.0 ─┐
netcoreapp3.1 ─┼─▶ net6.0 ──▶ net8.0 ──▶ ${TFM_DESTINO}
net5.0        ─┘
net6.0 ─┐
net7.0 ─┴────────────────▶ net8.0 ──▶ ${TFM_DESTINO}
net8.0 ─┐
net9.0 ─┴──────────────────────────▶ ${TFM_DESTINO}
```

**Por qué escalones y no un salto directo.** Poner `${TFM_DESTINO}` en un
`netcoreapp3.1` compila (a veces) y produce una pila de errores de cuatro saltos
mezclados, sin forma de atribuir cada uno a su causa. Con escalones, cada tanda de
errores tiene un único origen y el changelog de referencia es uno solo.

**Por qué net6 y net8 y no net7.** net7 es STS, murió antes que net6, y no aporta
ningún escalón intermedio útil: todo lo que rompe en net7 rompe igual en net8.

**Cada escalón cierra con:** build limpio + commit propio + anotación en el informe.
El commit intermedio no se despliega nunca. Existe para poder bisecar.

**Excepción a todo lo anterior:** si el origen es net8 o net9, es un solo salto y no
hay escalones que discutir.

---

## 2. Salto A — netcoreapp3.x / net5 ▸ net6

Es el salto más grande de todos, porque es el que cruza el cambio de modelo de hosting
y el cambio de globalización.

| # | Qué cambia | Impacto en la flota | Acción |
|---|---|---|---|
| A1 | `global.json` con SDK viejo bloquea el build | **[V]** `api-integracion-externa` pinea `6.0.412` sin `rollForward` | Poner `rollForward: latestFeature` o actualizar el pin. Plantilla en `templates/global.json` |
| A2 | Modelo de hosting: `Startup` sigue funcionando **[G]** | **[V]** 21 repos con `class Startup` | **No convertir.** Ver `01-analisis-previo` §3.5 |
| A3 | `IHostingEnvironment` / `IApplicationLifetime` obsoletos → `IWebHostEnvironment` / `IHostApplicationLifetime` **[G]** | Poco frecuente | Reemplazo mecánico, warning `CS0618` lo señala |
| A4 | ICU reemplaza a NLS para globalización (desde .NET 5) **[G]** | Alto: toda la flota formatea fechas y montos | Comparación de strings y `ToString()` de fechas pueden cambiar. Ver `03-plan-de-pruebas` §4 |
| A5 | `System.Text.Json` es el serializador por defecto de MVC (ya desde 3.0) | **[V]** 15+ repos con Newtonsoft | Si el componente depende de comportamiento Newtonsoft, mantenerlo **explícito** con `AddNewtonsoftJson()`. Ver E-JSON-01 |
| A6 | EF Core 5 → 6: `TransactionScope`, `Include` filtrado, cambios de traducción **[G]** | **[V]** `micro-cdl-portal-cliente`, `micro-integracion-portal-cliente`, `progreso-api-*` (EF Core 5.0.0) | Ver E-EF-01. Las consultas que antes se evaluaban en cliente ahora lanzan |
| A7 | `Microsoft.Data.SqlClient` 3.x→4.x: **`Encrypt=true` por defecto** **[G]** | **[V]** `micro-reporting` (System.Data.SqlClient 4.8.5), y todo lo que apunta al SQL Server on-prem | **E-SQL-01. Es el error que más tiempo cuesta en esta flota.** Leerlo antes de empezar |
| A8 | Nullable e ImplicitUsings: opcionales | — | **No activar.** Regla 5 de la skill |

**Paquetes que hay que mover en este salto [V]:** `Swashbuckle 5.0.0-rc4 → 6.5.0`,
`Newtonsoft.Json 10/12 → 13.0.3`, `Pomelo 3.x/5.x → 6.0.x`, `NLog.Web.AspNetCore
4.x → 5.x`, `Sentry 2.x → 3.x`.

---

## 3. Salto B — net6 / net7 ▸ net8

| # | Qué cambia | Impacto en la flota | Acción |
|---|---|---|---|
| B1 | `Microsoft.AspNetCore.Authentication.JwtBearer` 8 pasa a **Microsoft.IdentityModel 7.x** **[G]** | **[V]** 7 repos en `System.IdentityModel.Tokens.Jwt 5.6.0` | **E-JWT-01.** Cambia el mapeo de claims y el handler por defecto. Gate de cybersec |
| B2 | EF Core 7 → 8: `DateOnly`/`TimeOnly` nativos, `ExecuteUpdate/Delete`, cambios de traducción de `GroupBy` y de `string` **[G]** | **[V]** ~20 repos en EF Core 7 | E-EF-02. El riesgo no es que falle el build: es que una consulta traduzca distinto |
| B3 | `dotnet publish` y `dotnet pack` pasan a `Release` por defecto en el SDK 8 **[G]** | CI legacy que asume `Debug` | Fijar `-c Release` explícito en los pipelines |
| B4 | `System.Text.Json`: `JsonSerializerOptions` se congela tras el primer uso **[G]** | Código que muta opciones después de serializar | `InvalidOperationException` en runtime, no en build |
| B5 | Contenedores: la imagen `aspnet:8.0` corre como **no-root** por defecto y expone **8080**, no 80 **[G]** | Alineado con el estándar FaaST (R1/R2) | Ya cubierto por `estandar-dockerizacion-faast` §1 |
| B6 | `Sentry` 4.x requiere net6+, 5.x/6.x requiere net8+ **[G]** | **[V]** `Sentry.AspNetCore` va de 2.1.3 a 5.11.0 en la flota | Coordinar con ADR-005/012: puede que la acción sea **quitarlo**, no subirlo |
| B7 | `Ocelot` 17 (net5) → 23/24 **[G]** | **[V]** `gw-crm`, `gw-reporting`, `gw-security` | Usar `gw-contabilidad` (Ocelot 24.0.1 / net8) como referencia viva. Ver E-OC-01 |

---

## 4. Salto C — net8 / net9 ▸ `${TFM_DESTINO}`

Es el salto corto, y aun así tiene los dos cambios más peligrosos para esta flota.

| # | Qué cambia | Impacto | Acción |
|---|---|---|---|
| C1 | **`BinaryFormatter` deja de existir** en .NET 9: no hay paquete de compatibilidad que lo reviva **[G]** | **[V] Cero hallazgos en la flota.** Riesgo nulo | Solo verificar en los repos no clonados |
| C2 | Constructores de `X509Certificate2` obsoletos (`SYSLIB0057`) → `X509CertificateLoader` **[G]** | **[V]** `micro-banco` (6 usos) + componentes con `cert/`: apiauth, operations, ope-ordering, backoffice, monitor-cesiones-hf (SII) | Warning, no error — salvo `TreatWarningsAsErrors`. **Gate de cybersec** |
| C3 | JwtBearer 9/10 usa **Microsoft.IdentityModel 8.x**: `JsonWebTokenHandler` pasa a ser el handler por defecto **[G]** | **[V]** toda la flota con JWT | **E-JWT-02.** El tipo de `HttpContext.User` y el nombre de los claims cambian. Es el error silencioso más caro del salto |
| C4 | EF Core 9/10: cambios de traducción y de `ExecuteUpdate` **[G]** | **[V]** ~30 componentes | E-EF-02, y **el techo de Pomelo**: ver `01-analisis-previo` §2.4 |
| C5 | `Swashbuckle` 6.x sigue funcionando, pero las plantillas oficiales pasaron a `Microsoft.AspNetCore.OpenApi` **[G]** | **[V]** 40+ repos en Swashbuckle 6.x | **No migrar a `Microsoft.AspNetCore.OpenApi` ahora.** Cambia el JSON de OpenAPI generado y eso rompe el snapshot de contrato, que es justamente la red de seguridad |
| C6 | `HttpClient` / `SocketsHttpHandler`: sin `PooledConnectionLifetime`, una IP de backend que cambia no se re-resuelve **[G]** | Alto en el modelo to-be: los micros se van a llamar por IP privada | E-HTTP-01 |
| C7 | Imagen base: `aspnet:10.0` es Debian 13 (trixie) con **OpenSSL 3.x** y `SECLEVEL` estricto **[G]** | Alto contra SQL Server on-prem viejo | **E-TLS-01.** Es el que va a aparecer en el peor momento |

---

## 5. Herramientas

| Herramienta | Para qué sirve de verdad | Cuándo **no** usarla |
|---|---|---|
| `dotnet-upgrade-assistant` | Analizar y proponer el cambio de TFM y de paquetes conocidos | **No aplicar sus cambios en lote.** Está afinado para Framework→Core, que no es el caso de esta flota. Para Core→Core aporta poco más que cambiar el TFM |
| `dotnet outdated` | **Listar** lo que está atrasado | **Nunca `-u`.** Ver §6 |
| `dotnet list package --vulnerable --include-transitive` | Lo mejor del set: encuentra CVEs en transitivas | Ninguna objeción. Correrlo en cada escalón |
| `dotnet list package --deprecated` | Detecta paquetes marcados deprecados en nuget.org | Complementa, no reemplaza, el criterio de "abandonado" (`Hangfire.MySqlStorage` **no** está marcado deprecado y está muerto desde 2019) |
| `Microsoft.DotNet.ApiCompat.Tool` | Comparar superficie pública de un ensamblado antes/después | Útil en librerías (`micro-shared-library`, `faast-telemetry`). Poco valor en una API HTTP: ahí el contrato es OpenAPI, no el ensamblado |
| Analizadores `AnalysisMode=Recommended` + `EnforceCodeStyleInBuild=false` | Sacar a la luz `SYSLIB*` y `CS0618` | Activarlos **al final** del escalón, no al principio: si no, el ruido tapa los errores del salto |
| `git bisect` sobre los commits de escalón | Encontrar en qué salto se rompió el comportamiento | Solo funciona si cada escalón tiene su commit. Por eso la regla |

### Cuándo NO usar automatismos

1. **`dotnet outdated -u` está prohibido en esta flota [V].** Arrastra `AutoMapper`
   11/12/13 → 16.x y `MediatR` 11/12.4.1 → 14.x, y **ambos cambiaron a licencia
   comercial** en sus majors recientes. Un `-u` de rutina convierte una migración
   técnica en un problema de licenciamiento que nadie pidió. Fijar, no actualizar.
2. **No usar un automatismo en un componente sin snapshot de contrato.** El
   automatismo cambia decenas de paquetes a la vez; sin línea base no se puede
   verificar nada de lo que hizo.
3. **No usar el upgrade-assistant en repos con `.sln` multi-proyecto y TFM mixtos**
   (**[V]** `micro-agents-antropic`, `gw-mobile-fintec`): unifica TFM de forma
   agresiva y puede llevarse por delante un proyecto de test que estaba así a propósito.
4. **No correr nada automático sobre versiones flotantes [V].** Primero se fijan
   (los 9 repos de `01-analisis-previo` §2.1), después se automatiza.

---

## 6. Orden de operaciones dentro de un escalón

Siempre el mismo, y el orden es el que hace la diferencia:

1. **Fijar** versiones flotantes a la versión que el restore resuelve hoy.
2. **Subir Newtonsoft a 13.0.3** si está por debajo (seguro, y saca un CVE).
3. **Cambiar el TFM** de todos los `.csproj` del escalón (y de `Directory.Build.props`
   si existe).
4. **Actualizar `global.json`** al SDK del escalón, con `rollForward: latestFeature`.
5. **`dotnet restore`** → resolver `NU1605` / `NU1608` (E-NU-01, E-NU-02).
6. **`dotnet build`** → resolver `CS*`. Los `SYSLIB*`/`CS0618` se **leen y anotan**,
   se arreglan al final.
7. **`dotnet list package --vulnerable --include-transitive`** → registrar.
8. **Actualizar solo los paquetes que el escalón exige** (tabla del salto).
9. **Build limpio + commit del escalón.**
10. Recién acá, siguiente escalón.

**El paso 6 es donde se gana o se pierde tiempo.** La tentación es agregar `NoWarn`
para ver la salida limpia. Cada `NoWarn` agregado en una migración es un error de
runtime programado para dentro de tres semanas, cuando nadie recuerde el contexto.
