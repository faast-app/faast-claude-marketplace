# 01 — Análisis previo

**Fase 1 de `migrar-dotnet`. Solo lectura: no se compila, no se hace checkout, no se escribe.**

`templates/analisis-previo.sh` automatiza la parte mecánica. Este documento explica
**qué significa cada hallazgo** y cubre lo que un grep no puede contestar.

Leyenda: **[V]** verificado por grep sobre los repos reales de FaaST el 2026-09-21 ·
**[G]** conocimiento general de la plataforma, a confirmar en el piloto.

---

## 1. Inventario de csproj y TFM

### Qué leer

| Dato | Dónde | Trampa |
|---|---|---|
| `<TargetFramework>` | cada `.csproj` | **Nunca** el `FROM` del Dockerfile. 17 repos lo tienen desalineado |
| `<TargetFramework>` en `Directory.Build.props` | raíz o carpeta de solución | Puede contradecir el `.csproj`, y **gana el `.csproj`** |
| `global.json` | raíz | Fija el SDK. Si dice `6.0.412` sin `rollForward`, el build **falla** en una máquina con SDK 10 |
| `<AssemblyName>` | `.csproj` | Es el nombre real del `.dll`. No asumir |
| Ubicación del `.sln` | `git ls-tree` | Afecta el `COPY` del Dockerfile después |

### Lo que la flota tiene hoy **[V]**

| TFM origen | Componentes backend | Saltos hasta `net10.0` |
|---|---|---|
| netcoreapp3.0 | 3 (gw-ordering, gw-portal-cliente, progreso-gw-portal-cliente) | 3 |
| netcoreapp3.1 | 6 (api-cloud, batch_autoatencion, batch_monitor_cesion, micro-autoatencion, micro-operations-ordering, progreso-micro-autoatencion) | 3 |
| net5.0 | 11 (gw-crm, gw-reporting, gw-security, api-background-tasks, micro-cdl-portal-cliente, micro-integracion-portal-cliente, micro-portal-cliente, micro-reporting, progreso-api-cdl, progreso-api-int, progreso-micro-portal-cliente) | 3 |
| net6.0 | 10 (gw-confirming, gw-factoring, api-integracion-externa, micro-authorization, micro-confirming, micro-crm, micro-factoring, micro-hangfire-tasks, micro-ordering, micro-security) | 2 |
| net7.0 | 8 (gw-gestion-cobranza, gw-venta-cartera, api-webhook, micro-banco, micro-buro, micro-contabilidad, micro-gestion-cobranza, micro-operations) | 2 |
| net8.0 | 22 (gw-app, gw-backoffice, gw-contabilidad, gw-mobile-fintec, gw-monitor-cesiones, gw-portal-digital, gw-scoring, micro-agents-antropic, micro-api-back, micro-api-cloud, micro-backoffice, micro-integration-services, micro-monitor-cesiones, micro-monitor-cesiones-hf, micro-notificaciones-hf, micro-notification, micro-portal-digital, micro-reversas, micro-scoring, micro-venta-cartera, micro-versions-manager, xml-to-pdf-api) | 1 |
| net9.0 | 1 (micro-hangfire-tasks-scoring) + `faast-confirming-2.0` | 1 |
| net10.0 | `faast-identidad-y-acceso` (ya está) | 0 |

**Dato que cambia la conversación [V]:** la flota **no tiene .NET Framework**. Se buscó
`TargetFrameworkVersion`, `net4*`, `packages.config`, `Web.config`, `Global.asax`: sin
hallazgos. Todo es .NET Core 3.0+, todo es multiplataforma, y **ninguna migración de
esta flota es una migración de Framework a Core**. Eso elimina la clase de problema
más cara (System.Web, WebForms, AppDomain, GAC) de todo el plan.

### Tres inconsistencias reales encontradas **[V]**

1. **`micro-agents-antropic`**: `Directory.Build.props` declara `net10.0`, los 6
   `.csproj` declaran `net8.0` (y ganan), y el `Dockerfile` usa `sdk/aspnet:10.0`.
   Compila — el SDK 10 construye net8 — pero nadie sabe cuál es el destino. Hay que
   resolverlo antes de migrar, no durante.
2. **`gw-mobile-fintec`**: la app es `net8.0` y **el proyecto de test es `net10.0`**.
   `dotnet test` requiere SDK 10 instalado; en una máquina con SDK 8 el build de la
   solución falla sin relación aparente con la app.
3. **`micro-versions-manager`**: los `.csproj` no declaran TFM; sale de
   `Directory.Build.props` (`net8.0`). El grep ingenuo sobre `*.csproj` devuelve vacío
   y parece un repo sin .NET. **Siempre grepear también `*.props`.**

---

## 2. PackageReferences: versión, compatibilidad, abandono, licencia

### 2.1 Lo primero: versiones flotantes **[V]**

Nueve repos usan comodines (`8.*`, `6.*`, `7.*`, `4.8.*`, `11.*`, `22.*`):
`gw-backoffice`, `gw-scoring`, `micro-backoffice`, `micro-cdl-portal-cliente`,
`micro-monitor-cesiones-hf`, `micro-portal-cliente`, `micro-scoring`,
`progreso-api-cdl`, `progreso-micro-portal-cliente`.

**Se fijan a versión exacta ANTES de empezar el primer salto.** Con un comodín, el
build del escalón 2 puede resolver un paquete distinto al del escalón 1, y el error
que aparece no es del salto: es del comodín. No se puede bisecar una migración con
versiones flotantes.

`micro-scoring` es el peor caso: EF Core, Pomelo, JwtBearer, Swashbuckle e
IdentityModel, todos flotantes.

### 2.2 Paquetes que se caen o cambian con el salto

| Paquete | En la flota **[V]** | Qué pasa | Acción |
|---|---|---|---|
| `System.Data.SqlClient` 4.8.5 | `micro-reporting` | Deprecado por Microsoft, no recibe features | → `Microsoft.Data.SqlClient` **y leer E-SQL-01**: cambia el default de `Encrypt` |
| `MySql.Data` 8.0.18 / 8.0.22 | `gw-backoffice`, `gw-ordering`, `gw-portal-cliente`, `progreso-gw-portal-cliente`, `api-cloud` | Conector de Oracle, versiones de 2019-2020, sin pruebas en runtimes nuevos | → `MySqlConnector` (drop-in) o subir a `MySql.Data` 9.x |
| `Hangfire.MySqlStorage` 2.0.3 | 6 repos | **Última versión 2.0.3, de 2019. Abandonado** — verificado en nuget.org: no hay 2.0.4+ | Ver E-HF-01. No se migra el storage "de paso": es un proyecto propio |
| `Swashbuckle.AspNetCore` **5.0.0-rc4** | `gw-ordering`, `gw-portal-cliente`, `micro-autoatencion`, `micro-operations-ordering`, `micro-portal-cliente`, `progreso-*` | Es una **release candidate de 2019** en producción | → 6.9.x mínimo; 9.x/10.x si se alinea con el TFM destino |
| `System.IdentityModel.Tokens.Jwt` **5.6.0** | 7 repos | 5.x tiene CVEs y el salto a 7/8 cambia el manejo de claims | Ver E-JWT-01 y E-JWT-02. **Gate de cybersec** |
| `Newtonsoft.Json` 10.0.1 / 12.0.3 | 15+ repos | <13.0.1 afecta CVE-2024-21907 (DoS por profundidad) | → 13.0.3 mínimo. Es un cambio seguro y se hace primero |
| `Sentry.AspNetCore` 2.1.3 | `gw-backoffice`, `gw-ordering`, `micro-operations-ordering` | De 2019; Sentry 4.x pide net6+, 5.x/6.x pide net8+ | Coordinar con ADR-005/ADR-012 (reemplazo por OpenTelemetry/GlitchTip): puede ser que **no haya que actualizarlo sino sacarlo** |
| `SkiaSharp` 2.88.x + `QuestPDF` 2023.12.6 | `micro-factoring`, `micro-monitor-cesiones`, `micro-monitor-cesiones-hf` | Van **acoplados**: QuestPDF fija la major de SkiaSharp | Ver E-SKIA-01 — y el hallazgo de abajo |
| `AutoMapper` 11/12/13 + `.Extensions.Microsoft.DependencyInjection` | 12 repos | En v13 el paquete `Extensions` desaparece (se fusiona al core); **v15+ es licencia comercial** | **No actualizar sin decisión de negocio** |
| `MediatR` 11 / 12.4.1 | 10 repos | **v13+ es licencia comercial** | 12.4.1 es la última libre. **Fijar, no actualizar** |
| `Ocelot` 17.0.1 | `gw-crm`, `gw-reporting`, `gw-security` (net5) | 17 es de la era net5; hoy va por 25.x | Ver §2.4 |
| `GemBox.Document` 31.x / 35.x | 7 repos | Licencia comercial por aplicación | Verificar que la clave cubre el destino **antes** de migrar |

### 2.3 El hallazgo que hay que mirar dos veces **[V]**

`micro-monitor-cesiones-hf` declara **`QuestPDF 2023.12.6` junto con
`SkiaSharp.NativeAssets.Linux.NoDependencies 3.119.1`**. QuestPDF 2023.12 está
construido contra la línea SkiaSharp **2.88**; los native assets 3.x publican un
`libSkiaSharp` de otra major. Es una combinación que el restore acepta y el runtime
puede no aceptar.

**Esto no lo introduce la migración: ya está en `develop` hoy.** Verificar en el
ambiente antes de migrar, porque si la generación de PDF ya está rota, la migración
se va a llevar la culpa.

### 2.4 El techo real de MySQL + EF Core **[V]**

Verificado en nuget.org el 2026-09-21:

| Paquete | Última estable | ¿Hay línea 10.x? |
|---|---|---|
| `Microsoft.EntityFrameworkCore` | 10.0.12 | sí |
| `Pomelo.EntityFrameworkCore.MySql` | **9.0.0** | **no, ni preview** |
| `MySql.EntityFrameworkCore` (Oracle) | 10.0.9 | sí |

**~30 componentes de la flota usan Pomelo.** Con `TFM_DESTINO=net10.0` quedan en
`net10` + EF Core 9 + Pomelo 9, que es una combinación **soportada** (una app net10
puede referenciar EF Core 9), pero deja el proveedor de datos en una línea que sigue
el ciclo de .NET 9.

Tres caminos, y **ninguno es decisión de esta skill** (está levantado como decisión
abierta en ADR-017 §7):

1. **Quedarse en Pomelo 9 bajo net10** y esperar Pomelo 10. Es lo que recomienda
   ADR-017: el TFM sube, el proveedor espera. Sin cambio de código.
2. **Cambiar a `MySql.EntityFrameworkCore` de Oracle**. Hay 10.x, pero es otro
   proveedor: difiere en traducción de LINQ, en tipos y en migraciones. Es un cambio
   de riesgo alto que **no** se hace dentro de una migración de runtime.
3. **Salir de EF Core para MySQL** (Dapper + MySqlConnector). Reescritura.

**Importante:** esto aplica **igual a net9 y a net10**. No es un argumento a favor de
ninguno de los dos destinos, es un pendiente propio de MySQL.

### 2.5 Ocelot: hay una referencia interna **[V]**

`gw-contabilidad` ya corre **Ocelot 24.0.1 sobre net8**, con `Swashbuckle 9.0.4` y
`Serilog.AspNetCore 9.0.0`. Es la migración de gateway que ya se hizo en casa.

Los tres gateways en Ocelot 17 (`gw-crm`, `gw-reporting`, `gw-security`) **no se
migran a ciegas**: se toma el `ocelot.json` y el `Program.cs` de `gw-contabilidad`
como referencia del formato actual. Es la diferencia entre leer changelogs de 8
versiones y copiar algo que ya funciona en el mismo ambiente.

---

## 3. APIs obsoletas y usings sospechosos

### 3.1 El falso positivo más caro de este proyecto **[V]**

`asis-repos-legado.md` §4.4 y ADR-016 marcan `System.Drawing` como dependencia nativa
que exige `libgdiplus`, y lo listan como bloqueador en `api-cloud` (28 archivos),
`micro-banco`, `micro-backoffice`, `micro-confirming`, `micro-factoring`,
`micro-ordering` y los gateways `gwSolution`.

Verificación directa sobre los 61 repos backend:

```
Paquete System.Drawing.Common referenciado en algún csproj ....... 0
Uso real de GDI+ (new Bitmap / Graphics.From / Image.From) ....... 0
```

**Los `using System.Drawing;` son huérfanos o usan solo primitivas.** `Color`,
`Point`, `Size` y `Rectangle` viven en `System.Drawing.Primitives`, que es parte del
runtime y funciona perfecto en Linux. Lo que lanza `PlatformNotSupportedException` en
.NET 7+ es el **paquete** `System.Drawing.Common`, que **ningún repo referencia**.

Comprobado en detalle en `micro-banco` (net7, el caso que ADR-016 marca como "confirmar
si el uso es real"): los dos `using System.Drawing` no tienen un solo símbolo GDI+
debajo. Son líneas muertas.

**Consecuencias, que van más allá de esta skill:**
- `libgdiplus` sale de la plantilla D4 del estándar de dockerización.
- `micro-banco` deja de ser un caso dudoso y pasa a ser candidato a piloto.
- Cae uno de los motivos por los que la familia D4 existía.

**El límite de esta verificación:** cubre los repos presentes en
`~/Repositorios`. Los componentes de QA Total cuyo repo **no está clonado localmente**
(`prod-leasing-micro`, `prod-juicios-micro`, `prod_micro_backoffice_ordering`,
`prod-ordencompra-micro`, `prod-bo-micro`) **no fueron verificados**: en esos, el
`System.Drawing` que reporta `asis-qa-total-apis-micros.md` §7 sigue siendo una
hipótesis abierta. Se verifica con el mismo grep cuando se tenga el repo.

### 3.2 `System.Web` **[V]** — tampoco es lo que parece

Aparece en 12 repos. Todos los casos revisados son `using System.Web;` para
`HttpUtility.UrlEncode` / `HtmlDecode`, que en .NET Core vive en el ensamblado
`System.Web.HttpUtility` y **es parte del runtime**. Compila y funciona.

Lo que **sí** sería un bloqueador es `HttpContext.Current`, `System.Web.UI`,
`HttpModule` o `Global.asax`: **cero hallazgos en la flota**. El script lo cuenta por
separado por eso.

### 3.3 Los que sí son bloqueadores reales **[V]**

| Patrón | Dónde | Gravedad |
|---|---|---|
| `System.ServiceModel` (WCF **cliente**) | `micro-portal-cliente` (386), `progreso-micro-portal-cliente` (386), `micro-cdl-portal-cliente` (5), `progreso-api-cdl` (5) | **Media.** Como cliente SOAP funciona en Linux y en runtimes nuevos vía `System.ServiceModel.*` 4.10+/6.x. Los repos lo tienen flotante en `4.8.*`: fijar primero |
| `BinaryFormatter` | **ninguno** | — |
| `AppDomain.CreateDomain` / `Unload` | **ninguno** (los 20 hits de `AppDomain.` son `CurrentDomain.BaseDirectory`, que es válido) | — |
| `System.Runtime.Remoting` | **ninguno** | — |
| EF6 (`PackageReference Include="EntityFramework"`) | **ninguno** | — |
| `DirectoryServices` / LDAP | ninguno de los repos clonados; `asis-qa-total` lo reporta en `QAApiBO` (repo no clonado) | **Alta si se confirma.** `System.DirectoryServices` no es multiplataforma; en Linux hay que usar `Novell.Directory.Ldap` o similar |

**Corrección a `asis-repos-legado.md`:** el inventario atribuye **EF6** a
`micro-backoffice`. No es así: `micro-backoffice` usa `Microsoft.EntityFrameworkCore
8.0.6`. **No hay EF6 en ningún repo de la flota**, lo que elimina el bloqueador más
caro que quedaba.

### 3.4 `UseUrls` — el riesgo R3 de ADR-016, corregido **[V]**

ADR-016 §7.1 R3 dice: *"`UseUrls("http://localhost:…")` hardcodeado […] el contenedor
arranca escuchando en loopback **interno**: el `ProxyPass` recibe conexión rechazada"*.

El código real, en los 5 componentes:

```csharp
// api-cloud/Cloud.Progreso.Api/Program.cs:36  (y sus 4 gemelos)
webBuilder.UseUrls($"http://*:{urlPort}");
```

Bindea a `*`, no a `localhost`, y el puerto sale de configuración. **El síntoma
descrito en el ADR no es el que va a ocurrir.**

El problema real es otro y hay que enunciarlo bien porque el fix es distinto:
**`UseUrls()` tiene mayor precedencia que la variable `ASPNETCORE_URLS`**. El
contenedor va a arrancar escuchando en `urlPort` (7200, 7300…) y va a **ignorar** el
`ASPNETCORE_URLS=http://+:8080` del estándar. El healthcheck contra `:8080` falla, el
contenedor queda `unhealthy` para siempre, y la app está perfecta.

**Fix:** sacar la llamada a `UseUrls` y dejar que `ASPNETCORE_URLS` mande. Si hay que
conservar el comportamiento fuera de contenedor, condicionarlo a que la variable no
esté definida.

Componentes afectados **[V]**: `api-cloud` (3 llamadas), `micro-cdl-portal-cliente`,
`progreso-api-cdl`, `micro-integracion-portal-cliente`, `progreso-api-int`.

### 3.5 `Startup.cs` vs minimal hosting **[V]**

21 repos todavía tienen `class Startup`. **No hay que convertirlos.** El modelo
`Startup` + `IHostBuilder` sigue siendo válido y soportado en net10; `WebApplication.
CreateBuilder` es azúcar, no un requisito.

Convertir a minimal hosting durante una migración de runtime viola la regla 5 de la
skill: cambia el orden de registro de servicios y el orden del pipeline de middleware,
que es exactamente donde viven los bugs difíciles de diagnosticar (E-MW-01).

**Se convierte después, en su propio PR, si hay una razón.** La migración de runtime
no es esa razón.

### 3.6 Certificados X.509 **[G]**, con evidencia de exposición **[V]**

A partir de .NET 9 los constructores de `X509Certificate2` que cargan de archivo o
byte array están **obsoletos** (`SYSLIB0057`) en favor de `X509CertificateLoader`.
Con `TreatWarningsAsErrors` el build falla; sin él, funciona pero queda deuda.

Exposición real en la flota **[V]**: `new X509Certificate2(` aparece en `micro-banco`
(6), y los componentes con carpeta `cert/` montada son `apiauth`, `micro-operations`,
`ope-ordering` y `micro-backoffice`, más los certificados SII de
`micro-monitor-cesiones-hf`. **Todos pasan por el gate de cybersec.**

---

## 4. Lo que el grep no contesta y hay que averiguar

| Pregunta | Cómo se contesta | Por qué bloquea |
|---|---|---|
| ¿La licencia de **GemBox** cubre el destino y el contenedor? | Preguntar a quien administra la licencia | GemBox en modo free trunca documentos **en silencio**: el PDF sale, con menos páginas |
| ¿**QuestPDF** califica para la Community License? | Depende de la facturación de FaaST | QuestPDF Community es gratis bajo cierto umbral de ingresos; arriba requiere licencia |
| ¿El componente está **vivo**? | DNS + tráfico + dueño de negocio | 9 repos sin commits desde 2023-2024. Migrar un muerto es gasto puro |
| ¿Quién lo **consume**? | `asis-qa-total-apis-micros.md` §2-§5 | Define el orden y a quién avisar si algo cambia |
| ¿Tiene **jobs de Hangfire**? ¿contra qué storage? | `.csproj` + `RecurringJob` + la base | Un job que corre dos veces durante la migración es daño en datos de negocio |
| ¿El `appsettings` desplegado tiene claves que el repo no tiene? | `{coordinacion}/env-reales/` (gitignored) o el servidor | El `appsettings` del repo **no** es el desplegado |
| ¿Hay dependencia de un servicio externo **congelado**? | Jasper/SSRS (`micro-reporting`), Softland, Defontana, Cavali | Si el tercero exige TLS viejo o un cliente viejo, el runtime nuevo puede romper la integración (E-TLS-01) |

---

## 5. Salida de la fase: el carril

| Carril | Criterio | Tratamiento |
|---|---|---|
| **Verde** | Origen ≥ net6, sin nativas, sin auth, sin Hangfire, sin bloqueadores, ≤2 saltos | Migración mecánica. Plan de pruebas reducido (§3.7 de `03-plan-de-pruebas`) |
| **Amarillo** | 3 saltos, o nativas, o Hangfire, o auth/crypto, o integración externa congelada | Plan de pruebas completo + gate que corresponda |
| **Rojo** | WCF **servidor**, EF6, `BinaryFormatter`, GDI+ real, LDAP en Linux, o dependencia de un tercero que no soporta el runtime destino | **No es migración.** Se para, se documenta el bloqueador y se escala a la decisión (c) de ADR-016 |

Después de la verificación de §3, **la flota clonada no tiene ningún componente Rojo
por código**. Los candidatos a Rojo que quedan son los repos **no clonados** de QA
Total (`QAApiBO` por LDAP, `microleasing` y `microjuicios` por GemBox + System.Drawing
sin verificar) y cualquier componente cuyo tercero externo no soporte el destino.
