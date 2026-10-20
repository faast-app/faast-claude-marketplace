# 05 — CI, cobertura y Definition of Done

**Fase 6 de `crear-tests-backend`.**

---

## 1. Qué corre y dónde

| Suite | En cada PR | En CI nocturno | A mano | Necesita |
|---|---|---|---|---|
| `Tests.Unit` | **Sí, bloqueante** | sí | sí | SDK |
| `Tests.Caracterizacion` | **Sí, bloqueante** | sí | sí | SDK |
| `Tests.Integracion` | Sí **si el runner tiene Docker** | sí | sí | SDK + Docker |
| `Tests.Contrato` | **No** | no | sí (`workflow_dispatch`) | Ambiente QA + variables |

**Las dos primeras son el gate.** Corren en minutos, sin red, sin Docker y sin secretos.
Si alguna necesita algo más, está mal clasificada (`T-FLAKE-02`).

**Si el runner no tiene Docker**, la integración no corre y **se declara como gap en el
informe**. No se borra, no se marca `[Skip]` global, no se pretende que no existe.

---

## 2. Cobertura: por riesgo, no por porcentaje

Un umbral global de cobertura en un legado produce dos cosas, las dos malas: tests de
getters para llegar al número, y un gate que nadie puede subir sin trampa.

**El gate de esta skill es una lista de módulos, con su umbral, escrita por el equipo:**

| Módulo | Umbral de línea | Por qué |
|---|---|---|
| Núcleo puro (formateo, cifrado, utilidades) | **≥ 80%** | Es testeable al 100% sin excusas y lo usa todo el sistema |
| Autenticación / autorización | **≥ 70%**, y **100% de los casos de `02-estrategia` §2.5** | El fallo silencioso |
| Cálculos de dinero | **100% de los casos identificados**, sin umbral de línea | Lo que importa son los casos, no las líneas |
| Controllers / repositorios | **sin umbral** | Se cubren por caracterización de contrato, que no se mide en % |
| DTOs, entidades, `Program.cs`, migraciones | **excluidos de la medición** | `coverage.runsettings` |

**Además, dos gates que sí son globales y sí sirven:**

1. **La suite pasa.** Cero rojos, cero `[Skip]` sin motivo escrito.
2. **La cobertura no baja** (ratchet): el porcentaje del PR se compara con el de la rama
   base. Bajar requiere justificación en el PR. Esto empuja hacia arriba sin obligar a
   nadie a inventar tests para llegar a un número de un día para otro.

**Y el gate que más vale de todos, el del `T-CI-01`: el pipeline falla si se ejecutaron
0 tests.** Sin eso, todo lo anterior es decorado.

---

## 3. El workflow

`templates/ci-tests.yml`. Lo que hace, y por qué cada paso:

| Paso | Para qué |
|---|---|
| `setup-dotnet` con el TFM de `parametros-tests.env` | Que la versión del SDK no esté escrita a mano en 40 workflows (misma política que ADR-017 D2) |
| Verificar que el TFM del test **coincide** con el de la app | `E-CS-03`: proyecto de test en otro escalón = solución que no compila |
| `dotnet test` de Unit + Caracterización con `--collect` | El gate |
| **Contar los tests ejecutados y fallar si son 0** | `T-CI-01` |
| **Fallar si el PR modifica un `.verified.*` y además toca `.csproj`** | `T-SNAP-01`: nadie regenera un snapshot dentro de un PR de migración |
| Buscar patrones de secreto en `tests/` | `T-SEC-01` |
| Publicar resultados (`.trx`) y cobertura como artefactos + resumen | Que el revisor del PR vea el resultado sin abrir logs |
| Integración condicionada a que haya Docker | `T-TC-01` |

**Sin secretos.** El workflow no usa `secrets.*` para nada: ni DSN, ni conexiones, ni
token del tracker. Si algún día hiciera falta uno, deja de ser el workflow de tests.

---

## 4. Convención de nombres y ubicación

```
<repo>/tests/<Proyecto>.Tests.<Unit|Caracterizacion|Integracion|Contrato>/
```

- **Siempre `tests/` en la raíz del repo.** No `src/Tests`, no al lado del `.csproj` de la
  app, no en otro repo. Un lugar, en todos los componentes de la flota.
- **Namespace** = nombre del proyecto de test.
- **Archivo** = `<ClaseEnPrueba>Tests.cs`.
- **Test** = `Metodo_Escenario_ResultadoEsperado`, en español y sin abreviar:
  `Desencriptar_ValorExistenteEnBase_DevuelveElTextoOriginal`.
- **Categorías** con `Trait`: `unit`, `caracterizacion`, `integracion`, `contrato`.
  Permite `dotnet test --filter "categoria!=contrato"` sin listar proyectos.
- **Rama**: la del componente. En `micro-api-back`, `develop_docker_net10`.
- **Un commit propio para los tests.** Nunca en el mismo commit que la migración.

---

## 5. Definition of Done

Se completa `reference/checklist.md`; esto es el resumen de lo que no se negocia.

### 5.1 De la suite

- [ ] Unit + Caracterización corren **en local sin Docker, sin red y sin ambiente**, y en CI.
- [ ] La integración corre en local con Docker, o está **declarada como no viable** con el
      motivo (`T-DB-04` es un motivo válido; "no tuve tiempo" no).
- [ ] La suite pasa **dos veces seguidas** y también con paralelismo desactivado (`T-FLAKE-01`).
- [ ] La suite pasa con `TZ=UTC` y con la TZ del ambiente (`T-TIME-01`).
- [ ] Cero secretos, cero datos reales de cliente (`T-SEC-01`).
- [ ] Cada `[Skip]` tiene motivo escrito en el atributo y, si corresponde, un ticket.
- [ ] El CI **falla si se ejecutan 0 tests** (`T-CI-01`).

### 5.2 De la cobertura por riesgo

- [ ] Auth: emisión, validación, **token de oro**, firma inválida, expirado, arranque sin clave.
- [ ] Dinero: todos los cálculos identificados en el análisis, con sus bordes.
- [ ] Cifrado: vectores de ida y de vuelta, incluido **descifrar un valor con el formato
      que hay en la base hoy**.
- [ ] Fechas/cultura/TZ: formato de salida, parseo de entrada, monto formateado.
- [ ] Contrato: snapshot de OpenAPI de **cada** documento publicado + golden-file de los
      endpoints que el inventario marca como consumidos.

### 5.3 Si esto es la red de seguridad de una migración

- [ ] Los tests están **mergeados antes** de que empiece la migración (SKILL §5).
- [ ] La suite pasa en el TFM **actual**.
- [ ] Después de migrar, **los mismos tests, sin un solo cambio**, pasan en el TFM destino.
- [ ] El `git diff` del PR de migración **no toca** ningún archivo bajo `tests/` salvo el
      `<TargetFramework>` del `.csproj` (`E-CS-03`).

### 5.4 De los gates

- [ ] **(gate) cybersec** — si la suite cubre JWT, cifrado o certificados. Firmado por: ____
- [ ] **(gate) dba** — si se pidió un dump de estructura para Testcontainers. Firmado por: ____
- [ ] **(gate) QA** — QA valida que la suite cubre lo que a QA le importa, y **sigue
      validando funcionalmente con capturas**: la suite no reemplaza ese gate. Firmado por: ____
- [ ] **(gate) infra** — si se cambió el `Dockerfile` por `T-DOCK-01`. Firmado por: ____

### 5.5 Del cierre

- [ ] Informe en `{coordinacion}/inventario/tests/<repo>.md`.
- [ ] Errores citados **por código** (`T-*`), y entradas nuevas agregadas al catálogo.
- [ ] Entradas **[G]** que se ejecutaron de verdad, repromovidas a **[V]**.
- [ ] **Lista explícita de lo que NO quedó cubierto**, con el motivo. Sin esto el informe
      está incompleto: alguien va a leer "tiene tests" y asumir una red que no existe.
- [ ] Handoff al lead.

---

## 6. Relación con SonarQube (ADR-015)

Si el piloto de SonarQube avanza, el reporte de cobertura de esta skill es **su insumo**:
`coverlet` produce `cobertura.xml`, que Sonar consume. Dos cosas para no duplicar trabajo:

- La **exclusión** de DTOs/entidades/`Program.cs` se define una sola vez, en
  `coverage.runsettings`, y Sonar la respeta.
- El **quality gate de Sonar no reemplaza** al gate por riesgo de §2. Sonar mide líneas;
  esta skill mide si lo que cuesta plata está cubierto. Son preguntas distintas.
