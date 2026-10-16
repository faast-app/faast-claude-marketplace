# 01 — Análisis de testabilidad

**Fase 1 de `crear-tests-backend`.** Solo lectura. No se compila, no se ejecuta la app,
no se toca el repo.

El script `templates/analizar-testabilidad.sh` produce los números. Este documento dice
**qué significan** y dónde el script se queda corto.

---

## 1. Mapa del componente

Lo primero es saber qué hay, no cuánto falta.

| Dato | Cómo se obtiene | Para qué sirve |
|---|---|---|
| Nº de controllers y de endpoints por controller | `[Http(Get\|Post\|Put\|Delete\|Patch)]` | Define el tamaño del contrato a caracterizar |
| Endpoints anónimos vs autenticados | `[AllowAnonymous]`, atributos propios de auth | Los anónimos son el punto de entrada barato para el primer test de integración |
| Capas reales | Carpetas `Controllers/`, `Services/`, `Repositories/`, `Interfaces/` | Dónde vive el negocio de verdad (§2) |
| LOC por capa | `git show` + `wc -l` por carpeta | Una capa de repositorios 3× más grande que la de controllers significa que el negocio está en los repositorios, no en los servicios |
| Nº de `DbContext` y su proveedor | `class * : DbContext`, `UseSqlServer`/`UseMySql`/`UseNpgsql` | Cuántos contenedores hace falta levantar, y si son motores distintos |
| Origen del esquema | ¿hay migraciones de EF en el repo, o solo `.sql` sueltos? | **Determina si la integración con Testcontainers es viable** (§5) |

> **Pregunta que el script no contesta y define todo lo demás: ¿dónde está el negocio?**
> En la flota FaaST la respuesta casi nunca es "en los servicios". Suele estar (a) dentro
> del controller, (b) dentro del repositorio mezclado con SQL, o (c) **dentro de un stored
> procedure**, que es el peor caso porque no está en el repo.

---

## 2. Acoplamiento: la pregunta que decide el techo

Para cada pieza de negocio hay que contestar **una** cosa: *¿puedo construirla en un test
sin levantar nada?*

| Patrón encontrado | Testabilidad | Qué se puede hacer |
|---|---|---|
| Clase con constructor que recibe interfaces (`IRepository`, `IMapper`, `IHttpClientFactory`) | **Alta** | Unitario con dobles, hoy |
| Clase `static` **pura** (entra un valor, sale un valor, sin estado) | **Alta** | Unitario directo. Es el mejor retorno por hora de toda la skill |
| Clase `static` que lee configuración o el reloj | **Media** | Testeable, pero el test arrastra un archivo o una variable de entorno. Ver `T-CFG-01` |
| Clase que hace `new HttpClient()` adentro del método | **Baja** | No se puede interceptar sin cambiar el código. Se cubre por integración con WireMock **solo si** hay `IHttpClientFactory`; si no, queda fuera |
| Lógica dentro del `Controller` que llama a `DbContext` directo | **Baja** | Solo por HTTP: `WebApplicationFactory` + base real |
| Lógica dentro de un stored procedure | **Nula desde el repo** | Contrato contra el ambiente, o nada |

**Criterio operativo:** si para probar algo hay que cambiar más de 3 archivos de
producción, no se prueba en esta pasada. Se anota y se sigue. La suite que se escribe hoy
vale más que la suite perfecta que no se escribe.

---

## 3. Inventario de dependencias externas

Por cada una: dónde aparece, cómo se resuelve en un test, y si bloquea el arranque.

| Dependencia | Señal en el código | En unitarios | En integración | ¿Bloquea el arranque? |
|---|---|---|---|---|
| **EF Core + SQL Server** | `UseSqlServer`, `Microsoft.Data.SqlClient` | doble de la interfaz del repositorio | `Testcontainers.MsSql` **si hay esquema**; si no, nada | No (falla al primer request) |
| **EF Core + MySQL (Pomelo)** | `UseMySql`, `ServerVersion.AutoDetect(...)` | idem | `Testcontainers.MySql` | **SÍ con `AutoDetect`** — abre conexión al construir el proveedor (`T-DB-02`) |
| **HTTP a otros servicios** | `new HttpClient()`, `WebRequest.Create`, `IHttpClientFactory` | doble si hay interfaz; nada si es `new` | `WireMock.Net` si hay factory o URL configurable | No |
| **Hangfire (host)** | `AddHangfireServer`, `RecurringJob` | el método del job es una clase normal: **testear el método, no el scheduler** | `Hangfire.MemoryStorage` o deshabilitar el server en test | Sí si no hay storage |
| **SMTP / MailKit** | `SmtpClient`, `MailboxAddress` | **no se testea el envío**: se testea el armado del `MimeMessage` | nada. Jamás un SMTP real | No |
| **S3 / almacenamiento** | `AWSSDK.*`, `IAmazonS3` | doble de la interfaz | MinIO por Testcontainers, si hace falta de verdad | No |
| **JWT** | `JwtSecurityTokenHandler`, `AddJwtBearer` | **sí, y es prioridad 1** | endpoint autenticado con token emitido en el test | Sí si aborta sin clave (y debería) |
| **Sentry / telemetría** | `UseSentry`, `SentrySdk.CaptureException` | sin DSN queda inerte [G] | asegurarse de que el DSN **no** esté definido | No |
| **Reloj** | `DateTime.Now`, `DateTime.Today` | el test no puede fijarlo sin refactor: se **acota** | idem | No |
| **Archivos en disco** | `ContentRootPath + "/..."`, plantillas HTML, `FileServer/` | verificar que el archivo se copia al directorio de salida del test | idem | No, pero rompe el test con `FileNotFound` |
| **Cultura y TZ** | `new CultureInfo("es-XX")`, `InvariantGlobalization` | **sí, y es barato**: es la causa más común de "verde en local, rojo en CI" | idem | No |

---

## 4. Los cinco bloqueadores de `WebApplicationFactory`

Son los que convierten "escribo un test de integración en 20 minutos" en dos días. Hay
que buscarlos **antes** de prometer integración.

### 4.1 `Program` no es accesible desde el proyecto de test

Con minimal hosting y top-level statements, el compilador genera una clase `Program`
**internal**. `WebApplicationFactory<Program>` no compila desde otro ensamblado.

- **Señal:** `Program.cs` sin `class Program` declarada y sin `public partial class Program`.
- **Fix (aditivo, 1 línea):** `public partial class Program { }` al final de `Program.cs`.
- **Alternativa sin tocar `Program.cs`:** `[assembly: InternalsVisibleTo("<Tests>")]` en el
  proyecto de la app — que también es un cambio en el repo, y menos legible.
- Ver `T-WAF-01`.

### 4.2 El arranque abre una conexión a la base

`ServerVersion.AutoDetect(cadena)` de Pomelo **se conecta al MySQL al construir el
`DbContextOptions`**, no al primer query. Sin base accesible, la app no levanta, y
tampoco levanta `WebApplicationFactory`.

- **Señal:** `ServerVersion.AutoDetect(` en `Program.cs`.
- **Consecuencia:** *no hay* test de integración sin un MySQL real (Testcontainers) o sin
  cambiar a `ServerVersion.Parse(...)`.
- Ver `T-DB-02`.

### 4.3 La configuración se lee fuera de `IConfiguration`

Un `new ConfigurationBuilder().AddJsonFile("appsettings.json")` dentro de una clase
estática **ignora las variables de entorno** y lee un archivo relativo al directorio de
trabajo del proceso. En un test, ese directorio es el de salida del test.

- **Síntomas:** `TypeInitializationException`, o `FileNotFoundException: appsettings.json`,
  o —peor— el test pasa leyendo el `appsettings` de otro ambiente.
- **Choca de frente con la regla de la casa "todo el `appsettings` a variables de entorno"**
  (ADR-016 §Paso 4): si la configuración no pasa por `IConfiguration`, ni el contenedor ni
  el test pueden inyectarla.
- Ver `T-CFG-01`.

### 4.4 `UseUrls` / puertos fijos

`WebApplicationFactory` no usa un puerto real (levanta un `TestServer` en memoria), así
que `UseUrls` no rompe el test — **pero sí rompe el contenedor** (`E-RT-02` de
`migrar-dotnet`). Si aparece, se anota para la otra skill.

### 4.5 Middleware que exige infraestructura en el primer request

`UseHttpsRedirection` (307 inesperados), autenticación que consulta un servicio externo,
health checks que consultan la base. Se resuelven en la factory con `ConfigureTestServices`,
no cambiando el código. Ver `T-WAF-02` y `T-WAF-03`.

---

## 5. La pregunta que decide si Testcontainers sirve: **¿de dónde sale el esquema?**

Es el punto donde más planes de test se caen en esta flota.

| Situación en el repo | ¿Testcontainers sirve? | Qué hacer |
|---|---|---|
| Hay **migraciones de EF Core** (`Migrations/`) | **Sí.** `db.Database.Migrate()` en el fixture y listo | Integración completa |
| Hay un **dump de esquema versionado** (`.sql` de estructura, sin datos) | **Sí**, aplicándolo en el fixture | Integración completa. Es el mejor estado alcanzable para un legado |
| El acceso a datos es **LINQ sobre entidades mapeadas** y el esquema se puede derivar | Parcial: `EnsureCreated()` genera un esquema **parecido**, no el real | Sirve para lógica de consulta; **no** para verificar SQL real |
| El acceso a datos es **`FromSqlRaw("EXEC sp_...")`** y los SP **no están en el repo** | **No.** El contenedor arranca vacío y el SP no existe | Queda **contrato contra QA** (familia d) o pedirle al dba un dump de estructura + SPs |

> **`EnsureCreated()` no es el esquema de producción.** Genera tablas a partir del modelo
> de EF: tipos, colaciones, índices y constraints reales pueden no coincidir. Sirve para
> probar *tu* LINQ, no para afirmar que la consulta funciona contra la base real.

---

## 6. Qué mirar además del código

| Fuente | Qué se saca |
|---|---|
| `asis-qa-total-apis-micros.md` | **Quién consume el componente** → qué endpoints entran en la caracterización. No se caracterizan los 108 endpoints: se caracterizan los que alguien llama |
| Logs / accesos del ambiente | Los endpoints realmente usados, cuando el inventario no alcanza |
| `Dockerfile` y workflow | Si agregar proyectos al `.sln` rompe el build de la imagen (`T-DOCK-01`) |
| El `.env` del ambiente (solo nombres) | Las claves que la factory de test tiene que poder inyectar |
| ADR-016 §Paso 4 | La regla "todo el appsettings a variables" que la factory debe respetar |

---

## 7. Salida de la fase

El análisis cierra con **cuatro** cosas escritas, no con una impresión:

1. **Carril** (Verde / Amarillo / Rojo) con su motivo en una línea.
2. **Lista de lo testeable hoy sin tocar código**, con estimación en jornadas.
3. **Lista de cambios de testabilidad** pedidos, con tamaño y riesgo (SKILL §4).
4. **Lista de lo que NO se va a cubrir**, con el motivo. Esta es la más importante: es lo
   que evita que alguien lea "hay tests" y crea que hay red donde no la hay.
