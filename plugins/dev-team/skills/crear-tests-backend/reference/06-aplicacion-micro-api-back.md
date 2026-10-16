# 06 — Aplicación concreta: `micro-api-back` v2.0.33

**Todo lo de este documento se leyó del tag `v2.0.33` con `git show` / `git ls-tree` /
`git grep`, en solo lectura. No se hizo checkout, no se compiló, no se escribió en el repo.**

Complementa `{coordinacion}/inventario/analisis-previo-apiback-net10.md` (si existe en el proyecto) (migración) desde el ángulo de
los tests. Lo marcado **[V]** sale de ese código; **[G]** es conocimiento de plataforma.

---

## 0. Veredicto en cinco líneas

1. **Carril: 🟡 AMARILLO**, con una parte 🔴. Hay un núcleo que se puede testear **hoy,
   sin tocar una línea de producción y sin infraestructura**; y hay una capa de datos que
   **no se puede testear localmente de ninguna forma**, porque el esquema y los stored
   procedures no están en el repo.
2. **El mejor retorno está en `Cloud.Faast.Core`**: 555 líneas [V], estáticas y puras
   (cifrado, formateo, fechas, base64, serialización). Son tests en verde el primer día y
   cubren tres de los cuatro riesgos prioritarios: **cifrado, dinero y fechas**.
3. **La autenticación es testeable con un parche conocido**: `JwtUtils` depende de
   `Variables.ConfiguracionJwt.jwtSecret`, que se lee de un `appsettings.json` por un
   `ConfigurationBuilder` privado [V] (`T-CFG-01`). Con un `appsettings.json` de prueba en
   el directorio de salida, los seis tests de JWT —incluido el **token de oro**— son
   viables. Y el test que **hoy falla** documenta el bug de configuración.
4. **La integración por HTTP necesita un cambio de una línea** (`public partial class
   Program { }`, `T-WAF-01`) y una verificación de 30 minutos sobre el arranque (§3.2).
   Con eso, el **snapshot de OpenAPI corre en CI**, que es la red de seguridad de la
   migración.
5. **El acceso a datos queda fuera** hasta que el dba entregue un dump de estructura
   (`T-DB-04`): **147 líneas de `FromSqlRaw`, casi todas `EXEC sp_...`, y un solo `.sql`
   en todo el repo** [V]. Decirlo ahora ahorra la semana que se perdería descubriéndolo.

---

## 1. El mapa, con números

### 1.1 Superficie

| Dato | Valor [V] |
|---|---|
| Controllers | **24** |
| Endpoints (`[Http*]`) | **106** |
| Documentos OpenAPI publicados | **3 rutas**: `/swagger/BackOffice/swagger.json`, `/swagger/GestionCobranza/swagger.json`, `/webapi/swagger/{doc}/swagger.yaml` (V2) |
| ReDoc | `/documentacion/BackOffice`, `/documentacion/GestionCobranza` |
| Endpoints **anónimos** | **15** (ver §1.4) |
| Healthcheck del contenedor | `/swagger/index.html` (no hay `/health`) |

Controllers con más superficie: `CarteraController` 13, `CarteraGCController` 10,
`MovimientoController` 9, `IndicadoresController` 9, `TareasGCController` 8 [V].

### 1.2 Dónde está el código

| Capa | LOC [V] | Lectura |
|---|---|---|
| `Repositories/` | **12.403** | **Acá está el negocio.** 22 archivos, SQL armado a mano |
| `Controllers/` | 4.960 | Orquestación + try/catch + `Utils.SentryIO` |
| `Services/` | 1.067 | Llamadas HTTP salientes y correo |
| `Contexts/` | 509 | 3 `DbContext` |
| `Common/` | 399 | Incluye `Variables.cs`, el bloqueador de configuración |
| `Authorization/` | 291 | JWT propio: `JwtUtils`, `JwtMiddleware`, atributos propios |
| `Cloud.Faast.Core/` | **555** | `Utils` 216, `Cifrado` 147, `Formater` 145, `SerializaJson` 47 |

**No hay capa de servicios de dominio.** El patrón real es
`Controller → Repository (SQL) → AutoMapper → DTO`. Eso decide la estrategia: no hay
"lógica de negocio pura" que testear en una capa intermedia, salvo la de `Core`.

### 1.3 Acceso a datos

| Contexto | Motor | Dónde |
|---|---|---|
| `Context` | **SQL Server** (`conexion-backoffice`) | La mayoría de los repositorios |
| `ContextFintec` | **MySQL** (`conexion-fintex`) | Gestión de cobranza, operaciones |
| `ContextBuros` | **MySQL** (`conexion-buros`) | Burós |

**151 líneas con `FromSqlRaw`/`ExecuteSql*`, de las cuales 135 contienen `EXEC sp_` o un
nombre `sp_*`, repartidas en 22 repositorios** [V]. El patrón es:

```csharp
string SQL = String.Format("EXEC sp_sel_documentos_cartera '{0}','{1}','{2}',{3},'{4}'", rut, tipo, modulo, negocio, tasaMora);
var dbEntidad = _context.DbDocumentosCartera.FromSqlRaw(SQL).ToList();
```

Dos consecuencias, una de tests y otra que no lo es:

- **De tests:** sin los SPs no hay nada que probar localmente (`T-DB-04`).
- **Que no es de tests:** eso es **concatenación de parámetros dentro de un `EXEC`**. No
  es alcance de esta skill y **no se arregla acá**, pero corresponde levantarlo a cybersec
  como hallazgo aparte, con su propio ticket.

### 1.4 Endpoints anónimos: 15, y 12 de ellos son el controller más grande **[V]**

| Controller | Anónimos / total | Detalle |
|---|---|---|
| `AutenticacionController` | 2 / 2 | `POST /api/oauth/token`, `POST /api/oauth/registrar` — esperable |
| **`CarteraController`** | **12 / 13** | La clase está decorada `[Authorize]`, pero **12 de sus 13 acciones llevan `[AllowAnonymous]`**: `listar-documentos-cartera`, `listar-protestos`, `obtener-cartola-cliente`, `obtener-tipo-cliente`, `validar-documento-cartera`, `listar-deudores-cliente`, … |
| `FactoringWhatsAppController` | 1 / 2 | |

**Para los tests, es una oportunidad:** el contrato del controller más usado se puede
caracterizar **por HTTP y sin token**, que es el camino más barato que hay.

**Para cybersec, es un hallazgo y hay que tratarlo como tal:** a nivel de la aplicación,
consultar cartera, protestos y cartola por RUT **no exige autenticación**. Puede estar
mitigado en el gateway o en la red —no lo verifiqué y no corresponde asumirlo—, pero
queda levantado, con su propio ticket, fuera del alcance de esta skill.

---

## 2. Qué se puede testear hoy, sin tocar nada

### 2.1 `Cloud.Faast.Core` — el primer día

| Clase | Qué testear | Riesgo que cubre |
|---|---|---|
| **`Cifrado`** (147 LOC) | `Encriptar`/`Desencriptar` con **vectores fijos**; ida y vuelta; entrada no-base64 lanza; entrada vacía lanza `ArgumentNullException` | **Cifrado.** Usa `RijndaelManaged` (SYSLIB0022) y `Rfc2898DeriveBytes(string, byte[])` (SYSLIB0060 en net10) [V]: si la derivación cambia, **lo cifrado en base deja de leerse**. Es el test que hay que tener antes de migrar. En uso real en `OperacionGiroRepository` [V] |
| **`Formater`** (145 LOC) | `FormatMonto` con enteros, decimales, negativos y valores grandes; `FormatFecha`; `FormatComillaSimple`; `tipoContenido`/`tipoContenidoExtension` | **Dinero y fechas.** `FormatMonto` hace `Convert.ToDouble(v).ToString().Replace(",", ".")`: **depende de `CurrentCulture`** [V] → `T-CULT-01`. `tipoContenidoExtension("json")` devuelve **`"jsonn"`** [V]: un bug preexistente que el test **congela tal cual**, no arregla |
| **`Utils`** (216 LOC) | `FormatFechaString` (entrada `ddMMyyyy` con y sin separadores), `FormatFechaDateTime`, `EliminarEspaciosVacios`, `ObtenerStringBuscado`, `Base64Decode`/`DecodeBase64ToString`, `Encriptar`/`DesEncriptar` (Unicode+base64) | **Fechas y cultura.** Usa `new CultureInfo("es-CL")` dos veces [V]. Todos los métodos **se tragan las excepciones y devuelven vacío o `null`** [V]: el test documenta ese contrato, que es el que los llamadores asumen |
| **`SerializaJson`** (47 LOC) | `Serialize`, `JsonSerializer<T>`, `JsonDeserialize<T>` con un DTO con `[DataContract]` | **Contrato.** `DataContractJsonSerializer` con `Encoding.Default` [V] |

**Todos son `static` y puros: no necesitan DI, ni base, ni Docker, ni red.**
Estimación: **~40 tests, 1,5 jornadas**, verde el mismo día.

### 2.2 Autenticación — con un `appsettings.json` de prueba

`JwtUtils.GenerateToken` / `ValidateToken` son estáticos y usan
`Variables.ConfiguracionJwt.jwtSecret`, que se resuelve leyendo `appsettings.json` desde
el directorio de trabajo [V]. En un proyecto de test alcanza con copiar un
`appsettings.json` **de prueba** (clave inventada) al output.

| Test | Qué fija | Estado esperado hoy |
|---|---|---|
| `GenerateToken_UsuarioValido_EmiteTokenConClaimsEsperados` | claims `id`, `sub`, `email`, `jti`; alg `HS256`; expiración 1 día | verde |
| `ValidateToken_TokenEmitidoAhora_DevuelveElIdDelUsuario` | el ida y vuelta | verde |
| **`ValidateToken_TokenDeOro_SigueSiendoValido`** | un token **emitido con el runtime actual**, guardado como constante | **verde hoy; es EL test de la migración** |
| `ValidateToken_TokenFirmadoConOtraClave_DevuelveNull` | validación de firma viva | verde |
| `ValidateToken_TokenExpirado_DevuelveNull` | `ClockSkew = TimeSpan.Zero` [V] | verde |
| `ValidateToken_TokenNulo_DevuelveNull` | contrato del método | verde |
| `GenerateToken_SinClaveConfigurada_Aborta` | la regla de ADR-016 §3.5 | **rojo hoy**: no aborta. Queda `[Skip]` con motivo + hallazgo para cybersec |

**El token de oro hay que generarlo antes de migrar**, con el binario actual, y guardarlo
en el repo de tests como constante. Vence en 24 h por diseño (`Expires = UtcNow.AddDays(1)`)
[V], así que el test de validación completa usa un token generado en el test, y el de oro
se acota a **estructura y firma**, no a vigencia. Ese detalle está en la plantilla.

> **Gate de cybersec obligatorio** sobre esta sección (regla dura 8), y sobre dos
> hallazgos preexistentes que los tests van a dejar por escrito: `ValidateIssuer=false`,
> `ValidateAudience=false` [V], y la clave por `Encoding.ASCII.GetBytes` [V].

### 2.3 Contrato OpenAPI

El snapshot de los 3 documentos es lo que reemplaza al `snapshot-contrato.sh` manual y lo
mete en CI. Necesita que la app **arranque** bajo `WebApplicationFactory` → §3.

**Normalización obligatoria:** `info.version` sale de `version.txt`, que **sube en cada
PR** por regla del repo [V]. Sin quitarlo, el test falla en cada entrega (`T-SNAP-02`).

---

## 3. Los bloqueadores, en orden de costo

### 3.1 `T-WAF-01` — `Program` no es accesible (1 línea)

`Program.cs` es top-level sin `public partial class Program` [V]. Sin eso no hay
`WebApplicationFactory<Program>` y no hay ningún test por HTTP.

**Pedido:** agregar `public partial class Program { }` al final. Aditivo, sin efecto en
runtime, sin cambio de pipeline. Es el único cambio de producción que esta skill pide
para `micro-api-back`.

### 3.2 `T-DB-02` — el arranque y MySQL: **contradicción a resolver primero**

`Program.cs` configura dos contextos con `ServerVersion.AutoDetect(conex...)` [V].

- El análisis de migración lo reporta como **"abre conexión a MySQL al arrancar: sin BD
  accesible el servicio no levanta"** (`analisis-previo-apiback-net10.md` §2.5).
- Leyendo el código, la llamada está **dentro de la lambda de opciones** de
  `AddDbContext`, que EF Core evalúa al construir las opciones del contexto —lo que
  normalmente ocurre **al resolver el `DbContext` por primera vez**, no en el arranque [G].

**Las dos lecturas llevan a planes distintos**, así que se resuelve antes de estimar nada
más: **el primer test de integración es la prueba** — levantar la factory sin ninguna base
y pedir `/swagger/BackOffice/swagger.json`.

| Resultado | Consecuencia |
|---|---|
| Responde 200 | **El snapshot de OpenAPI corre en CI sin Docker.** Y hay que corregir §2.5 del análisis de migración |
| Falla al arrancar | El snapshot necesita un MySQL vacío por Testcontainers (solo para satisfacer `AutoDetect`), o el cambio a `ServerVersion.Parse` |

Media jornada, y es lo primero que hay que hacer.

### 3.3 `T-CFG-01` — la configuración estática

`Common/Variables.cs`: **20 claves** leídas con `new ConfigurationBuilder().AddJsonFile(...)`
en campos estáticos [V]. Las variables de entorno **no surten efecto**.

- Para los tests: se parchea copiando un `appsettings.json` de prueba.
- Para la regla de la casa ("todo el appsettings a variables de entorno"): **no se puede
  cumplir** hasta que entre `Variables.Initialize(IConfiguration)`, que **ya existe en
  `release/faast/stage`** [V].
- **Test que se escribe igual, marcado `[Skip]` con motivo:** definir
  `AppSettings__JwtSecret` por variable de entorno y verificar que el token se firma con
  esa clave. Se quita el `Skip` el día que entre el fix. Es la forma de que la deuda
  quede en el CI y no en un documento.

### 3.4 `T-WAF-03` — `JwtMiddleware` consulta SQL Server

`JwtMiddleware` llama a `IUserRepository.ObtenerUsuario` contra `Context` cuando hay
token [V]. **Sin token no consulta**: los endpoints anónimos y las rutas de Swagger se
pueden probar sin ninguna base. Para probar un endpoint autenticado sin base, se sustituye
`IUserRepository` por un doble en `ConfigureTestServices`.

### 3.5 `T-DB-04` — el esquema no está en el repo (**el bloqueador caro**)

Un solo `.sql` en todo el repo (`Scripts/Migrations/sp_sel_indicadores_cartera_operacion_v2.sql`)
frente a decenas de `EXEC sp_...` [V]. **Testcontainers con SQL Server no sirve para
nada** mientras no exista un dump de estructura.

**Lo que hay que pedirle al dba:** dump de **estructura** (tablas, vistas y **stored
procedures**, sin datos) de la base de `conexion-backoffice` y de los dos MySQL, en un
`.sql` versionable **sin credenciales ni datos de clientes**. Con eso, la integración real
pasa a ser viable y esta misma skill la cubre sin cambios.

**Mientras tanto:** familia (d), contrato contra QA en solo lectura, fuera del CI.

### 3.6 `T-DOCK-01` — agregar tests al `.sln` rompe la imagen

El `Dockerfile` de `release/faast/stage` copia solo los dos `.csproj` de la app y hace
`dotnet restore Cloud.Faast.Back/Cloud.Faast.Back.sln` [V]. Al agregar proyectos de test
al `.sln`, **el build de la imagen falla con `MSB3202`**.

**Fix propuesto (1 línea, va con la suite):** restaurar el `.csproj` de la app en vez de
la solución. Requiere ojo de infra, porque toca el `Dockerfile` de un componente que ya
está desplegado en Stage y Puente.

---

## 4. El plan, priorizado

| # | Bloque | Qué entra | Infra | Riesgo que cubre | Jornadas |
|---|---|---|---|---|---|
| **0** | **Verificación de arranque** (§3.2) | Un test que levanta la factory y pide `/swagger/BackOffice/swagger.json` | — | Decide todo lo demás | **0,5** |
| **1** | Andamiaje | `tests/`, 4 `.csproj`, `Directory.Build.props`, `.gitignore`, `coverage.runsettings`, workflow | — | — | **0,5** |
| **2** | **`Cloud.Faast.Core`** | ~40 tests: `Cifrado` (vectores), `Formater` (montos/fechas), `Utils` (parseo es-CL, base64), `SerializaJson` | — | **cifrado, dinero, fechas** | **1,5** |
| **3** | **JWT** | 6 tests + **token de oro** + el `[Skip]` de config por env | — | **auth** | **1,0** |
| **4** | **Contrato OpenAPI** | Snapshot de los 3 documentos, normalizado | según §3.2 | **contrato** | **0,5** |
| **5** | Cultura y TZ | Suite corrida con `TZ=UTC` y `es-CL`; caso de monto y de fecha | — | fechas/TZ en contenedor | **0,5** |
| **6** | Integración HTTP mínima | `POST /api/oauth/token` con `IUserRepository` doblado: 200 con credenciales válidas, 401 con inválidas; un endpoint autenticado devolviendo 401 sin token; y **los anónimos de `CarteraController` (§1.4) con el repositorio doblado**, que dan forma de respuesta sin base | — | auth por el camino real + forma del contrato | **1,0** |
| **7** | **Contrato contra QA** (familia d) | `GET` de los endpoints consumidos, línea base antes de migrar. Fuera del CI | ambiente QA | regresión funcional | **1,5** |
| **8** | CI | Workflow, gate de 0 tests, gate de `.verified.`, publicación de resultados | — | que todo lo anterior no se pudra | **0,5** |
| — | **Total** | | | | **~7,5 jornadas** |

**Fuera de alcance hasta que haya dump de estructura:** repositorios, SQL, cualquier
endpoint que consulte datos reales. Es la mayor parte de las 12.403 líneas de
`Repositories/`, y hay que decirlo con todas las letras en el informe.

### 4.1 Qué endpoints entran en el contrato (propuesta, a confirmar)

No se caracterizan los 108. La lista sale de `asis-qa-total-apis-micros.md` §4.2 (quién
consume a quién) y de los logs del ambiente. **Propuesta de arranque**, a validar con
el responsable de plataforma y QA:

| Grupo | Endpoints | Por qué |
|---|---|---|
| Auth | `POST /api/oauth/token` | Todo lo demás depende de él |
| Cartera | `GET /api/v2/interface/listar-documentos-cartera/{rut}/{tipo}/{modulo}`, `listar-protestos/{rut}`, `obtener-cartola-cliente/{rut}`, `obtener-tipo-cliente/{rut}/{negocio}` | El controller más grande y el que usa el backoffice |
| Indicadores | `GET /api/v1/indicadores/obtener-cartera`, `obtener-cartera-detalle`, `obtener-cartera-cuentas` | Dinero en pantalla |
| Movimiento contable | `GET listar-contabilidad-nubox`, `exportar-contabilidad-nubox` | **Dinero + Excel + `System.Drawing` transitivo por EPPlus**: el punto más frágil de la migración |
| Core / Integración | `GET /api/v2/core/obtener-parametros`, `/api/v2/integracion/obtener-volumen-operacional` | Baratos, consumidos por otros micros |

Los dos de Excel merecen su propio golden-file **binario** (tamaño y primeras celdas), no
solo el status: es donde `EPPlus.Core` y `System.Drawing.Common` transitivo pueden fallar
en Linux sin lanzar excepción [G].

---

## 5. Orden respecto de la migración a net10

```
  HOY  ──▶ (0) verificar arranque          medio día, decide el resto
       ──▶ (1)(2)(3)(5) tests en net8       sin tocar producción, salvo T-WAF-01
       ──▶ (4)(6) contrato + integración    ← PR de tests, mergeado
       ──▶ (7) línea base contra QA         antes del primer commit de migración
  ────────────────────────────────────────────────────────────────────────────
       ──▶ MIGRACIÓN net8 → net10           skill migrar-dotnet, 13 commits
           · los tests NO se editan
           · sube el <TargetFramework> del .csproj de test en el MISMO commit
             que el de la app (E-CS-03)
  ────────────────────────────────────────────────────────────────────────────
       ──▶ los MISMOS tests verdes en net10 ← el DoD de la migración
       ──▶ DOCKERIZACIÓN                    skill dockerizar-componente
```

**Por qué en `micro-api-back` los tests van antes y no después:** el análisis de migración
ya identificó los cinco puntos de mayor riesgo del salto —JWT/IdentityModel 8, EF Core 9 +
Pomelo 9, MailKit 4, Swashbuckle (contrato) y EPPlus en Linux—. De esos cinco, **los tests
cubren tres directamente** (JWT, contrato, y cifrado/fechas que viajan con todo), y un
cuarto por golden-file binario (Excel). Escribirlos después de migrar los convierte en
descripción del sistema nuevo: no sirven para nada.

**Lo que los tests NO van a cubrir de esa migración**, y por lo tanto sigue dependiendo del
smoke contra el ambiente: EF Core 9 + Pomelo 9 (traducción LINQ contra la base real) y
MailKit 4 (TLS contra el SMTP real). Son exactamente los dos que necesitan infraestructura
que hoy no está disponible localmente.

---

## 6. Lo que hay que pedir para que esto avance

| # | Quién | Qué |
|---|---|---|
| 1 | **Responsable de plataforma / lead** | Aprobar el cambio de 1 línea `public partial class Program { }` (`T-WAF-01`) |
| 2 | **Responsable de plataforma / lead** | Confirmar que la suite se escribe sobre `v2.0.33` / `develop_docker_net10` y no sobre `release/faast/stage` — es la misma pregunta P1 del análisis de migración, y cambia si `Variables.Initialize` ya está disponible |
| 3 | **dba** | Dump de **estructura** (tablas + SPs, sin datos) de las 3 bases. Sin eso no hay integración real, hoy ni después |
| 4 | **infra** | Confirmar si el runner de CI tiene Docker; y revisar el cambio de `Dockerfile` de `T-DOCK-01` |
| 5 | **QA** | Validar la lista de endpoints del contrato (§4.1): QA sabe cuáles se usan de verdad |
| 6 | **cybersec** | Gate sobre los tests de JWT y cifrado, y **tres** hallazgos preexistentes que la suite va a dejar por escrito: (a) `ValidateIssuer/Audience=false` [V]; (b) el `EXEC` con parámetros concatenados en los repositorios [V]; (c) **12 de los 13 endpoints de `CarteraController` son `[AllowAnonymous]`** [V] (§1.4). Ninguno se arregla en esta skill: se levantan con ticket propio |
| 7 | **backend** | Media jornada para el bloque (0), que desbloquea la estimación del resto |
