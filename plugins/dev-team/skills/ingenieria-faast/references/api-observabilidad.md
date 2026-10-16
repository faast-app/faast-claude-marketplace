# API, resiliencia y observabilidad — detalle

En repos legados se respeta el formato de error y de respuesta que ya consumen los clientes
(cambiarlo es un breaking change). Lo de aqui es el default para APIs y endpoints nuevos.

## 1. Diseño de endpoints

- Recursos en plural y sustantivos (`/api/v1/operaciones/{id}/giros`); acciones de negocio que
  no son CRUD como subrecurso o verbo explicito (`POST /operaciones/{id}/aprobar`).
- Metodos con su semantica: GET sin efectos; PUT idempotente; POST para crear/acciones (con
  `Idempotency-Key` si mueve dinero); PATCH parcial; DELETE logico salvo pedido.
- Codigos: `200/201(+Location)/202(asincrono)/204`; `400` mal formado; `401` sin
  autenticacion; `403` sin permiso; `404` no existe **o no es tuyo** (no confirmes existencia de
  recursos ajenos); `409` conflicto de estado/concurrencia/idempotencia; `412` If-Match fallido;
  `422` regla de negocio; `429` rate limit; `500` inesperado; `503` dependencia caida.
- DTOs de request/response propios: nunca exponer entidades de BD (mass assignment, fugas).
- Nombres JSON consistentes con el repo (camelCase por defecto en .NET/Node).
- Fechas ISO 8601 (UTC con `Z`; fechas de negocio `YYYY-MM-DD`); montos como en `fintech.md` §2.

## 2. Errores — RFC 9457 Problem Details

```json
{
  "type": "urn:faast:problem:operacion-estado-invalido",
  "title": "La operacion no esta en un estado que permita girar",
  "status": 422,
  "detail": "La operacion 18233 esta en estado PENDIENTE_FIRMA.",
  "instance": "/api/v1/operaciones/18233/giros",
  "traceId": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
  "code": "OPERACION_ESTADO_INVALIDO",
  "errors": { "monto": ["Debe ser mayor que 0"] }
}
```
- `Content-Type: application/problem+json`. `type` estable (URI o codigo) que el front puede
  mapear a un mensaje; `code` de negocio legible por maquina.
- `detail` para humanos, **sin** stack trace, SQL, nombres de tabla, rutas ni datos personales.
- .NET: `builder.Services.AddProblemDetails()` + `app.UseExceptionHandler()` +
  `IExceptionHandler` para mapear excepciones de dominio; `TypedResults.Problem/ValidationProblem`.
  Node: un error handler central (Fastify `setErrorHandler`, Nest `ExceptionFilter`).
  FastAPI: `exception_handler` para `RequestValidationError` y errores de dominio.
  Spring: `ProblemDetail` + `@ControllerAdvice` (`spring.mvc.problemdetails.enabled=true`).
- Log del error en el servidor con `traceId` y contexto; al cliente solo el Problem.

## 3. Validacion en el borde

- Toda entrada externa se valida al entrar (forma, tipos, rangos, longitudes, enumerados):
  FluentValidation / DataAnnotations / validacion nativa de Minimal APIs (.NET 10), Zod/
  TypeBox/class-validator (Node), Pydantic v2 (FastAPI), Bean Validation (Spring).
- Reglas de negocio (estado, limites, pertenencia) en el dominio/servicio, con error `422`.
- Limites duros: tamaño de body, de archivos (y tipo real por magic bytes, no por extension),
  de paginas, de longitud de strings. Nada de deserializacion polimorfica abierta.

## 4. Paginacion, filtros y orden

- Siempre paginado lo que puede crecer. `limit` con default (20-50) y **maximo** (100-500).
- Offset (`page/pageSize`) para listados administrativos; cursor/keyset (`after=<id>`) para
  volumenes grandes o feeds. Respuesta con `items`, `total` (si es barato) y `next`.
- Orden **estable** (agrega la PK como desempate). Filtros por lista blanca de campos; nada de
  ordenar por un nombre de columna que llega del cliente sin validar (inyeccion).

## 5. Versionado y compatibilidad

- `/api/v1/...` cuando hay consumidores externos o de otros equipos. Cambios aditivos (campo
  nuevo opcional, endpoint nuevo) no versionan; quitar/renombrar campos, cambiar tipos o
  semantica de codigos **si**.
- Ley de robustez: el cliente ignora campos desconocidos; el servidor no exige campos nuevos a
  clientes viejos.
- Deprecacion con aviso (`Deprecation`/`Sunset` headers) y handoff al Lead con los consumidores.
- OpenAPI es el contrato: se actualiza en el mismo PR. .NET 9+: `AddOpenApi()`/`MapOpenApi()`
  nativo + UI **Scalar** (skill `scalar-api-docs`); en legado se mantiene el generador existente.

## 6. Seguridad de la API

- Autorizacion **cerrada por defecto** (fallback policy global) y explicita por endpoint;
  `[AllowAnonymous]` solo donde corresponde y justificado.
- Autorizacion **por recurso** (anti IDOR/BOLA): el filtro por tenant/cliente/usuario va en la
  consulta, no despues de traer el dato.
- Rate limiting **aplicado** (no solo declarado) en login, MFA, reset de clave, endpoints de
  alto costo; los fallos de MFA cuentan para el lockout.
- CORS con lista explicita de origenes por ambiente; nunca `*` con credenciales.
- Cabeceras: `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`,
  `Content-Security-Policy` en lo que sirva HTML, `Cache-Control: no-store` en respuestas con
  datos sensibles.
- JWT: validar firma, `iss`, `aud`, `exp`, algoritmo fijo; claves desde config y arranque
  abortado si faltan.

## 7. Resiliencia en llamadas salientes

- **Timeout en TODA llamada saliente** (HTTP, BD, colas, SMTP, S3). Sin timeout, un tercero
  lento tumba tu servicio.
- **Reintentos solo de operaciones idempotentes** (GET, PUT, o POST con Idempotency-Key), con
  backoff exponencial + jitter y tope (2-3). Nunca reintentar un giro sin clave de idempotencia.
- **Circuit breaker** ante dependencias inestables; fallback explicito (error claro o
  degradacion documentada), nunca silencioso en auth o dinero.
- .NET 8+: `Microsoft.Extensions.Http.Resilience` (`AddStandardResilienceHandler()`, Polly v8)
  sobre `IHttpClientFactory`; nunca `new HttpClient()` por request. Node: `undici`/`fetch` con
  `AbortSignal.timeout()`, `p-retry`, `opossum`. Python: `httpx` con `timeout=`, `tenacity`.
  Java: Resilience4j, `RestClient`/`WebClient` con timeouts.
- Bulkhead/limites de concurrencia hacia terceros con cuota (bancos, SII, burós).

## 8. Observabilidad

**Correlacion:** W3C Trace Context (`traceparent`) propagado en HTTP y mensajes. OpenTelemetry
para trazas, metricas y logs (exportador OTLP al collector que define infra). .NET:
`AddOpenTelemetry().WithTracing(...).WithMetrics(...)` + instrumentacion ASP.NET Core,
HttpClient, EF Core/SqlClient. Node: `@opentelemetry/sdk-node` + auto-instrumentations.
Python: `opentelemetry-instrumentation-fastapi`. Java: agente OTel o Micrometer Tracing.

**Logs estructurados** (Serilog/Microsoft.Extensions.Logging con plantillas, Pino, structlog,
Logback JSON):
- Mensaje con plantilla y propiedades (`"Giro {GiroId} creado para operacion {OperacionId}"`),
  nunca concatenacion.
- Siempre `traceId`/`spanId`; `tenant`/`cliente` como id interno; nunca PII ni secretos.
- Niveles: `Error` = algo que alguien debe mirar; `Warning` = anomalia recuperada; `Information`
  = hitos de negocio (operacion creada, giro enviado); `Debug` apagado en ambientes reales.
- A stdout/stderr (contenedor); nada de archivos de log dentro del contenedor.
- Integraciones de errores (Sentry u otra) con scrubbing de datos sensibles activado.

**Metricas minimas por servicio:** tasa de requests, errores y latencia (p50/p95/p99) por
endpoint; saturacion (pool de conexiones, colas, threads); metricas de negocio clave (giros
creados/fallidos, operaciones por estado).

**Health:**
- `GET /health/live` → solo el proceso (lo usa el HEALTHCHECK del contenedor; una caida de la
  BD no debe reiniciar el contenedor).
- `GET /health` (readiness) → dependencias + `{component, version, status, environment,
  commit, timestamp, checks}`; `200` Healthy/Degraded, `503` Unhealthy; sin datos sensibles.
- La version sale de `version.txt` leido en runtime (una sola fuente, ver `deployment-standard`).

## 9. Asincronia, colas y jobs

- Mensajes con `message_id`, `correlation_id`, version de esquema; consumidores idempotentes
  (inbox) y con DLQ; reintentos con backoff; poison messages observables.
- Jobs programados: idempotentes, con lock o una sola replica (Hangfire: una replica por
  storage y ambiente), zona horaria explicita en el cron, y metricas de exito/fallo.
- Operaciones largas por API: `202 Accepted` + recurso de estado (`/procesos/{id}`), no
  requests de minutos.
