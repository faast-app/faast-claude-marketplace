# Stacks vigentes (2026) y como tratarlos

**Regla de oro:** el repo ya tiene una version (`global.json`, `TargetFramework`, `.nvmrc`/
`engines`, `pyproject.toml`, `pom.xml`/`build.gradle`, `package.json`). Trabajas en ESA
version y con SUS librerias. Lo de aqui es el default para servicios nuevos (los decide el
Arquitecto) y la referencia de idioms. Migrar de version, de ORM o de framework solo con
pedido explicito (en .NET con la skill `migrar-dotnet`). Antes de agregar un paquete: version
fijada y licencia leida (AutoMapper 15+ y MediatR 13+ pasaron a licencia comercial;
FluentAssertions 8+ tambien — no se actualizan "porque hay version nueva" ni se agregan en
codigo nuevo sin decision).

## .NET
| Version | Estado | Notas |
|---|---|---|
| **.NET 10 (C# 14)** | LTS, destino de la flota (hasta 2028-11) | Default para servicios nuevos |
| .NET 8 / 9 | fin de soporte 2026-11-10 | Migrar con `migrar-dotnet` cuando se pida |
| netcoreapp3.x / net5 / net6 / net7 | EOL | No se dockerizan sin migrar (familia D5) |

Idioms vigentes: Minimal APIs con `MapGroup`, `TypedResults` y validacion integrada (o
Controllers si el repo los usa); `AddProblemDetails()` + `IExceptionHandler`; OpenAPI nativo
(`AddOpenApi()`/`MapOpenApi()`) + **Scalar** como UI (skill `scalar-api-docs`); EF Core 10
(`AsNoTracking`, `ExecuteUpdate/ExecuteDelete` para lotes, interceptores para auditoria,
`IsRowVersion` para concurrencia; migraciones revisadas por el DBA); `TimeProvider` para el
reloj; `IHttpClientFactory` + `AddStandardResilienceHandler()`; `IOptions<T>` validadas al
arranque (`ValidateOnStart`); health checks (`AddHealthChecks`); OpenTelemetry; Serilog o el
logging nativo con plantillas; `FallbackPolicy` de autorizacion; `AddRateLimiter` aplicado con
`RequireRateLimiting`. Config en codigo `config["Seccion:Clave"]`, en variables
`Seccion__Clave`. Comandos: `dotnet build`, `dotnet test`, `dotnet format`.

## Node.js
| Version | Estado |
|---|---|
| **Node 24** | LTS activo (default nuevo) |
| Node 22 | LTS de mantenimiento — valido; respeta el repo |
| Node 20 o anterior | fin de soporte (2026-04) — migrar cuando se pida |

Frameworks: NestJS (servicios con estructura), Fastify (rendimiento, esquemas JSON),
Express 5 (legado/simple). Validacion: Zod/TypeBox/class-validator. ORM: Prisma, Drizzle,
TypeORM (respeta el repo). Logs: Pino. Tests: Vitest/Jest + supertest + testcontainers.
TypeScript `strict`. ESM en codigo nuevo salvo que el repo sea CJS. `fetch`/undici nativo con
`AbortSignal.timeout`. Comandos: `npm ci`, `npm run build`, `npm test`, `npx eslint`, `npx prettier`.

## Python
**Python 3.13** (3.14 si el repo ya esta ahi). FastAPI + Pydantic v2 (`model_validate`,
`ConfigDict`, `Annotated`), SQLAlchemy 2.x (estilo 2.0, `select()`, sesiones async si el repo
es async), Alembic para migraciones, `httpx` con timeouts, structlog, pytest. Gestion con
`uv` o el que use el repo (poetry/pip-tools). Lint/format: **ruff** (`ruff check`, `ruff
format`; reemplaza black/isort/flake8 donde el repo lo adopto). Tipos con mypy/pyright.

## Java
**Java 21 LTS** (Java 25 LTS disponible para servicios nuevos si el Arquitecto lo decide).
Spring Boot 3.x (4.x solo en servicios nuevos con decision): virtual threads
(`spring.threads.virtual.enabled`), `RestClient`, `ProblemDetail`, Spring Data JPA/MyBatis,
Bean Validation, Flyway/Liquibase, Micrometer + OTel, JUnit 5 + AssertJ + Testcontainers.
Records para DTOs. Build: `./gradlew build` o `mvn verify`; formato Spotless.

## Frontend
- **React 19 + TypeScript + Vite** (default): Actions/`useActionState`/`useOptimistic` para
  mutaciones de formularios donde encaje, `use` para promesas, React Compiler si el repo lo
  habilito. Router: **TanStack Router** (tipado de punta a punta) o React Router v7 (respeta el
  repo). Datos: **TanStack Query v5**. Estado cliente: Zustand o contexto acotado. Formularios:
  React Hook Form + zod o TanStack Form. Estilos: Tailwind v4 o CSS Modules + tokens DTCG.
  Tests: Vitest + Testing Library + MSW; e2e Playwright (QA).
- **Angular** (version vigente del repo; nuevos en la ultima estable): standalone components,
  **signals** (`signal`, `computed`, `effect`, `input()`/`output()`), control flow `@if/@for`,
  `inject()`, zoneless donde el repo lo adopto, Reactive Forms tipados, `HttpClient` con
  interceptores, defer blocks para carga diferida.
- **Vue 3.5+**: `<script setup lang="ts">`, Composition API, Pinia, Vue Router, VeeValidate +
  zod, Vitest + Vue Test Utils.
- **Microfrontends**: Module Federation (Webpack 5 / `@module-federation/vite` / MF 2.0) con
  `react`/`react-dom` singleton; single-spa para polyglot. Contratos entre MF por eventos o
  estado minimo compartido; nada de logica de negocio compartida.
- Node de build: el `.nvmrc`/`engines` del repo; nuevos en Node 24.

## Bases de datos
MySQL **8.0 / 8.4 LTS** (InnoDB, `utf8mb4`), SQL Server 2019/2022, PostgreSQL 16/17, MongoDB
7/8, Redis 7. La version la fija el ambiente; no se usan features que el motor destino no
tiene (p. ej. `ADD COLUMN IF NOT EXISTS` es MariaDB, no MySQL 8).

## Infra
Docker Engine + Compose v2 (`docker compose`), GitHub Actions (acciones fijadas por SHA o tag
mayor verificado), GHCR, Terraform/OpenTofu, AWS (EC2, ECS, RDS, S3, CloudFront, Secrets
Manager/SSM), Apache httpd/Nginx/Traefik v3 como reverse proxy, YARP/Ocelot como gateways
.NET, OpenTelemetry Collector, Trivy/Grype + gitleaks en CI. Estandar de contenedor y
despliegue: skills `deployment-standard` y `dockerizar-componente`.
