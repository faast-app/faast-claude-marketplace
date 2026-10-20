# 04 — Catálogo de errores al crear tests

**Fase 5-6 de `crear-tests-backend`.** Cada entrada tiene código citable en un handoff:
*"la integración de `micro-api-back` está bloqueada por `T-DB-02` + `T-DB-04`"*.

**Leyenda:** **[V]** verificado por lectura del código real o comando ejecutado ·
**[G]** conocimiento general de la plataforma, a confirmar en el piloto.

**Regla:** si el error que tenés enfrente no está acá, se agrega cuando se resuelve, con
su verificación. Igual que en `migrar-dotnet`.

---

## A. Arranque de la app en un test

### T-WAF-01 · `WebApplicationFactory<Program>`: `Program` inaccesible **[V] en `micro-api-back`**

| | |
|---|---|
| **Síntoma** | `CS0122: 'Program' is inaccessible due to its protection level`, o `CS0246: no se encuentra el tipo 'Program'` en el proyecto de test |
| **Causa** | Con minimal hosting y top-level statements, el compilador genera una clase `Program` **internal**. `WebApplicationFactory<T>` necesita un `T` visible desde el ensamblado de test |
| **Exposición real [V]** | `micro-api-back` `v2.0.33`: `Program.cs` es top-level, sin `class Program` declarada |
| **Fix** | `public partial class Program { }` al final de `Program.cs`. Es aditivo: no cambia el pipeline, no cambia el orden del middleware, no cambia nada en runtime |
| **Alternativa** | `[assembly: InternalsVisibleTo("<Proyecto>.Tests.Integracion")]` en la app. También toca el repo y es menos evidente para el que lee |
| **Verificación** | El proyecto de test compila y `factory.CreateClient()` devuelve un cliente |
| **Qué NO hacer** | Copiar `Program.cs` al proyecto de test "para poder instanciarlo". Deja dos pipelines que divergen en la primera semana |

### T-WAF-02 · Todo responde 307 en los tests **[G]**

| | |
|---|---|
| **Síntoma** | Cada request del `TestServer` devuelve `307 Temporary Redirect` |
| **Causa** | `app.UseHttpsRedirection()` sin puerto HTTPS conocido en el host de test |
| **Fix** | En la factory: `builder.UseSetting("https_port", "443")`, o cliente con `AllowAutoRedirect = false` y aserción sobre el 307, o quitar el middleware solo en el entorno de test vía `ConfigureTestServices`. **No se toca `Program.cs`** |
| **Verificación** | Un `GET` a un endpoint anónimo devuelve 200 |

### T-WAF-03 · El pipeline de auth necesita la base en cada request **[V] en `micro-api-back`**

| | |
|---|---|
| **Síntoma** | Todos los tests de integración fallan con error de conexión, incluso los de endpoints `[AllowAnonymous]` |
| **Causa** | Un middleware propio que corre **antes** de la autorización y consulta un repositorio. En `micro-api-back`, `JwtMiddleware` llama a `userService.ObtenerUsuario(...)` contra `Context` (SQL Server) en **cada** request donde hay token [V] |
| **Fix** | Si el test no manda token, el middleware no consulta: los endpoints anónimos se pueden probar **sin base**. Para los autenticados: contenedor real, o sustituir `IUserRepository` por un doble en `ConfigureTestServices` |
| **Verificación** | Un endpoint anónimo responde 200 sin ninguna base levantada |

### T-WAF-04 · La factory no toma la configuración **[G]**

| | |
|---|---|
| **Síntoma** | La app de test arranca con los valores del `appsettings.json` del repo, no con los del test |
| **Causa** | Se configuró con `ConfigureAppConfiguration` **después** de que el host ya leyó, o se usó `UseSetting` para claves anidadas con el separador equivocado |
| **Fix** | Variables de entorno con `Seccion__Clave` (doble guion bajo **solo** en la variable; en el código siempre `Seccion:Clave`), fijadas **antes** de `CreateClient()`. Es lo que hace `templates/FaastWebApplicationFactory.cs` |
| **Verificación** | Un endpoint que devuelva algo derivado de la configuración refleja el valor del test |

---

## B. Configuración

### T-CFG-01 · Configuración estática leída fuera de `IConfiguration` **[V] en `micro-api-back`**

| | |
|---|---|
| **Síntoma** | `TypeInitializationException` envolviendo un `FileNotFoundException: appsettings.json`, disparado en el primer test que toca cualquier cosa. El mensaje **no** apunta a la configuración |
| **Causa** | Un `static` inicializado con `new ConfigurationBuilder().AddJsonFile("appsettings.json").Build()`. Se ejecuta la primera vez que se toca la clase, lee un archivo relativo al directorio de trabajo del proceso de test, e **ignora las variables de entorno** |
| **Exposición real [V]** | `micro-api-back` `v2.0.33`, `Common/Variables.cs`: **20 claves** (`JwtSecret`, `Pais`, `SMTP__*`, `CRM__*`, `Contabilidad__*`, `Hangfire__*`, `FINANZAS__*`, `Integraciones__Peru__Cavali__*`) se leen así. `JwtUtils` depende de una de ellas |
| **Fix (test)** | Copiar un `appsettings.json` de **prueba** al directorio de salida del test (`CopyToOutputDirectory`), con valores ficticios. Es un parche, y hay que decir que lo es |
| **Fix (real)** | `Variables.Initialize(IConfiguration)` — el cambio que **ya existe en `release/faast/stage`** [V, `{coordinacion}/inventario/analisis-previo-apiback-net10.md` (si existe en el proyecto) §8.2]. Hasta que entre, la regla de la casa "todo el appsettings a variables de entorno" **no se puede cumplir ni verificar** |
| **Verificación** | Un test define `AppSettings__JwtSecret` como variable de entorno y el token se firma con esa clave. **Hoy ese test falla**, y eso es exactamente lo que debe documentar |
| **Qué NO hacer** | Poner un `JwtSecret` real en el `appsettings` de test. Regla dura 4 |

### T-CFG-02 · Archivos de runtime que el test no encuentra **[V] en `micro-api-back`**

| | |
|---|---|
| **Síntoma** | `FileNotFoundException` sobre `version.txt`, una plantilla HTML o una carpeta de exportación |
| **Causa** | La app los lee desde `AppContext.BaseDirectory` o `ContentRootPath`. En un test, ese directorio es `bin/Debug/<tfm>/` del **proyecto de test** |
| **Exposición real [V]** | `micro-api-back` lee `version.txt` en `Program.cs` al arrancar, y `TemplateEmail/*.html` y `FileServer/ExportacionFiles/` en runtime |
| **Fix** | `<Content Include="..." CopyToOutputDirectory="PreserveNewest" Link="..."/>` en el `.csproj` de test, o `WithWebHostBuilder(b => b.UseContentRoot(rutaDelProyectoDeLaApp))` |
| **Verificación** | La factory arranca y el endpoint que usa el archivo responde |

---

## C. Base de datos

### T-DB-01 · `FromSqlRaw` no funciona con EF InMemory **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | `InvalidOperationException` al ejecutar cualquier repositorio bajo el proveedor InMemory |
| **Causa** | InMemory no es un motor relacional: no traduce ni ejecuta SQL |
| **Exposición real [V]** | `micro-api-back`: **~147 líneas con `FromSqlRaw`/`ExecuteSql*` en 22 repositorios**, la mayoría `EXEC sp_...` |
| **Fix** | No usar InMemory (`02-estrategia` §4.3). Motor real por Testcontainers, o doble de la interfaz del repositorio |
| **Verificación** | — |

### T-DB-02 · `ServerVersion.AutoDetect` conecta a MySQL antes de cualquier query · exposición **[V]**, efecto **[G]**

| | |
|---|---|
| **Síntoma** | `WebApplicationFactory` no llega a devolver un cliente, o el primer request contra cualquier endpoint muere con timeout / `MySqlException`, sin haber tocado datos |
| **Causa** | `ServerVersion.AutoDetect(cadena)` de Pomelo **abre una conexión** para descubrir la versión del servidor |
| **Exposición real [V]** | `micro-api-back` `Program.cs`: dos llamadas (`conexBuro`, `conexFintec`) |
| **Cuándo ocurre — punto a verificar [G]** | La llamada está **dentro de la lambda de opciones** de `AddDbContext`, que EF Core evalúa **al resolver el `DbContext` por primera vez**, no necesariamente en el arranque. `analisis-previo-apiback-net10.md` §2.5 lo reporta como bloqueo de arranque. **Se resuelve con un test de 30 minutos** (`06-aplicacion` §3.2): levantar la factory sin ninguna base y pedir un endpoint que no use datos. El fix es el mismo en los dos casos; lo que cambia es si el snapshot de OpenAPI necesita Docker o no |
| **Fix (test)** | Levantar MySQL con Testcontainers y apuntar la cadena al contenedor **antes** de construir la factory |
| **Fix (código, a decidir)** | `ServerVersion.Parse("8.0.x-mysql")` cuando la variable esté declarada. Es un cambio de arranque: va con su propio test y su propia aprobación (SKILL §4) |
| **Verificación** | La factory arranca con la red de salida cortada y con los contenedores arriba |

### T-DB-03 · SQLite pasa y el motor real falla **[G]**

| | |
|---|---|
| **Síntoma** | La suite verde en local, el endpoint roto en QA |
| **Causa** | SQLite no tiene los tipos, colaciones ni funciones del motor real. `decimal`, `datetime2`, `NVARCHAR` vs `VARCHAR`, `dbo.`, comparación de strings sensible a acento |
| **Fix** | SQLite solo para lógica de consulta LINQ. Todo lo que dependa del motor, con Testcontainers o nada. Y la conexión SQLite in-memory se mantiene **abierta** mientras dure la suite, o la base se borra sola |
| **Verificación** | Los tests que afirman algo del motor están en la suite de integración, no en la de unitarios |

### T-DB-04 · El contenedor arranca vacío: el esquema no está en el repo **[V] en `micro-api-back`**

| | |
|---|---|
| **Síntoma** | `Invalid object name 'sp_sel_...'` / `Table doesn't exist` contra un contenedor recién levantado |
| **Causa** | El componente consulta tablas y stored procedures que **no existen en el repositorio**: no hay migraciones de EF ni dump de estructura |
| **Exposición real [V]** | `micro-api-back` `v2.0.33`: un único `.sql` en el repo (`Scripts/Migrations/sp_sel_indicadores_cartera_operacion_v2.sql`) frente a decenas de `EXEC sp_...` |
| **Fix** | Pedir al **dba** un dump de **estructura** (tablas + SPs, sin datos) para poder sembrar el contenedor. Hasta que exista, la familia de integración con base **no es viable**: queda contrato contra QA |
| **Verificación** | El fixture aplica el dump y un `SELECT 1` sobre una tabla real responde |
| **Qué NO hacer** | Copiar datos de un ambiente real al repo para sembrar. Regla dura 4 |

### T-DB-05 · Los tests se pisan entre ellos **[G]**

| | |
|---|---|
| **Síntoma** | Pasan de a uno, fallan todos juntos; o el resultado depende del orden |
| **Causa** | Comparten base y nadie limpia |
| **Fix** | Un `IClassFixture` por suite con su propia base, o `Respawn` entre tests, o transacción con rollback. Y **jamás** un contenedor por test |
| **Verificación** | La suite completa pasa dos veces seguidas sin recrear nada |

---

## D. Tiempo, cultura y zona horaria

### T-TIME-01 · `DateTime.Now` hace el test no determinista **[V] exposición**

| | |
|---|---|
| **Síntoma** | Un test que pasa siempre menos a fin de mes, o a las 00:00, o en el runner (UTC) y no en la máquina (Lima/Santiago) |
| **Causa** | El código toma la hora del sistema y el test compara contra un valor fijo |
| **Exposición real [V]** | `micro-api-back`: **31 usos de `DateTime.Now` en 18 archivos**, cero `UtcNow` en ese conjunto |
| **Fix, en orden** | 1) No afirmar el valor exacto: afirmar el **formato** y un rango (`fecha >= inicioDelTest && fecha <= DateTime.Now`). 2) Si el valor exacto importa, el test declara la TZ y la fija. 3) Inyectar `TimeProvider` **es refactor**: no entra en el PR de tests (SKILL §4) |
| **Verificación** | La suite corre verde con `TZ=UTC` y con `TZ=America/Santiago` |
| **Regla relacionada** | Regla dura 7: ningún `DateTime.Now` **dentro** del test |

### T-CULT-01 · Verde en la máquina, rojo en el runner (o al revés) **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | Una aserción sobre `"1.234,56"` falla en CI devolviendo `"1234.56"` |
| **Causa** | `ToString()` sin cultura usa `CurrentCulture`. En la máquina es `es-CL`; en el contenedor del runner es invariante |
| **Exposición real [V]** | `micro-api-back` `Core/Formater.FormatMonto` hace `Convert.ToDouble(valor).ToString().Replace(",", ".")`: **el resultado depende de la cultura del proceso**. Y `Core/Utils` usa `new CultureInfo("es-CL")` dos veces |
| **Fix** | El test **declara** la cultura que ejercita (`CultureInfo.CurrentCulture = new CultureInfo("es-CL")` en el arranque de la suite, o un atributo propio). Nunca depender de la del host |
| **Verificación** | La suite pasa con `DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=0` y con la cultura del host cambiada |
| **Ojo** | Si el componente tiene `InvariantGlobalization=true`, `new CultureInfo("es-CL")` **lanza** (`E-CULT-01`). Es un test que vale por sí solo |

---

## E. Snapshots y golden files

### T-SNAP-01 · El snapshot se regeneró durante la migración **[G]**

| | |
|---|---|
| **Síntoma** | La suite pasa en el TFM nuevo, y nadie puede explicar por qué el `.verified.` cambió |
| **Causa** | Alguien aceptó el `.received.` para poner el verde |
| **Fix** | Regla dura 2. En el PR de migración, **cualquier cambio en un archivo `.verified.*` bloquea**. El CI lo verifica (`ci-tests.yml`) |
| **Verificación** | `git diff` del PR de migración no toca ningún `.verified.` |
| **Por qué importa** | Regenerar el snapshot durante la migración convierte la red de seguridad en un adorno, y lo hace en silencio |

### T-SNAP-02 · El snapshot de OpenAPI cambia en cada release **[V] exposición**

| | |
|---|---|
| **Síntoma** | El test falla en cada PR por `info.version` |
| **Causa** | La versión del documento sale de un archivo que sube en cada entrega |
| **Exposición real [V]** | `micro-api-back` arma `OpenApiInfo.Version` leyendo `version.txt`, y la regla del repo obliga a subirlo en cada PR |
| **Fix** | Normalizar antes de comparar: quitar `info.version` y cualquier timestamp. Es lo que hace `CaracterizacionOpenApiTests.cs` |
| **Verificación** | Dos corridas con `version.txt` distinto producen el mismo `.verified.` |

### T-SNAP-03 · Los archivos `.received.` terminan commiteados **[G]**

| | |
|---|---|
| **Síntoma** | Aparecen `*.received.*` en el repo |
| **Fix** | `*.received.*` en el `.gitignore` del proyecto de test. Viene en la plantilla |

---

## F. Infraestructura de test

### T-TC-01 · Testcontainers no arranca **[G]**

| | |
|---|---|
| **Síntoma** | `Docker is either not running or misconfigured`, o timeout esperando el contenedor |
| **Causas** | Docker apagado; el runner no tiene Docker; en macOS el socket no está en la ruta por defecto (Docker Desktop / Colima / Rancher) |
| **Fix** | Local: `DOCKER_HOST` apuntando al socket correcto. CI: si el runner no tiene Docker, la suite de integración **se declara como gap**, no se borra ni se ignora |
| **Verificación** | `docker ps` responde y el fixture levanta en una corrida limpia |

### T-TC-02 · La suite de integración tarda minutos **[G]**

| | |
|---|---|
| **Síntoma** | El CI pasa de 2 a 15 minutos y la gente deja de esperar el verde |
| **Causa** | Un contenedor por clase (o peor, por test). La imagen de SQL Server es pesada y su arranque no es inmediato |
| **Fix** | Un solo contenedor por suite (`ICollectionFixture`), reutilizado; limpieza entre tests con `Respawn` o transacción |
| **Verificación** | La suite de integración completa termina en un tiempo que alguien está dispuesto a esperar |

### T-DOCK-01 · Agregar tests al `.sln` rompe el build de la imagen **[V] en `micro-api-back`**

| | |
|---|---|
| **Síntoma** | La imagen deja de construir con `MSB3202: The project file ... was not found`, señalando el `.csproj` **de tests** |
| **Causa** | El `Dockerfile` copia **solo los `.csproj` de la app** y después hace `dotnet restore <solución>`. Al sumar proyectos al `.sln`, el restore busca archivos que no se copiaron |
| **Exposición real [V]** | `micro-api-back`, rama `release/faast/stage`: `COPY` de `Cloud.Faast.Back.sln` + los dos `.csproj` de la app, y `RUN dotnet restore Cloud.Faast.Back/Cloud.Faast.Back.sln` |
| **Fix recomendado** | Cambiar el restore de la imagen a **el `.csproj` de la app** (`dotnet restore .../Cloud.Faast.Back.csproj`): una línea, arrastra igual su `ProjectReference`, y la imagen deja de depender de la forma de la solución |
| **Alternativas** | Copiar también los `.csproj` de test (la imagen restaura paquetes de test que no usa) o mantener una solución aparte para tests (`dotnet test` necesita saber cuál) |
| **Verificación** | `docker build` local verde **con** los proyectos de test ya agregados al `.sln` |
| **Por qué está acá** | Es el efecto colateral más probable de esta skill sobre la dockerización, y aparece días después, en el CI de otra rama |

---

## G. CI

### T-CI-01 · `dotnet test` verde sin ejecutar un solo test **[V] en `micro-api-back`**

| | |
|---|---|
| **Síntoma** | El CI dice "tests OK" y nadie escribió tests |
| **Causa** | `dotnet test` sobre una solución sin proyectos de test **no falla**: no hay nada que correr |
| **Exposición real [V]** | `CI.yml` de `develop_docker` en `micro-api-back` corre `dotnet test` y pasa en vacío |
| **Fix** | El workflow **cuenta los tests ejecutados** y falla si son 0. Está en `templates/ci-tests.yml` |
| **Verificación** | Borrar temporalmente un proyecto de test hace fallar el pipeline |
| **Por qué es el peor del catálogo** | Es la única falla que **genera confianza falsa**. Un CI rojo se arregla; un CI verde mentiroso se cree |

### T-CI-02 · xUnit v3 sin `OutputType Exe`: 0 tests descubiertos **[G]**

| | |
|---|---|
| **Síntoma** | Compila, corre, no descubre tests. Verde |
| **Causa** | Un proyecto `xunit.v3` necesita ser ejecutable |
| **Fix** | `<OutputType>Exe</OutputType>`, o quedarse en xUnit v2 (recomendación de `03-stack` §2.3) |
| **Verificación** | El conteo del reporte es > 0 (mismo gate que `T-CI-01`) |

### T-COV-01 · La cobertura sale 0% **[G]**

| | |
|---|---|
| **Síntoma** | El reporte existe y dice 0%, o no se genera |
| **Causas** | Falta `coverlet.collector` en el proyecto de test; se usó `--no-build` con artefactos de otra configuración; el formato pedido no coincide con el que espera el reporter |
| **Fix** | `coverlet.collector` como `PrivateAssets="all"`, `dotnet test --collect:"XPlat Code Coverage" --settings coverage.runsettings` |
| **Verificación** | El `cobertura.xml` tiene líneas cubiertas > 0 para un módulo que sí se ejercita |

---

## H. Seguridad y datos

### T-SEC-01 · Secretos o datos reales dentro de los tests **[G]**

| | |
|---|---|
| **Síntoma** | Un `JwtSecret`, una cadena de conexión, un RUT real o un correo de cliente en un archivo de test |
| **Causa** | Copiar de un `appsettings` real para que "funcione" |
| **Fix** | Claves generadas en el test; RUT y nombres inventados (o `Bogus`); el ambiente se configura por variables de entorno que no se versionan. Lo que necesita un valor real **se saltea con motivo** |
| **Verificación** | Búsqueda de patrones de secreto sobre `tests/` antes de abrir el PR, y revisión de cybersec si el componente hace auth |
| **Antecedente [V]** | `micro-api-back` ya tiene `appsettings` versionados **con connection strings reales** (`analisis-previo-apiback-net10.md` §0.5). Los tests no pueden repetir ese error |

### T-SEC-02 · Un test apuntó a un ambiente que no era QA **[G]**

| | |
|---|---|
| **Síntoma** | Registros de prueba en Puente, Demo o producción de cliente. En el mejor caso, ruido; en el peor, plata |
| **Causa** | Una URL base por defecto en el código del test, o una variable de entorno heredada de otra corrida |
| **Fix** | Regla dura 5. La suite de contrato **no tiene URL por defecto**: sin variable, se saltea. Y **solo `GET`** — la plantilla no expone otro verbo |
| **Verificación** | Correr la suite de contrato sin variables definidas: todo salteado, cero requests |

---

## I. Inestabilidad

### T-FLAKE-01 · Tests que fallan de a ratos por estado compartido **[G]**

| | |
|---|---|
| **Síntoma** | Falla uno distinto en cada corrida; en solitario pasan todos |
| **Causa** | xUnit corre clases **en paralelo**. Estado estático (configuración, caché, `CurrentCulture`, variables de entorno) se comparte entre ellas |
| **Fix** | Una `[Collection]` para las clases que tocan estado global; o fijar cultura/variables una vez, en un fixture de colección, y no cambiarlas por test |
| **Verificación** | La suite pasa 3 veces seguidas y también con paralelismo desactivado |
| **Relación** | En componentes con configuración estática (`T-CFG-01`) esto es **seguro**, no probable |

### T-FLAKE-02 · Dependencia de red **[G]**

| | |
|---|---|
| **Síntoma** | Falla cuando el VPN está caído, cuando el tercero está lento, o a las 6 de la tarde |
| **Causa** | Un test de las familias (a)/(b) sale a internet |
| **Fix** | Correr la suite con la red cortada: lo que falla está mal clasificado y se mueve a (c) o (d) |
| **Verificación** | `dotnet test` verde sin red |

### T-FLAKE-03 · Orden y `async` **[G]**

| | |
|---|---|
| **Síntoma** | Resultados distintos según el orden; tests que terminan antes que la operación que dispararon |
| **Causa** | Un `async void`, un `.Result`, o un fire-and-forget del código en prueba |
| **Fix** | Todo test asíncrono devuelve `Task`. El fire-and-forget del código de producción **no se testea así**: se testea el método que se dispara |

---

## J. Observabilidad y jobs

### T-OBS-01 · La telemetría se activa durante los tests **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | Errores de test apareciendo en Sentry/GlitchTip; ruido en el proyecto del ambiente; latencia en cada test |
| **Causa** | El DSN quedó definido en el entorno del runner o en el `appsettings` de test |
| **Exposición real [V]** | `micro-api-back` llama a `SentrySdk.CaptureException` desde `Utils.SentryIO` en **225 sitios**, y `Program.cs` hace `UseSentry()` |
| **Fix** | La factory de test **no define ningún DSN** y lo borra si viene del entorno. Sin DSN, el SDK queda inerte [G] |
| **Verificación** | Provocar un error en un test y confirmar que no aparece ningún evento en el proyecto del ambiente |

### T-HF-01 · Hangfire ejecuta jobs durante los tests **[G]**

| | |
|---|---|
| **Síntoma** | Efectos reales (correos, asientos, archivos) disparados por una corrida de tests. O tests que cuelgan esperando un storage |
| **Causa** | La app registra el **servidor** de Hangfire en el arranque, y el test lo levanta con ella |
| **Fix** | En `ConfigureTestServices`: no registrar el servidor (solo el cliente), o `Hangfire.MemoryStorage`. **El job se testea llamando a su método**, no dejando que el scheduler lo dispare |
| **Verificación** | Durante la suite, cero filas nuevas en `HangFire.Server` del storage real |
| **Precedente** | `E-HF-02` de `migrar-dotnet`: dos instancias contra el mismo storage = trabajo duplicado con daño en datos |

---

## K. Cómo se agrega una entrada

1. Código nuevo en la familia que corresponda.
2. **Síntoma literal**, como aparece en consola, para que se encuentre con Ctrl+F.
3. Causa real, no la primera hipótesis.
4. Fix, y **qué NO hacer** si había un atajo tentador.
5. **Verificación**: cómo se comprueba que el fix funcionó. Sin esto, la entrada no sirve.
6. Marca **[V]** con el repo y el archivo donde se verificó.
