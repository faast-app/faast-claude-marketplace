# Estrategia de pruebas por capa — detalle

Para backends .NET legados sin tests (o antes de migrar de TFM) la skill especifica es
**`crear-tests-backend`**: carriles de testabilidad, caracterizacion, plantillas y CI. Esta
referencia es la estrategia general para todos los stacks y para el trabajo diario de HU/bug.

## 1. Que se prueba primero: el orden del riesgo

1. **Auth y autorizacion**: emision/validacion de token, expirado, firmado con otra clave,
   arranque sin clave, endpoint sin permiso → 403, recurso ajeno → 404/403 (anti IDOR).
2. **Dinero**: todo calculo que termina en monto, tasa, comision, excedente o prorrateo, con
   bordes (0, 1, maximo, redondeo en .5, CLP sin decimales, residuo de prorrateo).
3. **Estados y concurrencia**: transiciones validas e invalidas, doble ejecucion (idempotencia),
   dos actualizaciones simultaneas (409).
4. **Integraciones**: contrato con lo que consumes y con lo que te consumen; timeouts y errores
   del tercero.
5. **El resto** (CRUD trivial, mapeos), si el riesgo lo justifica.

No se persigue un porcentaje global de cobertura: el gate es que los modulos de riesgo estan
cubiertos.

## 2. Las capas

| Capa | Que valida | Como | Corre en CI |
|---|---|---|---|
| **Unit** | Reglas puras: calculos, validaciones, mapeos con logica, maquinas de estado | Sin I/O; dobles solo en los bordes (reloj, repositorio, cliente HTTP) | Siempre |
| **Integracion** | Endpoint → servicio → **BD real**; SQL, migraciones, constraints, transacciones, serializacion | `WebApplicationFactory` (.NET), `supertest`/`app.inject` (Node), `TestClient`/`httpx.AsyncClient` (FastAPI), `@SpringBootTest` (Java) + **Testcontainers** (MySQL/SQL Server/Postgres/Redis) | Si el runner tiene Docker (si no, gap declarado, no se borra) |
| **Contrato** | Que la API cumple su OpenAPI y que lo que consumes sigue igual | Snapshot del OpenAPI, Schemathesis (QA), tests de contrato del consumidor, golden files de respuestas | Snapshot si; contra ambiente no |
| **E2E** | Flujos criticos de usuario de punta a punta | Playwright (lo mantiene QA, suite `e2e-faast`); el dev agrega `data-testid` y no rompe selectores | Pipeline E2E |
| **Caracterizacion** | Que el comportamiento actual de un legado no cambia | Golden files, snapshot de contrato, antes/despues | Siempre (no se edita durante una migracion) |

**Por que BD real y no InMemory/SQLite:** el proveedor InMemory de EF no aplica constraints,
transacciones ni SQL real; SQLite no se comporta como MySQL/SQL Server (tipos, collation,
mayusculas, fechas). Un test que pasa contra InMemory y falla en produccion es peor que no
tener test. InMemory/SQLite solo para logica que no depende del motor, y declarado.

## 3. Herramientas por stack (default para codigo nuevo; respeta lo que ya usa el repo)

| Stack | Runner / aserciones | Dobles | Integracion | Otros |
|---|---|---|---|---|
| .NET | xUnit v2 (default de la flota; v3 si el repo ya lo usa) + **Shouldly** (FluentAssertions 8.x es **licencia comercial**; 7.x la ultima Apache-2.0) | **NSubstitute** en repos nuevos; Moq (>= 4.20.2) se queda donde ya esta | `Microsoft.AspNetCore.Mvc.Testing` + `Testcontainers.MsSql`/`.MySql` + Respawn | `TimeProvider` + `FakeTimeProvider`, Verify para snapshots. Versiones y licencias verificadas: `crear-tests-backend/reference/03-stack-y-licencias.md` |
| Node/TS | Vitest (o Jest si el repo ya lo usa) | `vi.fn`, MSW para HTTP | `testcontainers` (node) + `supertest`/`fastify.inject` | fake timers, `@faker-js/faker` con seed |
| Python | pytest + pytest-asyncio | `unittest.mock`, `respx` (httpx) | `testcontainers` (python) + `httpx.AsyncClient` | `freezegun`/`time-machine`, `hypothesis` para propiedades |
| Java | JUnit 5 + AssertJ | Mockito | Testcontainers + `@SpringBootTest`/`@DataJpaTest` | `Clock` inyectado, WireMock |
| Front | Vitest + Testing Library (+ `user-event`) | MSW | Playwright component testing o e2e de QA | `axe` en tests de componentes |

Antes de agregar un paquete de test: version fijada y **licencia leida** (no "el mas nuevo").

## 4. Reglas de una buena prueba

- **Determinista**: reloj inyectado o congelado (nada de `DateTime.Now`/`new Date()` en la
  asercion), cultura y zona horaria explicitas (corre igual en la maquina del dev y en CI UTC),
  seeds fijas para datos aleatorios, sin depender del orden de ejecucion.
- **Independiente**: cada test arma y limpia sus datos (transaccion revertida, BD por clase o
  respawn). Nada de "el test 3 necesita lo que creo el 2".
- **Legible**: nombre `Metodo_Escenario_ResultadoEsperado` (o `debe ... cuando ...`), Arrange/
  Act/Assert visibles, una razon para fallar.
- **Sin secretos ni datos reales**: claves de prueba generadas en el test, RUT sinteticos
  validos, nada de connection strings reales. Lo que necesita un valor real se salta con
  `Skip` y motivo escrito.
- **Contra ambientes reales: solo lectura y solo QA.** Prohibido POST/PUT/DELETE desde una
  suite contra cualquier ambiente; prohibido apuntar a puente/demo/productivo.
- **Un test rojo se investiga, no se `Skip`ea.** Un `Skip` sin motivo y ticket es deuda oculta.
- **Verde local y rojo en CI (o al reves) es un bloqueador**: casi siempre cultura, zona
  horaria, paralelismo o datos compartidos.

## 5. Bugs: prueba que reproduce primero

1. Escribe la prueba al nivel mas bajo que reproduce el bug (unit si es un calculo,
   integracion si es SQL/serializacion/permisos).
2. Ejecutala y confirma que **falla por la razon del bug** (no por un setup roto).
3. Corrige. La prueba pasa. Corre la suite completa del modulo.
4. Deja la prueba como regresion, con referencia al bug en el nombre o comentario.
Si el bug no se puede reproducir en una prueba automatizada (depende de un tercero o del
ambiente), documenta por que y como lo verificaste manualmente.

## 6. Que NO se prueba

DTOs sin logica, getters/setters, configuracion de DI linea por linea, librerias de terceros,
el framework, Swagger/Scalar, stored procedures que el repo no posee (se cubren por
integracion o contrato), y codigo generado. Tampoco se escriben tests que solo repiten la
implementacion (mocks verificando que se llamo al mock).

## 7. Datos de prueba fintech

- Montos con decimales "incomodos" (`0.005`, `999999999.99`), CLP grandes sin decimales, y
  monedas mezcladas para probar que se rechazan.
- Fechas en bordes: fin de mes, 29 de febrero, cambio de horario de Chile, feriados, vencimiento
  hoy/ayer/mañana en la zona del pais.
- Documentos validos e invalidos por pais (RUT con DV `K`, RUC/NIT con DV erroneo).
- Usuarios de distintos tenants/clientes para probar aislamiento.
