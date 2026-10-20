# 04 — Catálogo de errores

**Fase 4 de `migrar-dotnet`.** Cada entrada tiene código para poder citarla en un
handoff sin reexplicarla: *"`micro-factoring` quedó bloqueado en E-SKIA-01"*.

**Leyenda de confianza:**

| Marca | Significa |
|---|---|
| **[V]** | La **exposición está verificada** por grep sobre los repos reales de FaaST el 2026-09-21. El repo/paquete/versión que se nombra existe |
| **[G]** | Conocimiento general de la plataforma. El mecanismo es estándar; **el fix no fue ejecutado en este ambiente**. Confirmar en el piloto y volver a marcarlo [V] |

**Regla:** si el error que tenés enfrente no está acá, se agrega cuando se resuelve.

---

## A. Restore y NuGet

### E-NU-01 · `NU1605: Detected package downgrade` **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | El restore falla (o advierte) diciendo que el proyecto A pide `X 9.0.0` y el proyecto B lo baja a `8.0.0` |
| **Causa** | Dos proyectos de la misma solución quedaron en escalones distintos, o una transitiva trae una major mayor que la directa |
| **Exposición real [V]** | `micro-integration-services` (net8) referencia **EF Core 9.0.0** y **Pomelo 9.0.0**; `micro-notification` (net8) idem. El paquete va por delante del TFM: al mover el TFM, el árbol se reacomoda |
| **Fix** | Subir el TFM de **todos** los proyectos de la solución en el mismo escalón. Nunca escalonar por proyecto dentro de un mismo `.sln`. Si persiste, declarar la versión explícitamente en el proyecto que la baja |
| **Verificación** | `dotnet restore` sin warnings NU1605 y `dotnet list package --include-transitive` mostrando una sola versión de cada paquete |
| **Qué NO hacer** | `<NoWarn>NU1605</NoWarn>`. El downgrade sigue ahí y explota en runtime como `MissingMethodException` (E-RT-01) |

### E-NU-02 · `NU1608: version conflict detected` **[G]**

| | |
|---|---|
| **Síntoma** | Un paquete resuelve a una versión mayor que la que otro declara como dependencia |
| **Causa** | Familias que van acopladas y se movieron a destiempo (EF Core + proveedor, Hangfire core + storage, SkiaSharp + QuestPDF) |
| **Fix** | Mover la familia completa en un solo paso, no paquete por paquete |
| **Verificación** | Restore limpio + el runtime arranca y ejercita la funcionalidad de esa familia |

### E-NU-03 · Restore no reproducible por versión flotante **[V]**

| | |
|---|---|
| **Síntoma** | El build de ayer resolvió otra versión que el de hoy. Un error aparece y desaparece sin cambios en el código |
| **Exposición real [V]** | 9 repos con comodines: `gw-backoffice` (`8.0.*`), `gw-scoring` (`11.*`, `8.*`, `6.*`), `micro-backoffice`, `micro-scoring` (EF, Pomelo, Swashbuckle, JWT **todos** flotantes), `micro-monitor-cesiones-hf` (`22.*`), `micro-cdl-portal-cliente`, `micro-portal-cliente`, `progreso-api-cdl`, `progreso-micro-portal-cliente` (`4.8.*`) |
| **Fix** | Fijar a la versión exacta que el restore resuelve **hoy**, en un commit propio, **antes** del primer escalón |
| **Verificación** | `dotnet restore --locked-mode` con `packages.lock.json`, o dos restores en máquinas distintas resolviendo igual |

### E-NU-04 · `NU1701: restored using .NETFramework` **[G]**

| | |
|---|---|
| **Síntoma** | Warning de que un paquete se restauró usando un TFM que no es el del proyecto |
| **Causa** | Paquete viejo sin target para el TFM nuevo. Típico en los abandonados |
| **Exposición esperada [V]** | `Hangfire.MySqlStorage 2.0.3` (2019), `Swashbuckle 5.0.0-rc4` (2019), `Sentry.AspNetCore 2.1.3` (2019) |
| **Fix** | Verificar que el paquete realmente funciona en el TFM destino. Si es abandonado, ver E-HF-01 |
| **Verificación** | No alcanza con que compile: hay que **ejercitar la funcionalidad** del paquete en el runtime destino |

### E-NU-05 · SDK no encontrado / `global.json` bloquea **[V]**

| | |
|---|---|
| **Síntoma** | `A compatible .NET SDK was not found` o el build usa un SDK viejo sin explicación |
| **Exposición real [V]** | `api-integracion-externa` pinea `6.0.412` **sin `rollForward`**; `gw-app`, `micro-monitor-cesiones-hf`, `micro-notificaciones-hf` pinean `8.0.415` con `latestFeature`; `micro-versions-manager` pinea `8.0.0` |
| **Fix** | `templates/global.json` con `"rollForward": "latestFeature"` y el pin del escalón |
| **Verificación** | `dotnet --version` dentro del directorio del repo devuelve el SDK esperado |

---

## B. Compilación

### E-CS-01 · `CS0618` / `SYSLIB*`: API obsoleta **[G]**

| | |
|---|---|
| **Síntoma** | Warnings nuevos tras cambiar el TFM |
| **Causa** | Es el mecanismo por el que la plataforma avisa qué va a desaparecer |
| **Fix** | Leer cada uno, anotarlo en el informe, y arreglarlo **al final del escalón** |
| **Verificación** | El conteo de warnings del informe baja o queda justificado |
| **Qué NO hacer** | `NoWarn`. Regla 7 de la skill |

### E-CS-02 · `SYSLIB0057`: `X509Certificate2` obsoleto **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | Warning (o error con `TreatWarningsAsErrors`) al cargar un `.pfx`/`.cer` desde archivo o bytes |
| **Causa** | Desde .NET 9 esos constructores están obsoletos en favor de `X509CertificateLoader` |
| **Exposición real [V]** | `micro-banco` (6 usos de `new X509Certificate2(`); componentes con carpeta `cert/` montada: `apiauth`, `micro-operations`, `ope-ordering`, `micro-backoffice`; certificados SII en `micro-monitor-cesiones-hf` |
| **Fix** | `X509CertificateLoader.LoadPkcs12FromFile(...)` / `LoadCertificate(...)` |
| **Verificación** | El componente firma/valida un token o se conecta al tercero con el certificado real, **no** un certificado de prueba |
| **Gate** | **cybersec** antes de cerrar |

### E-CS-03 · El proyecto de test no compila y arrastra la solución **[V]**

| | |
|---|---|
| **Síntoma** | `dotnet build` de la solución falla en un proyecto que no es la app |
| **Exposición real [V]** | `gw-mobile-fintec`: app `net8.0`, proyecto de test `net10.0` |
| **Fix** | Alinear el TFM del test al escalón de la app |
| **Verificación** | `dotnet build` de la solución completa, no solo del proyecto de la API |

---

## C. Runtime y binding

### E-RT-01 · `MissingMethodException` / `TypeLoadException` al arrancar **[G]**

| | |
|---|---|
| **Síntoma** | Compila perfecto, revienta al arrancar o al ejecutar la primera ruta que usa el paquete |
| **Causa** | Casi siempre un `NU1605` silenciado: el ensamblado cargado no es el que se compiló |
| **Fix** | Volver a E-NU-01 y resolver el downgrade de verdad |
| **Verificación** | `dotnet publish` y revisar el `.deps.json`: una sola versión del ensamblado |

### E-RT-02 · `UseUrls` pisa `ASPNETCORE_URLS` **[V]**

| | |
|---|---|
| **Síntoma** | En contenedor: el healthcheck contra `:8080` falla siempre, el contenedor queda `unhealthy`, `docker logs` muestra `Now listening on: http://*:7200` y la app está perfecta |
| **Causa** | `UseUrls()` tiene **mayor precedencia** que la variable de entorno |
| **Exposición real [V]** | `api-cloud` (3 llamadas), `micro-cdl-portal-cliente`, `progreso-api-cdl`, `micro-integracion-portal-cliente`, `progreso-api-int`. El código real es `webBuilder.UseUrls($"http://*:{urlPort}")` — **no** `localhost`, como dice ADR-016 §7.1 R3 |
| **Fix** | Quitar la llamada y dejar mandar a `ASPNETCORE_URLS`. Si hace falta conservar el comportamiento fuera del contenedor, condicionarla a que la variable no esté definida |
| **Verificación** | `docker logs` dice `Now listening on: http://[::]:8080` y el healthcheck pasa |

### E-RT-03 · `Could not resolve assembly` en Hangfire **[V]** (lección propia)

| | |
|---|---|
| **Síntoma** | Jobs que fallan mudos o el dashboard mostrando trabajos de otro servicio |
| **Causa** | Dos servicios distintos compartiendo la **misma base de storage** de Hangfire: cada uno intenta deserializar los jobs del otro |
| **Exposición real** | Lección `hangfire-contab-demo-cl`; riesgo R1 de ADR-016 (copias net8 ociosas en `.10`) |
| **Fix** | Una base de storage **por servicio** y una réplica **por base y ambiente** |
| **Verificación** | `SELECT * FROM HangFire.Server` muestra **una** instancia |

---

## D. Entity Framework Core

### E-EF-01 · Una consulta que antes funcionaba ahora lanza `InvalidOperationException: could not be translated` **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | Error en runtime en un endpoint concreto, tras el salto |
| **Causa** | EF Core dejó de evaluar en cliente lo que no puede traducir; ahora lanza |
| **Exposición real [V]** | EF Core 5.0.0 en `micro-cdl-portal-cliente`, `micro-integracion-portal-cliente`, `progreso-api-cdl`, `progreso-api-int`; EF Core 3.1.0 en `api-cloud` |
| **Fix** | Materializar antes del método no traducible (`.ToList()` explícito, consciente de cuántas filas trae) |
| **Verificación** | El endpoint responde **y** el conteo de filas coincide con la versión anterior |

### E-EF-02 · La consulta funciona pero devuelve otro resultado o tarda 100× **[G]**

| | |
|---|---|
| **Síntoma** | Sin error. Números distintos en un reporte, o un timeout |
| **Causa** | Cambió la traducción a SQL: `GroupBy`, `Skip/Take`, `Include` filtrado, `string.Contains`, `DISTINCT` implícito |
| **Fix** | Diff del SQL generado antes/después (`ToQueryString()` o log de `Microsoft.EntityFrameworkCore.Database.Command`) |
| **Verificación** | Conteo de filas idéntico **y** tiempo del mismo orden de magnitud. Ver `03-plan-de-pruebas` §5.3 |
| **Por qué importa** | Es el error más peligroso del catálogo: **no falla, miente** |

### E-EF-03 · Techo de Pomelo: no hay proveedor MySQL para EF Core 10 **[V]**

| | |
|---|---|
| **Síntoma** | No hay error: hay un paquete que no existe. `Pomelo.EntityFrameworkCore.MySql` no tiene línea 10.x ni preview (verificado en nuget.org, 2026-09-21; última estable **9.0.0**) |
| **Exposición real [V]** | ~30 componentes usan Pomelo |
| **Fix recomendado** | TFM a `${TFM_DESTINO}` y **quedarse en EF Core 9 + Pomelo 9**. Es una combinación soportada: una app net10 puede referenciar EF Core 9 |
| **Alternativas** | `MySql.EntityFrameworkCore` de Oracle (sí tiene 10.0.9) — **es otro proveedor**, cambia traducción LINQ y migraciones: no se hace dentro de una migración de runtime. O salir de EF Core (Dapper + MySqlConnector): reescritura |
| **Verificación** | `dotnet list package` muestra EF Core 9.x coherente en toda la solución, y el humo de datos pasa |
| **Nota** | Aplica **igual a net9 y a net10**. No es argumento para elegir destino; es un pendiente propio de MySQL. Levantado como decisión abierta en ADR-017 §7 |

---

## E. Serialización JSON

### E-JSON-01 · Las respuestas cambian de forma sin que nadie tocara un DTO **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | El front deja de encontrar un campo; un consumidor recibe `null` donde había valor. Casing distinto, enums que cambian de número a string, fechas con otro offset |
| **Causa** | Se dejó de configurar Newtonsoft explícitamente y MVC cayó en `System.Text.Json` |
| **Exposición real [V]** | 15+ repos con Newtonsoft; `micro-factoring` (83 referencias), `progreso-api-cdl` (79), `micro-portal-cliente`/`progreso-micro-portal-cliente` (386 de WCF + Newtonsoft), `api-cloud` (154) |
| **Fix** | Si hoy usa Newtonsoft, **sigue** usando Newtonsoft: `AddControllers().AddNewtonsoftJson()` explícito, con las mismas `JsonSerializerSettings` |
| **Verificación** | Diff de respuestas byte a byte contra la línea base (`comparar-respuestas.sh`) |

### E-JSON-02 · `InvalidOperationException: JsonSerializerOptions ... can't be modified` **[G]**

| | |
|---|---|
| **Síntoma** | Excepción en runtime tras la primera serialización |
| **Causa** | Desde .NET 8 las opciones se congelan al primer uso |
| **Fix** | Construir las opciones una sola vez en el arranque; no mutarlas por request |
| **Verificación** | El endpoint que serializa responde en la segunda llamada, no solo en la primera |

### E-JSON-03 · CVE de Newtonsoft < 13.0.1 **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | `dotnet list package --vulnerable` lo reporta |
| **Exposición real [V]** | `api-webhook` y `micro-banco` en **10.0.1**; ~12 repos en 12.0.3 |
| **Fix** | Subir a 13.0.3. Es de los pocos cambios seguros: se hace en el paso 2 de cada escalón |
| **Verificación** | `--vulnerable` limpio y el diff de respuestas sin cambios |

---

## F. Cultura, fechas y zona horaria

### E-CULT-01 · `CultureNotFoundException` en un contenedor que "no cambió nada" **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | `Culture is not supported... PredefinedCulturesOnly` al formatear un monto o parsear una fecha |
| **Causa** | `InvariantGlobalization=true` en el csproj, o `DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1` en la imagen (típico en Alpine, que no trae ICU) |
| **Exposición real [V]** | 6 repos con la bandera en `true`: `gw-confirming`, `gw-portal-digital`, `gw-venta-cartera`, `micro-banco`, `micro-portal-digital`, `micro-venta-cartera`. Revisados: **hoy ninguno crea culturas concretas** — `micro-portal-digital` usa 40 veces `CultureInfo.InvariantCulture`, que es consistente. **No hay bug hoy; hay una bomba armada** |
| **Fix** | O se quita la bandera (la imagen Debian del estándar FaaST **sí** trae ICU), o se documenta que ese componente es invariante y no se le agregan culturas |
| **Verificación** | Formatear un monto en `es-PE` y parsear una fecha `dd/MM/yyyy` desde un request real |
| **Relación con Docker** | `estandar-dockerizacion-faast` ya prohíbe Alpine para la familia D4. Esta es otra razón para no usar Alpine en **ninguna** familia .NET |

### E-CULT-02 · Un monto o una fecha salen distintos **[G]**

| | |
|---|---|
| **Síntoma** | `1,234.56` donde había `1.234,56`. Nadie tocó el código |
| **Causa** | ICU reemplazó a NLS desde .NET 5; y la cultura del contenedor no es la del servidor |
| **Fix** | Formateo **explícito** con la cultura pretendida, no implícito con `CurrentCulture` |
| **Verificación** | Caso de monto y caso de fecha en el diff de respuestas |

### E-TZ-01 · Las fechas se corren 5 horas **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | Registros con la hora corrida, jobs que corren a destiempo |
| **Causa** | El contenedor arranca en **UTC**; el servidor PM2 estaba en `America/Lima` (verificado en los 4 servidores de QA Total) |
| **Exposición real [V]** | `DateTime.Now` usado ampliamente — 30 veces solo en `micro-banco` |
| **Fix** | `ENV TZ=America/Lima` en el Dockerfile (ya está en la familia D6 del estándar) **y** asegurarse de que la imagen tenga `tzdata`. Las imágenes `-alpine` y las `chiseled` **no lo traen** |
| **Verificación** | `docker exec <c> date` devuelve hora de Lima, y un registro creado por la app tiene el timestamp correcto en la base |

### E-TZ-02 · `TimeZoneNotFoundException: America/Lima` **[G]**

| | |
|---|---|
| **Síntoma** | Excepción al llamar `TimeZoneInfo.FindSystemTimeZoneById` |
| **Causa** | Falta `tzdata` en la imagen, o se usa el id de Windows (`SA Pacific Standard Time`) en Linux |
| **Fix** | Instalar `tzdata`; usar ids IANA. Desde .NET 6 hay conversión automática entre ids, pero no si falta la base de datos |
| **Verificación** | El endpoint que usa zonas horarias responde |

---

## G. HTTP, cookies, CORS, middleware

### E-HTTP-01 · El componente sigue llamando a una IP vieja **[G]**

| | |
|---|---|
| **Síntoma** | Tras mover un backend de servidor, el consumidor sigue yendo al anterior hasta que se reinicia |
| **Causa** | `SocketsHttpHandler` cachea conexiones y no re-resuelve DNS sin `PooledConnectionLifetime` |
| **Por qué importa acá** | El modelo to-be de ADR-016 §3.3 hace que los gateways llamen a los micros por **IP privada**, y el puente de vhost mueve componentes de servidor. Es el escenario exacto |
| **Fix** | `PooledConnectionLifetime = TimeSpan.FromMinutes(2)` en el handler de `IHttpClientFactory` |
| **Verificación** | Cambiar el destino y confirmar que el consumidor lo toma **sin reiniciarlo** |

### E-HTTP-02 · `SocketException` / `Connection refused` desde el gateway **[G]**

| | |
|---|---|
| **Síntoma** | El gateway no llega al micro |
| **Causa** | Tres sospechosos en orden: E-RT-02 (`UseUrls`), el bind del compose, el Security Group |
| **Fix** | Descartar en ese orden: `docker logs` (¿en qué puerto escucha?) → `docker ps` (¿qué publica?) → `curl` desde el host destino |
| **Verificación** | `curl` por el camino real (vhost), no directo al contenedor |

### E-COOKIE-01 · La sesión deja de persistir en el navegador **[G]**

| | |
|---|---|
| **Síntoma** | Login que no queda, cookie que no se guarda |
| **Causa** | `SameSite`: el default cambió con las políticas de los navegadores; `SameSite=None` exige `Secure=true` |
| **Exposición** | `gw-portal-digital` tiene `AuthCookie` en configuración |
| **Fix** | Declarar `SameSite` y `SecurePolicy` explícitamente |
| **Verificación** | Login real en el navegador con **captura de pantalla** (regla de la casa) |

### E-CORS-01 · `InvalidOperationException` al arrancar por política de CORS **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | Falla al construir el pipeline, o preflight que empieza a fallar |
| **Causa** | `AllowAnyOrigin()` junto con `AllowCredentials()` no está permitido |
| **Exposición real [V]** | `AllowAnyOrigin` aparece en varios gateways; los fronts hoy tienen **3 modelos de CORS distintos** (ADR-016 ola 4) |
| **Fix** | Orígenes explícitos cuando hay credenciales |
| **Verificación** | Preflight `OPTIONS` desde el origen real del front |

### E-MW-01 · 401/403 donde antes había 200 **[G]**

| | |
|---|---|
| **Síntoma** | Autorización que empieza a rechazar, o middleware que deja de ejecutarse |
| **Causa** | Cambió el orden del pipeline. `UseAuthentication` debe ir antes de `UseAuthorization`, y ambos después de `UseRouting`. Al convertir `Startup` a minimal hosting el orden se reescribe sin querer |
| **Fix** | **No convertir `Startup` durante la migración** (regla 5, y `01-analisis-previo` §3.5). Si ya se convirtió, comparar el orden línea por línea contra el original |
| **Verificación** | Un endpoint anónimo, uno autenticado y uno con rol insuficiente: 200 / 200 / 403 |

---

## H. Autenticación y JWT

### E-JWT-01 · Los claims cambian de nombre y la autorización por rol deja de funcionar **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | `User.Identity.Name` en `null`, `[Authorize(Roles="X")]` que rechaza, claims con URIs largas (`http://schemas.microsoft.com/ws/2008/06/identity/claims/role`) o al revés |
| **Causa** | JwtBearer 8+ pasa a Microsoft.IdentityModel 7.x y cambia el mapeo de claims inbound |
| **Exposición real [V]** | 7 repos en `System.IdentityModel.Tokens.Jwt` **5.6.0** (`gw-backoffice`, `gw-ordering`, `gw-portal-cliente`, `micro-autoatencion`, `micro-operations-ordering`, `micro-portal-cliente`, `progreso-*`). Ya hay referencias modernas en casa: `gw-portal-digital` 8.14.0, `micro-integration-services` 8.17.0 |
| **Fix** | Declarar explícitamente `MapInboundClaims`, `NameClaimType` y `RoleClaimType` en `TokenValidationParameters`. **No** dejarlo al default |
| **Verificación** | Volcar los claims de un token real antes y después y compararlos. Probar un endpoint por rol |
| **Gate** | **cybersec, obligatorio** |

### E-JWT-02 · `JsonWebTokenHandler` reemplaza a `JwtSecurityTokenHandler` **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | Código que hace *cast* a `JwtSecurityToken` lanza `InvalidCastException`; handlers propios dejan de invocarse |
| **Causa** | Microsoft.IdentityModel 8.x (que arrastra JwtBearer 9/10) cambia el handler por defecto |
| **Exposición real [V]** | `JwtSecurityTokenHandler` usado explícitamente en `micro-banco` y otros |
| **Fix** | Migrar a `JsonWebToken`/`JsonWebTokenHandler`, o registrar explícitamente el handler viejo mientras dure la transición |
| **Verificación** | Emisión + validación de un token real, y un token **expirado** que debe ser rechazado |
| **Gate** | **cybersec** |

### E-JWT-03 · Arranca sin clave de firma **[V]** (regla de la casa)

| | |
|---|---|
| **Síntoma** | El componente arranca "bien" pero valida cualquier token, o firma con una clave vacía |
| **Causa** | Fallback silencioso cuando la variable no está mapeada. Al pasar de `appsettings` a variables de entorno, es el error más fácil de cometer |
| **Fix** | **Abortar el arranque** si falta la clave. Prohibido el fallback. Ya es regla dura de ADR-016 §3.5 y del estándar |
| **Verificación** | Levantar el componente **sin** la variable: debe morir con mensaje claro, no arrancar |
| **Gate** | **cybersec** |

---

## I. Swagger / OpenAPI

### E-SWAG-01 · El JSON de OpenAPI cambia y el diff de contrato se vuelve inútil **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | Cientos de líneas de diff en el snapshot sin que ningún endpoint haya cambiado |
| **Causa** | Se cambió de generador (Swashbuckle → `Microsoft.AspNetCore.OpenApi`) o se saltó de Swashbuckle 5/6 a 9/10 en el mismo paso que el runtime |
| **Exposición real [V]** | 40+ repos en Swashbuckle 6.x; 6 repos en **5.0.0-rc4**; `gw-contabilidad` ya en 9.0.4 |
| **Fix** | **No cambiar de generador durante la migración.** Subir Swashbuckle lo mínimo para que compile, y dejar el salto grande para un PR propio |
| **Verificación** | El diff de OpenAPI muestra solo ruido conocido (`info.version`, orden de claves) |

### E-SWAG-02 · Swagger UI devuelve 404 y el healthcheck se cae con él **[V]**

| | |
|---|---|
| **Síntoma** | Contenedor `unhealthy` |
| **Causa** | Varios componentes usan `/swagger/index.html` como endpoint de healthcheck (así lo hace `micro-api-back`), y el path cambió o Swagger quedó deshabilitado en `Production` |
| **Fix** | Verificar el path real; idealmente exponer un `/health` propio y anotarlo como pendiente |
| **Verificación** | `curl -f` al endpoint exacto del `HEALTHCHECK`, dentro del contenedor |

---

## J. Logging y observabilidad

### E-LOG-01 · Los logs desaparecen **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | `docker logs` vacío, o los logs solo dentro del contenedor |
| **Causa** | Serilog/NLog configurados con sink a archivo |
| **Exposición real [V]** | `NLog.Web.AspNetCore` en `api-cloud`, `micro-cdl-portal-cliente`, `micro-integracion-portal-cliente`, `progreso-api-cdl`, `progreso-api-int`, `micro-backoffice`, `micro-reversas`, `api-integracion-externa`; `Serilog` a archivo en `gw-contabilidad`, `micro-hangfire-tasks-scoring`, `micro-versions-manager` |
| **Fix** | Sink a consola (regla R7 del estándar), y si el archivo es obligatorio, volumen montado |
| **Verificación** | `docker logs` muestra actividad de negocio, no solo el arranque |

### E-LOG-02 · Sentry deja de reportar, o se actualiza cuando había que quitarlo **[V]**

| | |
|---|---|
| **Síntoma** | Sin eventos en Sentry tras el salto |
| **Causa** | `Sentry.AspNetCore` 2.x/3.x no soporta el runtime nuevo (4.x pide net6+, 5.x/6.x pide net8+) |
| **Exposición real [V]** | La flota va de **2.1.3** (`gw-backoffice`, `gw-ordering`, `micro-operations-ordering`) a **5.11.0** (`gw-portal-digital`, `micro-integration-services`, `micro-portal-digital`) |
| **Fix** | **Preguntar antes de actualizar.** ADR-005 y ADR-012 definen el reemplazo por OpenTelemetry/GlitchTip: puede que la acción correcta sea **quitar Sentry**, no subirlo |
| **Verificación** | Un error provocado aparece donde se decidió que aparezca |

---

## K. Hangfire

### E-HF-01 · `Hangfire.MySqlStorage` está abandonado **[V]**

| | |
|---|---|
| **Síntoma** | Warnings de restore, comportamiento raro, o simplemente que no hay a dónde actualizar |
| **Causa** | Última versión **2.0.3**, de 2019. Verificado en nuget.org: no hay 2.0.4+ |
| **Exposición real [V]** | `api-background-tasks`, `micro-cdl-portal-cliente`, `micro-contabilidad`, `micro-hangfire-tasks`, `micro-hangfire-tasks-scoring`, `progreso-api-cdl` |
| **Fix** | **No se resuelve dentro de una migración de runtime.** Cambiar el storage de Hangfire migra datos de jobs: es un proyecto propio. Verificar que 2.0.3 funciona en el TFM destino y, si no, escalar |
| **Contradicción a resolver [V]** | Los repos referencian **MySqlStorage**, pero `asis-qa-total-apis-micros.md` §1 dice que en QA Total el storage de Hangfire es **SQL Server**. Antes de migrar cualquier componente D6 hay que saber contra qué storage corre de verdad |
| **Verificación** | Un job recurrente se registra, se ejecuta y queda en `Succeeded` |

### E-HF-02 · El job corre dos veces **[V]** (lección propia)

| | |
|---|---|
| **Síntoma** | Correos duplicados, asientos duplicados, archivos subidos dos veces |
| **Causa** | Dos instancias contra el mismo storage. Durante una migración es el escenario natural: la vieja sigue viva |
| **Fix** | **Apagar la instancia anterior antes de levantar la nueva.** No hay validación en paralelo posible para un host de Hangfire |
| **Verificación** | `SELECT * FROM HangFire.Server` muestra **una** instancia antes y después |
| **Precedente** | Riesgo R1 de ADR-016 + lección `hangfire-contab-demo-cl` |

### E-HF-03 · Los jobs encolados antes de la migración fallan al deserializar **[G]**

| | |
|---|---|
| **Síntoma** | Jobs en `Failed` con error de deserialización de argumentos |
| **Causa** | El storage guarda los argumentos serializados; un cambio de serializador o de firma del método los invalida |
| **Fix** | Vaciar la cola antes del corte, o migrar en una ventana sin jobs pendientes |
| **Verificación** | Cero jobs en `Failed` tras la migración |

---

## L. Librerías nativas y recursos del SO

### E-SKIA-01 · `DllNotFoundException: libSkiaSharp` o PDF que sale en blanco **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | Falla la generación de PDF, o sale sin texto |
| **Causa** | SkiaSharp y QuestPDF van **acoplados**: QuestPDF fija la major de SkiaSharp. Y los native assets tienen que coincidir con la major del managed |
| **Exposición real [V]** | `micro-factoring`: QuestPDF 2023.12.6 + SkiaSharp 2.88.7 (coherente). **`micro-monitor-cesiones-hf`: QuestPDF 2023.12.6 + SkiaSharp.NativeAssets.Linux.NoDependencies 3.119.1 — majors distintas.** Hoy en `develop`, no lo introduce la migración |
| **Fix** | Mover QuestPDF y SkiaSharp **juntos**, nunca uno solo. Verificar primero si la generación de PDF de `micro-monitor-cesiones-hf` funciona **hoy** |
| **Verificación** | Generar un PDF real y **abrirlo**. Que el archivo exista y pese algo no alcanza |

### E-NAT-01 · El PDF sale sin tildes o con cuadraditos **[G]**

| | |
|---|---|
| **Síntoma** | Texto con glifos faltantes |
| **Causa** | Falta `fontconfig` o las fuentes en la imagen |
| **Fix** | `fontconfig fonts-liberation fonts-dejavu-core` (ya está en la plantilla D4 del estándar) |
| **Verificación** | PDF con un texto con `ñ`, tildes y `€`/`S/` |

### E-NAT-02 · `libgdiplus` — **no hace falta** **[V]**

| | |
|---|---|
| **Estado** | Verificado: **ningún** repo de la flota clonada referencia el paquete `System.Drawing.Common` ni usa GDI+ real (`Bitmap`/`Graphics`/`Image.From*`). Los `using System.Drawing` son huérfanos o usan solo primitivas, que funcionan en Linux |
| **Consecuencia** | `libgdiplus` sale de la plantilla D4. El bloqueador que ADR-016 atribuye a `micro-banco`, `micro-factoring`, `micro-ordering`, `micro-confirming`, `micro-backoffice` y los `gwSolution` **no existe** |
| **Límite** | No verificado en los repos **no clonados** de QA Total (`microleasing`, `microjuicios`, `microbackoffice-ordering`, `apibo`). Ahí sigue siendo hipótesis |
| **Verificación** | Correr el grep de `analisis-previo.sh` sobre esos repos cuando se tengan |

### E-NAT-03 · Chromium se descarga al arrancar **[V]**

| | |
|---|---|
| **Síntoma** | Primer arranque lento o fallido; tráfico de salida inesperado |
| **Causa** | PuppeteerSharp descarga Chromium en runtime si no se le fija `ExecutablePath` |
| **Exposición real [V]** | `micro-factoring` y `micro-ordering` (PuppeteerSharp 12.0.0) |
| **Fix** | Instalar Chromium en la imagen y fijar el path + `--no-sandbox` (plantilla D4) |
| **Verificación** | Contenedor **sin salida a internet** que igual genera el PDF |

### E-LIC-01 · GemBox trunca documentos en silencio **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | El documento se genera pero le faltan páginas o tiene marca de agua |
| **Causa** | Modo free por clave inválida o ausente. **No lanza excepción** |
| **Exposición real [V]** | `GemBox.Document` en `gw-backoffice`, `gw-ordering`, `gw-portal-cliente`, `micro-autoatencion`, `micro-factoring` (35.0.1000), `micro-ordering`, `micro-portal-cliente`, `progreso-*` |
| **Fix** | Verificar que la clave está en variable de entorno y que la licencia cubre el runtime destino, **antes** de migrar |
| **Verificación** | Generar un documento de **más de 20 páginas** y contarlas |

### E-LIC-02 · Actualizar arrastra a licencia comercial **[V]**

| | |
|---|---|
| **Síntoma** | Aparece un aviso de licencia, o legal pregunta por una dependencia nueva |
| **Causa** | `AutoMapper` y `MediatR` pasaron a licencia comercial en sus majors recientes (hoy en nuget: AutoMapper 16.x, MediatR 14.x) |
| **Exposición real [V]** | 12 repos con AutoMapper 11/12/13; 10 repos con MediatR 11/12.4.1 — **todas versiones libres** |
| **Fix** | **Fijar, no actualizar.** `dotnet outdated -u` está prohibido en esta flota por exactamente esto (regla 6) |
| **Verificación** | `dotnet list package` muestra AutoMapper ≤13 y MediatR ≤12.4.1, salvo decisión explícita de negocio |

---

## M. Bases de datos y TLS

### E-SQL-01 · `A connection was successfully established... but then an error occurred during the login process` / `The certificate chain was issued by an authority that is not trusted` **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | La conexión a SQL Server que funcionaba deja de funcionar, sin cambios en la cadena de conexión |
| **Causa** | `Microsoft.Data.SqlClient` 4.0+ cambió el default a **`Encrypt=true`**. La cadena que no lo dice ahora exige TLS con certificado válido |
| **Exposición real [V]** | `micro-reporting` usa `System.Data.SqlClient 4.8.5` (a migrar); `micro-contabilidad` usa **los dos** conectores; `micro-reversas` ya en `Microsoft.Data.SqlClient 5.2.2`. Verificado además: **cero** cadenas con `Encrypt=` o `TrustServerCertificate` en los repos — o sea, todas dependen del default |
| **Fix** | Decidir **explícitamente**: `Encrypt=True;TrustServerCertificate=True` (lo pragmático contra servidores internos sin PKI) o instalar un certificado válido. Nunca dejarlo al default |
| **Verificación** | Abrir conexión y ejecutar un `SELECT 1` **desde el contenedor**, contra el servidor real |
| **Por qué es el más caro** | Se manifiesta tarde (al primer acceso a datos, no al arrancar), el mensaje apunta al login y no al TLS, y en QA Total hay dos SQL Server (uno RDS y uno on-prem — ver inventario de servidores) con distinta configuración |

### E-TLS-01 · Handshake TLS rechazado contra un servidor viejo **[G]**

| | |
|---|---|
| **Síntoma** | `SSL Provider: The client and server cannot communicate, because they do not possess a common algorithm`, o `ssl3_get_record:wrong version number` |
| **Causa** | La imagen base nueva trae **OpenSSL 3.x** con `SECLEVEL` estricto: rechaza TLS 1.0/1.1, SHA-1 y claves RSA cortas. Los servidores de QA Total corren Amazon Linux 2 con OpenSSL 1.0.2/1.1.1 (verificado en el AS-IS) |
| **Exposición** | el SQL Server on-prem (ver inventario de servidores), y terceros congelados: Jasper/SSRS (`micro-reporting`), Softland, Cavali |
| **Fix, en orden de preferencia** | 1) Actualizar el servidor/tercero a TLS 1.2. 2) Si no es posible, bajar `SECLEVEL` en la imagen vía `openssl.cnf` — **decisión consciente, documentada y con fecha de revisión**, no un parche silencioso |
| **Verificación** | `openssl s_client -connect <host>:<puerto>` **desde dentro del contenedor** |
| **Gate** | **cybersec** si se baja el SECLEVEL |

### E-MYSQL-01 · `MySql.Data` viejo contra runtime nuevo **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | Fallos de conexión o de autenticación (`caching_sha2_password`), o cuelgues bajo carga |
| **Exposición real [V]** | `MySql.Data` **8.0.18** en `gw-backoffice`, `gw-ordering`, `gw-portal-cliente`, `progreso-gw-portal-cliente`; **8.0.22** en `api-cloud` — de 2019/2020 |
| **Fix** | Migrar a `MySqlConnector` (API compatible, mantenido, es lo que usa Pomelo por debajo) o subir `MySql.Data` a 9.x |
| **Verificación** | Conexión + una consulta que devuelva filas, desde el contenedor |

---

## N. Gateways

### E-OC-01 · Ocelot deja de rutear tras el salto **[G]** · exposición **[V]**

| | |
|---|---|
| **Síntoma** | 404 en todas las rutas, o el gateway no arranca por error de configuración |
| **Causa** | El formato de `ocelot.json` y los paquetes de Ocelot cambiaron mucho entre 17 y 24+ |
| **Exposición real [V]** | `gw-crm`, `gw-reporting`, `gw-security` en **Ocelot 17.0.1 / net5** (hoy va por 25.x) |
| **Fix** | **No leer 8 changelogs: copiar de casa.** `gw-contabilidad` ya corre **Ocelot 24.0.1 sobre net8** con `SwaggerForOcelot`. Su `ocelot.json` y su `Program.cs` son la referencia del formato actual, en el mismo ambiente y con la misma gente |
| **Verificación** | Cada ruta del `ocelot.json` devuelve lo mismo que antes. El `ocelot.json` va **montado**, no horneado (familia D3) |

---

## O. Contenedor

### E-DOCK-01 · La imagen base no coincide con el TFM **[V]**

| | |
|---|---|
| **Síntoma** | `You must install .NET to run this application` o `The framework 'Microsoft.NETCore.App', version 'X' was not found` |
| **Causa** | El `FROM` quedó en otra versión que el `.csproj` |
| **Exposición real [V]** | 17 repos ya tienen el Dockerfile desalineado **hoy**: `micro-agents-antropic` (imagen 10.0 / csproj net8), `micro-confirming` y `gw-confirming` (8.0 / net6), `micro-operations` (8.0 / net7), `micro-authorization` (7.0 / net6), `micro-reporting` (6.0 / net5), y los stubs de Visual Studio con `dotnet/core/aspnet:3.0` |
| **Fix** | `ARG DOTNET_VERSION=${DOTNET_TAG}` desde `parametros.env`. **Nunca escribir la versión a mano en el Dockerfile** |
| **Verificación** | `docker run --rm <img> dotnet --list-runtimes` |

### E-DOCK-02 · `mcr.microsoft.com/dotnet/core/aspnet:X` no existe **[V]**

| | |
|---|---|
| **Síntoma** | `manifest unknown` al construir |
| **Causa** | El segmento `core/` desapareció del repositorio de MCR. Los stubs de Visual Studio de 2019 lo usan |
| **Fix** | `mcr.microsoft.com/dotnet/aspnet:${DOTNET_TAG}` |
| **Verificación** | `docker pull` del tag exacto antes de construir |

### E-DOCK-03 · `unhealthy` permanente con la app funcionando **[V]** (lección propia)

| | |
|---|---|
| **Síntoma** | El contenedor nunca llega a `healthy` |
| **Causas, en orden** | 1) La imagen `aspnet` (Debian slim) **no trae `curl`**. 2) E-RT-02: la app escucha en otro puerto. 3) E-SWAG-02: el path del healthcheck ya no existe |
| **Fix** | `apt-get install -y curl` antes de bajar a no-root (ya está en la plantilla D1) |
| **Verificación** | `docker inspect --format '{{json .State.Health}}' <c>` |
| **Precedente** | Ya costó tiempo en `micro-api-back` |

---

## P. Cómo se agrega una entrada

Cuando resolvés un error que no está acá:

1. Código nuevo en la familia que corresponda.
2. **Síntoma literal** — el mensaje como aparece, para que sea encontrable con Ctrl+F.
3. Causa real, no la primera hipótesis.
4. Fix, y **qué NO hacer** si hubo un atajo tentador.
5. **Verificación**: cómo se comprueba que el fix funcionó. Sin esto la entrada no sirve.
6. Marca **[V]** con el repo y la versión donde se verificó.
