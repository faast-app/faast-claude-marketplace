# Checklist de creación de tests — `<componente>`

**Repo:** · **Rama:** · **Carril de testabilidad:** 🟢/🟡/🔴
**TFM de la app:** · **TFM del test:** (deben ser iguales) · **Objetivo:** migración / regresión / desarrollo
**Responsable:** · **Fecha inicio:** · **Fecha cierre:**

> Cualquier "no" bloquea. Se adjunta al handoff.
> Los ítems **(gate)** requieren firma de otro rol.

---

## 0. Encuadre

- [ ] Objetivo declarado (migración / regresión / desarrollo). Si es migración, **los
      tests van antes** y en su propio PR (SKILL §5).
- [ ] Identificado qué **cuesta plata** si se rompe. Es el orden de trabajo.
- [ ] Definido si hay ventana para **cambios de testabilidad** (SKILL §4).
- [ ] `parametros-tests.env` leído; versiones de paquetes fijadas desde ahí.

## 1. Análisis

- [ ] `analizar-testabilidad.sh` ejecutado; salida en el informe.
- [ ] Mapa de endpoints por controller y LOC por capa.
- [ ] **Dónde vive el negocio** contestado (controller / repositorio / stored procedure).
- [ ] Inventario de dependencias externas completo (EF, HTTP, Hangfire, SMTP, S3, JWT,
      reloj, archivos, cultura).
- [ ] **De dónde sale el esquema** contestado (`01-analisis` §5). Si es "de ningún lado":
      integración con base **declarada no viable** (`T-DB-04`).
- [ ] Los cinco bloqueadores de `WebApplicationFactory` revisados uno por uno.
- [ ] **Carril asignado** con su motivo en una línea.
- [ ] Lista de endpoints a caracterizar, sacada del inventario de consumidores — **no** "todos".

## 2. Preparación

- [ ] Árbol `tests/` con la convención de `05-ci-cobertura-dod` §4.
- [ ] `.csproj` con **versiones exactas**, sin comodines (`E-NU-03`).
- [ ] TFM del test **igual** al de la app (`E-CS-03`).
- [ ] `Microsoft.AspNetCore.Mvc.Testing` en la major del TFM (`03-stack` §4.1).
- [ ] Paquetes de EF de test en la major de **EF Core** de la app, no del TFM (§4.2).
- [ ] **Licencias revisadas**: sin `FluentAssertions` ≥ 8, sin `AutoMapper` ≥ 15, sin
      `MediatR` ≥ 13 (`E-LIC-02`).
- [ ] `.gitignore` con `*.received.*`.
- [ ] `coverage.runsettings` con las exclusiones (DTOs, entidades, `Program.cs`, migraciones).
- [ ] Verificado que agregar los proyectos al `.sln` **no rompe el build de la imagen** (`T-DOCK-01`).

## 3. Caracterización (si esto es red de seguridad de una migración)

- [ ] Escrita y **verde en el TFM actual**, antes de tocar el `.csproj` de la app.
- [ ] Snapshot de **cada** documento OpenAPI publicado, **normalizado** (sin `info.version`
      ni timestamps) (`T-SNAP-02`).
- [ ] Golden-file de las respuestas de los endpoints consumidos.
- [ ] Serialización JSON: `null`, enums, `decimal`, `DateTime`.
- [ ] Fechas: una parseada desde request y una serializada.
- [ ] Monto formateado con la cultura real del componente.
- [ ] **JWT**: emisión, validación, **token de oro**, firma inválida, expirado, arranque sin clave.
- [ ] **Cifrado**: vector de ida, vector de vuelta, y descifrado de un valor con el formato
      que hay en la base hoy.
- [ ] SQL generado por EF (`ToQueryString()`) de las consultas LINQ complejas.
- [ ] **PR de tests mergeado antes del primer commit de migración.**

## 4. Unitarios y negocio

- [ ] Cálculos de dinero cubiertos, con bordes (0, negativo, redondeo).
- [ ] Validaciones de entrada sucia (`null`, vacío, tilde, `ñ`).
- [ ] Un test por cada bug ya reportado que siga vivo.
- [ ] Un solo test para AutoMapper: `AssertConfigurationIsValid()`.
- [ ] **No hay tests que solo verifiquen que un método llamó a otro.**

## 5. Integración

- [ ] La factory inyecta configuración **por variables de entorno** `Seccion__Clave` (regla
      de la casa "todo el appsettings a variables").
- [ ] La factory **no define ningún DSN de telemetría** (`T-OBS-01`).
- [ ] Hangfire no levanta su servidor en tests (`T-HF-01`).
- [ ] Un contenedor **por suite**, no por test (`T-TC-02`); limpieza entre tests.
- [ ] Nada de EF InMemory (`02-estrategia` §4.3).
- [ ] Si no hay Docker en el runner: **gap declarado**, no borrado ni silenciado.

## 6. Contrato contra ambiente

- [ ] **Solo QA. Solo `GET`.** Nunca Puente, Demo ni producción de cliente (regla 5).
- [ ] Sin URL por defecto: sin variable de entorno, los tests se **saltean**.
- [ ] Categoría propia, **excluida del CI** por defecto.
- [ ] Línea base tomada **antes** de la migración.

## 7. Higiene

- [ ] La suite pasa **sin red** (`T-FLAKE-02`).
- [ ] La suite pasa **dos veces seguidas** y sin paralelismo (`T-FLAKE-01`).
- [ ] La suite pasa con `TZ=UTC` **y** con la TZ del ambiente (`T-TIME-01`).
- [ ] **Ningún `DateTime.Now` dentro de un test** (regla 7).
- [ ] Cero secretos, cero datos reales de cliente (`T-SEC-01`).
- [ ] Cada `[Skip]` con motivo escrito en el atributo.

## 8. CI

- [ ] Unit + Caracterización corren en cada PR y **bloquean**.
- [ ] **El pipeline falla si se ejecutaron 0 tests** (`T-CI-01`).
- [ ] El pipeline falla si un PR de migración modifica un `.verified.*` (`T-SNAP-01`).
- [ ] Resultados (`.trx`) y cobertura publicados como artefacto y en el resumen del run.
- [ ] El workflow **no usa ningún secreto**.
- [ ] Cobertura medida y **gate por riesgo** definido (`05-ci` §2), no por porcentaje global.

## 9. Gates

- [ ] **(gate) cybersec** — JWT, cifrado, certificados. Firmado por: ____
- [ ] **(gate) dba** — si se pidió dump de estructura. Firmado por: ____
- [ ] **(gate) QA** — lista de endpoints del contrato validada; QA **sigue** validando con
      capturas. Firmado por: ____
- [ ] **(gate) infra** — si se tocó el `Dockerfile` (`T-DOCK-01`) o hace falta Docker en CI. Firmado por: ____

## 10. Cierre

- [ ] Informe en `{coordinacion}/inventario/tests/<repo>.md`.
- [ ] **Lista explícita de lo que NO quedó cubierto, con el motivo.**
- [ ] Entradas nuevas agregadas a `04-catalogo-errores-tests.md`, con su verificación.
- [ ] Entradas **[G]** ejecutadas de verdad, repromovidas a **[V]**.
- [ ] Cambios de testabilidad pedidos, listados con tamaño y riesgo.
- [ ] Handoff al lead.
