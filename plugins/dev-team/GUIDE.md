# Dev Team — Manual de Usuario (v2.2)

Equipo completo de desarrollo con **15 agentes IA** que cubre todo el ciclo de vida
del software: Historia de Usuario → diseño UI/UX → arquitectura → desarrollo →
QA en equipo con evidencia → seguridad → **pases a ambientes** → deploy →
documentacion, con una **wiki viva** del proyecto y una **oficina virtual en vivo**
para ver al equipo trabajar. Funciona con proyectos **nuevos o existentes**, en
**mono-repo o multi-repo**, con backlog en **GitHub o Azure DevOps**.

---

## Indice

1. [Instalacion](#instalacion)
2. [Inicio rapido](#inicio-rapido--un-solo-comando)
3. [El equipo: 15 agentes](#el-equipo-15-agentes)
4. [Comandos (22)](#comandos)
5. [Flujos de trabajo](#flujo-a-proyecto-nuevo)
6. [La wiki del proyecto](#la-wiki-del-proyecto-patron-llm-wiki)
7. [La oficina virtual](#la-oficina-virtual-team-office)
8. [Metricas del equipo](#metricas-del-equipo-team-metrics)
9. [Pases a ambientes](#pases-a-ambientes-pase)
10. [Configuracion](#configuracion-del-proyecto)
11. [Preguntas frecuentes](#preguntas-frecuentes)

---

## Instalacion

```bash
# 1. Agregar el marketplace (una sola vez)
/plugin marketplace add faast-app/faast-claude-marketplace

# 2. Instalar el plugin
/plugin install dev-team@faast-marketplace

# 3. Actualizar cuando haya cambios
/plugin marketplace update faast-marketplace
/plugin update dev-team
```

---

## Inicio rapido — un solo comando

No necesitas memorizar nada. Escribe:

```
/dev-team:start
```

El equipo detecta tu situacion y te guia:
- **No hay proyecto** → te ofrece crear uno nuevo o heredar uno existente
- **Hay proyecto** → te muestra el estado y te propone la siguiente accion
- **Pediste algo especifico** → `/dev-team:start quiero agregar un filtro de fechas`
  y el equipo enruta tu pedido al agente correcto

Antes de cualquier trabajo, el agente **setup** valida que tengas todo instalado
(git, Docker, gh/az, cliente de BD, Playwright, Node) y **ofrece instalar lo que
falte**. Nunca te vas a topar con un error criptico por una herramienta faltante.

---

## El equipo: 15 agentes

| Agente | Rol | Modelo |
|--------|-----|--------|
| 🧰 **setup** | Valida e instala prerequisitos, configura conexiones BD y tracker | haiku |
| 📋 **product-owner** | HUs de negocio con criterios de aceptacion; items de entregable ricos en GitHub/Azure | sonnet |
| 📐 **architect** | Arquitectura: topologia (mono/multi), servicios, stack, BD, gateway | sonnet (opus opcional) |
| 🎨 **ui-designer** | Mockups y specs UI/UX: paletas (contraste WCAG), tipografia, estados, accesibilidad | sonnet |
| 🎯 **lead** | Coordina, asigna, exige gates de calidad, unico que mergea | sonnet |
| ⚙️ **backend** | Servicios backend (.NET 8, Node.js, Python, Java) | sonnet |
| 🖥️ **frontend** | SPA y microfrontends (React, Vue, Angular) | sonnet |
| 🗄️ **dba** | Esquemas, indices, migraciones, **scripts de pase**, **comparacion de BDs** | sonnet |
| 🔎 **qa** (QA Lead) | Plan de pruebas, reparte a los especialistas, consolida el veredicto, suite E2E | sonnet |
| 🖱️ **qa-frontend** | Especialista QA de UI: Playwright MCP, responsive, evidencia visual | sonnet |
| 🔌 **qa-backend** | Especialista QA de APIs: contract testing contra OpenAPI, permisos, bordes | sonnet |
| 📦 **release-manager** | Solicitudes de pase (Word+PDF), **audita los scripts del DBA**, Scripts.zip | sonnet |
| 🚢 **infra** | Docker, CI/CD, gateways, deploy | sonnet |
| 🛡️ **cybersec** | Audita seguridad; nunca commitea, reporta hallazgos | sonnet |
| 📚 **tech-writer** | Docs tecnicas + **mantenedor de la wiki del proyecto** | haiku |

> Los modelos estan asignados para optimizar costo: `haiku` para trabajo
> mecanico, `sonnet` para el resto. Nunca se usa fable ni opus por defecto.
>
> **Modelo configurable por proyecto:** en `.coordination/config.json` puedes
> subir o bajar el modelo de cualquier agente SOLO para ese proyecto:
> ```json
> "team": { "models": { "architect": "opus", "cybersec": "haiku" } }
> ```
> El lead (y los flujos) pasan ese valor como override al invocar al agente.
> Valores: `haiku` | `sonnet` | `opus`. Util para equipos con limites ajustados
> (todo en sonnet) o proyectos complejos (architect en opus).
>
> **Config personal (global a TUS proyectos):** el mismo bloque en
> `~/.claude/dev-team.config.json` aplica en toda tu maquina; el config del
> proyecto tiene prioridad sobre el personal.
> **Excepcion fija:** los agentes con default `haiku` (setup, tech-writer) NO son
> configurables — su modelo no se altera y cualquier entrada para ellos se ignora.

### Reglas del equipo (siempre activas)

- **El PO redacta TODO en lenguaje funcional de negocio** — HUs, bugs e items que
  entiende QA o cualquier persona no programadora: sin codigo, sin jerga, titulos
  limpios sin codigos raros (parametros funcionales si, como los ve el usuario).
  Lo tecnico va al final o en los handoffs, nunca en la narrativa
- **Se trabaja con Scrum** — sprints con Sprint Goal, story points (1-8), backlog
  priorizado por valor, refinamiento antes del planning, review y retrospectiva
- **QA es un equipo y es gate de merge** — nada llega a main sin veredicto APROBADA
- **REGLA DE ORO FIJA E INALTERABLE — QA no valida sin informe de conformidad**:
  para ambientes desplegados exige el informe (que se desplego, version exacta,
  health OK); en desa exige el stack COMPLETO levantado. Replica en el ambiente qa
  siempre que este disponible. Nadie puede saltarse este flujo
- **LEY QA: a la primera falla, reporta** — si algo no funciona al primer intento,
  evidencia + `blocked` + reporte inmediato; prohibido reintentar, buscar
  workarounds o probar fuera de su alcance (criterios asignados, ambiente
  validado, credenciales dadas)
- **QA no debuggea** — reproduce, documenta y reporta (bloqueantes de inmediato),
  SIEMPRE con evidencia: screenshots o clips cortos, adjuntos al item del tracker
- **Cybersec es segundo gate** en features que tocan auth o datos sensibles y nunca commitea
- **Solo el Lead mergea** a develop/main; un agente = un branch = una tarea
- **El release-manager es gate de pases** — audita el formato de los scripts del
  DBA y puede rechazarlos hasta que cumplan
- **PLAN PRIMERO** — antes de ejecutar una feature o un fix (flujos C y D), el
  Lead presenta el plan (que/quien/donde/riesgos) y espera tu confirmacion;
  puedes ajustar o pedir otro abordaje. Nada se ejecuta sin tu OK
- **Nada de personas hardcodeadas** — nombres, correos, reviewers, "elaborado
  por": SIEMPRE del config del proyecto o preguntando; jamas copiados de un
  ejemplo, de otro proyecto o inventados
- **Los devs preguntan antes de abrir PR** — no todo entregable lleva PR
- **Solo el Lead delega en subagentes** — puede lanzar a cualquier agente del
  equipo, incluso varias instancias del mismo rol en paralelo (2 backend en HUs
  distintas), nunca otro lead. Los demas agentes ejecutan su trabajo directamente
  (herramienta deshabilitada + hook que bloquea el intento; unica excepcion:
  Explore, busqueda barata de solo-lectura). Esto evita el desperdicio de tokens
  de un backend lanzando 3 backends anidados
- **Wiki primero** — todos los agentes leen `.coordination/wiki/` antes de cada
  tarea (menos tokens, mas contexto); solo el tech-writer la escribe
- **Todo queda registrado AUTOMATICAMENTE** — hooks del plugin escriben
  `task_start`/`task_end` en `.coordination/metrics/activity.jsonl` cada vez que
  un agente arranca o termina (sin depender de que el agente se acuerde); los
  agentes agregan lo demas (handoffs, bloqueos, evidencia). Alimenta metricas y
  la oficina virtual

---

## Comandos

### Los 3 que usaras todos los dias
| Comando | Que hace |
|---------|----------|
| `/dev-team:start` | Punto de entrada universal: detecta contexto y te guia |
| `/dev-team:status` | Estado del proyecto: sprint, backlog, handoffs, bloqueos |
| `/dev-team:sync` | Sincroniza con GitHub/Azure: trae tickets, sube avances, crea PRs |

### Crear o adoptar proyectos
| Comando | Que hace |
|---------|----------|
| `/dev-team:new-project {doc o idea}` | Proyecto nuevo: arquitectura → repos → backlog → wiki |
| `/dev-team:onboard {nombre}` | Hereda un proyecto existente (detecta repos, trae tickets) |
| `/dev-team:setup` | Valida/instala prerequisitos (`setup db`, `setup tracker`, `setup playwright`) |

### Backlog y trabajo
| Comando | Que hace |
|---------|----------|
| `/dev-team:refine {pedido}` | El PO convierte tu pedido en HUs y las crea en el tracker |
| `/dev-team:assign-task` | El Lead asigna HUs/tickets a los agentes |
| `/dev-team:inbox` | Un agente lee sus tareas y handoffs pendientes |
| `/dev-team:handoff` | Crear comunicacion entre agentes |

### Calidad
| Comando | Que hace |
|---------|----------|
| `/dev-team:test-plan {HU}` | QA genera el plan de pruebas desde los criterios |
| `/dev-team:e2e {HU\|run\|explorar url}` | QA valida con Playwright y automatiza la suite E2E |
| `/dev-team:review-pr {n}` | Revision de codigo de un PR |
| `/dev-team:security-audit` | Auditoria de seguridad |
| `/dev-team:git-check` | Verificacion git antes de commitear |

### Operacion y releases
| Comando | Que hace |
|---------|----------|
| `/dev-team:db-health` | Health check de BD (esquema, indices, slow queries) |
| `/dev-team:deploy-check` | Verifica readiness para deploy |
| `/dev-team:pase {ambiente}` | **Solicitud de pase completa**: documento Word+PDF + Scripts.zip auditado |
| `/dev-team:document {tema}` | Tech Writer actualiza documentacion tecnica |

### Conocimiento y visibilidad
| Comando | Que hace |
|---------|----------|
| `/dev-team:wiki {init\|ingest\|lint\|query}` | Wiki viva del proyecto (vault de Obsidian) |
| `/dev-team:team-office` | **Oficina virtual 2D en vivo** — ve al equipo trabajar |
| `/dev-team:team-metrics` | Productividad y consumo de tokens por agente |

---

## Flujo A: Proyecto nuevo

```
/dev-team:new-project docs/requerimientos.docx
```

1. **setup** valida tu entorno (instala lo que falte, con tu OK)
2. **architect** analiza los requerimientos y propone: topologia (mono o multi-repo),
   servicios, stack, BD, gateway — con diagrama y justificacion
3. **Tu apruebas o ajustas** ("prefiero mono-repo", "usa MySQL", "quita el servicio X")
4. Eliges tracker: **GitHub Projects** o **Azure DevOps Boards**
5. Se crean los repos/carpetas con scaffolding completo (Dockerfile, CI/CD, tests)
6. **product-owner** convierte los requerimientos en HUs reales en tu tracker
7. Se crea la **wiki** (`/wiki init`) y la carpeta de metricas
8. Listo: `/dev-team:assign-task` para empezar a trabajar

## Flujo B: Heredar un proyecto existente

```
/dev-team:onboard backoffice
```

1. **setup** valida entorno y pregunta: ¿GitHub, Azure DevOps o solo local?
2. Detecta los repos (locales y remotos), analiza stack y estructura de cada uno
3. Detecta la topologia (mono/multi) — **nunca propone migrarla**
4. Configura el acceso del DBA a la BD (motor, credenciales, prueba de conexion)
5. Trae los tickets reales del tracker y arma el backlog
6. Crea la wiki e ingiere lo detectado (arquitectura, backlog, mapa de repos)
7. Listo: el equipo conoce tu proyecto y puede trabajar

## Flujo C: Una feature de principio a fin

```
/dev-team:refine "los analistas necesitan filtrar cobranzas por fecha"
```

```
0. PLAN PRIMERO: el Lead presenta que se hara, quien, donde y riesgos ──► TU confirmas
   (o pides ajustes / otro abordaje) — nada se ejecuta sin tu OK
1. PO escribe la HU (negocio + criterios Gherkin) ──► la crea en GitHub/Azure
2. (Si hay pantallas nuevas) ui-designer propone mockups ──► tu eliges ──► spec a frontend
3. Lead asigna: backend + frontend implementan ──► QA prepara el plan de pruebas en paralelo
   · Los devs preguntan si el entregable lleva PR antes de abrir nada
   · Rama SIEMPRE desde origin/{defaultBranch} + version bump + UN PR consolidado
4. Devs terminan ──► handoff a QA
5. QA Lead reparte: qa-frontend valida criterios de UI y qa-backend los de API — EN PARALELO
   · Todo con evidencia (screenshots/clips) · sin debuggear · bloqueantes al instante
6. Cybersec audita (solo si toca auth/datos sensibles)
7. Lead verifica gates: CI verde + QA aprobo + seguridad OK ──► merge
8. /dev-team:sync push ──► PR mergeado, HU a Done, descripcion rica item↔PR alineada
9. tech-writer documenta e ingiere todo a la wiki
```

## Flujo D: Reportar y corregir un bug

```
/dev-team:start hay un bug en la paginacion de cobranzas
```

1. **Lead** hace triaje: ¿que componente falla? ¿severidad?
2. **QA** lo reproduce (sin debuggear): pasos exactos + screenshots/clip
   — y ANTES de pasar a corregir, el Lead te presenta el PLAN del fix
   (que/quien/donde/riesgos) y espera tu confirmacion; puedes pedir otro abordaje
3. El PO registra el Bug en el tracker **con la evidencia adjunta**; el Lead lo
   asigna con branch `fix/...`
4. El dev corrige (la causa raiz es SU trabajo, no de QA); **QA escribe el test de
   regresion** que cubre el bug
5. Lead mergea cuando el test pasa; el bug no vuelve

## Flujo E: Pruebas

```
/dev-team:test-plan HU-042       # plan de pruebas desde los criterios
/dev-team:e2e HU-042             # valida y automatiza esa HU
/dev-team:e2e run                # corre la regresion completa
/dev-team:e2e explorar http://localhost:3000   # prueba exploratoria libre
```

El equipo QA trabaja en dos modos:
- **Interactivo** (Playwright MCP): navega la app real, valida criterios, captura evidencia
- **Automatizado** (suite Playwright): tests en codigo que corren en CI en cada PR

Cada criterio de aceptacion = al menos un test (trazabilidad HU → criterio → test).
La evidencia queda en `.coordination/evidence/{HU|BUG}/` y, si es un bug, adjunta
al item del tracker.

## Flujo F: Base de datos

```
/dev-team:db-health          # configura conexion si falta, luego health check
/dev-team:db-health full     # esquema, indices, slow queries, tamaños
```

Ademas el DBA puede:
- **Comparar dos bases de datos** (dev vs cert, cliente A vs cliente B): schema
  diff, charset, data de catalogos y volumenes — en modo **estrictamente
  solo-lectura** (jamas escribe en las BDs comparadas). Pideselo via
  `/dev-team:start compara la BD de dev contra la de certificacion`
- **Preparar scripts de pase** en el formato global: archivos numerados por tipo
  (`1_createTable.sql` … `7_update.sql`), 100% idempotentes (re-ejecutables N
  veces), insert-only, DB-agnosticos, con acentos/ñ intactos (UTF-8 verificado)

## Flujo G: Pase a un ambiente

```
/dev-team:pase preprod PE
```

1. El **release-manager** recopila: ambiente destino (si es productivo, ¿que
   cliente?), componentes y versiones, ¿lleva scripts de BD?
2. Si lleva scripts: **audita el paquete del DBA** contra el checklist del formato
   global — si algo falla, lo **rechaza y devuelve** al DBA con archivo+linea+regla
3. Con auditoria aprobada: consolida **`Scripts.zip`** (los .sql numerados en la raiz)
4. Llena la **solicitud de pase** desde la plantilla oficial y la exporta a PDF
5. Entrega la **carpeta de pase** completa:
   ```
   Release v1.0.0 09julio2026 - Notificaciones Cobranza/
   ├── Solicitud de Pase Ambientes - Preprod PE.pdf
   ├── Solicitud de Pase Ambientes - Preprod PE.docx
   └── Scripts.zip
   ```

El documento es **obligatorio** para: certificacion, puente, demo (Chile/Peru/
Colombia), preprod (CO/PE) y productivos de cliente. Para ambientes internos, solo
si lo pides.

## Flujo H: Diseño de pantallas

```
/dev-team:start necesito la pantalla de resumen de cobranzas
```

1. **ui-designer** detecta tu sistema de diseño actual (tailwind config, tokens,
   pantallas existentes via screenshot)
2. Te entrega **2-3 propuestas de mockup** (HTML que abres en el browser) + spec
   completa: paleta con contraste WCAG verificado, tipografia, espaciado, estados
   (loading/error/empty/success), responsive
3. Eliges una → la spec pasa a **frontend** para implementar exactamente eso

---

## La wiki del proyecto (patron LLM Wiki)

`.coordination/wiki/` es la **memoria viva del proyecto** (patron LLM Wiki de
Karpathy): en vez de que cada agente re-lea decenas de handoffs viejos, el
**tech-writer destila** todo a paginas canonicas enlazadas con `[[wikilinks]]`.

```
wiki/
├── index.md            # portada con el mapa del proyecto
├── servicios/          # estado vivo de cada servicio (stack, contratos, BD)
├── hus/                # una pagina por HU con su historia completa
├── bugs/               # reproduccion, evidencia, fix
├── decisiones/         # ADRs
├── pases/              # que se paso, a donde, con que scripts
└── agentes/            # memoria por rol
```

**Comandos:**

```
/dev-team:wiki init      # crear la wiki (una vez; new-project/onboard lo hacen solos)
/dev-team:wiki ingest    # destilar los handoffs/reportes nuevos (hazlo al final del dia)
/dev-team:wiki lint      # salud: links rotos, huerfanos, paginas desactualizadas
/dev-team:wiki query ¿por que elegimos MySQL para cobranzas?   # responde citando paginas
```

**Con Obsidian:** abre `.coordination/wiki/` como vault → tienes **graph view** del
conocimiento del proyecto (HUs ↔ servicios ↔ bugs ↔ decisiones) gratis.

**Por que importa:** cada `ingest` (lo hace tech-writer, que es haiku = barato)
hace que la siguiente tarea de cualquier agente sea mas barata y con mejor
contexto. El conocimiento compone.

---

## La oficina virtual (team-office)

```
/dev-team:team-office
```

Abre `http://localhost:4321`: una **oficina 2D en vivo** (estilo Gather Town) con
los 15 agentes en sus salas:

- 🟢 **Trabajando**: arco giratorio, burbuja de "escribiendo…", monitor parpadeando
  y su tarea actual debajo
- 🔴 **Bloqueado**: anillo rojo pulsante con 🚫
- ✉️ **Handoffs**: el agente **camina** hasta el escritorio del destinatario a
  entregar el sobre (📬 pop al recibir)
- ✅ **Tarea completada**: confetti
- Panel lateral: equipo ordenado por estado, handoffs pendientes, feed de actividad
- Header: contadores en vivo (trabajando / bloqueados / handoffs / eventos)

**Controles:** rueda = zoom · arrastrar = mover · doble-click = vista general ·
click en un agente = la camara lo sigue.

**Como funciona:** un servidor Node local sin dependencias que solo LEE
`.coordination/` (eventos de `metrics/activity.jsonl` + carpeta `handoffs/`) y
empuja cambios por SSE. Cero tokens, cero escritura.

**El registro es automatico:** los hooks del plugin (`SubagentStart`/`SubagentStop`)
escriben el evento cada vez que un agente dev-team arranca o termina — veras a
los agentes encenderse en la oficina sin que ellos hagan nada. Requiere reiniciar
la sesion de Claude Code tras instalar/actualizar el plugin (los hooks se cargan
al inicio).

---

## Metricas del equipo (team-metrics)

```
/dev-team:team-metrics            # dashboard del sprint
/dev-team:team-metrics --watch    # modo live
```

El Lead genera un ranking por agente: tareas completadas, handoffs, commits,
**lead time real** (task_start → task_end del event log), tokens consumidos y
costo estimado segun el modelo de cada agente. Cierra con recomendaciones
(rebalancear carga, bajar/subir modelo de un agente, handoffs estancados).

> Fuente primaria: `metrics/activity.jsonl`. Los tokens se estiman desde los
> transcripts de Claude Code; si no estan disponibles se reporta "sin datos" —
> nunca cifras inventadas.

---

## Pases a ambientes (pase)

Resumen de reglas que el equipo aplica solo (detalle en el Flujo G):

| Regla | Detalle |
|-------|---------|
| Scripts agrupados por TIPO | `1_createTable` `2_alterTable_add` `3_alterTable_modify` `4_views` `5_insertInto` `6_procedures` `7_update` |
| Idempotencia total | Re-ejecutable N veces: `IF NOT EXISTS`, guards por `information_schema`, INSERT solo con `WHERE NOT EXISTS` |
| Insert-only | Prohibido `ON DUPLICATE KEY UPDATE` / `REPLACE INTO` — un pase jamas toca datos ya cargados |
| DB-agnostico | Sin `mi_db.tabla`; corre contra la BD conectada de cualquier ambiente/cliente |
| FKs externos por natural key | Nunca ids literales de catalogos (roles, monedas…) — cambian por ambiente |
| Acentos intactos | UTF-8 en todo; deteccion de mojibake antes de entregar |
| Gate de auditoria | El release-manager verifica TODO el checklist; si falla, rechaza y el DBA corrige |
| Entregable | Carpeta `Release vX.Y.Z {fecha} - {Proyecto}/` con PDF + Word + Scripts.zip |

---

## Configuracion del proyecto

Todo vive en `.coordination/config.json` (lo crean new-project/onboard):

```json
{
  "project": "backoffice",
  "topology": "multi",
  "tracker": {
    "provider": "azure",
    "azure": { "org": "faast", "project": "BackOffice" },
    "reviewer": "{email-del-reviewer}",
    "overheadEpicId": 1234,
    "areaPath": "BackOffice\\Fintec",
    "iterationPath": "BackOffice\\Sprint 12"
  },
  "git": {
    "defaultBranch": "develop",
    "identity": { "name": "{Nombre Apellido}", "email": "{email-del-proyecto}" }
  },
  "pase": {
    "templatePath": "(opcional — default: plantilla del plugin)",
    "outputDir": "(opcional — default: .coordination/pases/)"
  },
  "team": {
    "models": { "architect": "opus" }
  },
  "urls": { "dev": "http://localhost:3000" }
}
```

| Campo | Efecto |
|-------|--------|
| `topology` | `mono`/`multi`: como trabajan los agentes y donde vive `.coordination/` |
| `tracker.provider` | `github`/`azure`: donde viven HUs, items y PRs |
| `tracker.reviewer` | Reviewer que los devs ponen en cada PR |
| `tracker.overheadEpicId` | Epica/PBI padre para fixes sueltos sin epica propia |
| `git.defaultBranch` | Rama base OBLIGATORIA para ramificar (via `git fetch origin`) |
| `git.identity` | Identidad de commits del proyecto (no la default del agente) |
| `pase.*` | Plantilla y carpeta de salida de las solicitudes de pase |
| `team.models.{agente}` | Override de modelo por agente en ESTE proyecto (`haiku`/`sonnet`/`opus`) — ej. architect a opus. No aplica a los de default haiku (setup, tech-writer): esos son fijos |

**Estructura completa de `.coordination/`:**

```
.coordination/
├── config.json          # fuente de verdad (arriba)
├── handoffs/ (+archive/)# comunicacion entre agentes
├── wiki/                # wiki viva (vault de Obsidian)
├── metrics/             # activity.jsonl (eventos de los agentes)
├── evidence/            # screenshots/clips de QA
├── pases/               # carpetas de pase entregadas
├── office/              # la oficina virtual (se instala con /team-office)
├── test-plans/          # planes de prueba de QA
├── backlog.md · sprint-actual.md · architecture.md · repos.md
├── dba-access.json      # credenciales BD — NUNCA en git
└── setup-status.json    # estado del entorno — NUNCA en git
```

---

## Como cuidar tu limite de uso (5 horas / semanal)

El equipo dispara subagentes y eso consume tokens — estas practicas mantienen el
consumo sano. Revisa tu panel con `/usage` (pestaña Usage de Settings).

**Habitos que mas ahorran:**
1. **Sesiones cortas por tarea** — el enemigo #1 es el contexto gigante: una sesion
   de 3 horas re-lee 150k+ tokens en CADA turno (aun cacheados, cuentan). Usa
   `/compact` a mitad de tarea larga y `/clear` (o sesion nueva) al cambiar de tema.
2. **Wiki al dia** — `/dev-team:wiki ingest` al cierre del dia hace que la sesion
   de mañana arranque liviana: los agentes leen la pagina canonica (2-3k tokens),
   no el historial completo.
3. **Pregunta directa = respuesta directa** — no uses `/dev-team:start` para
   preguntas simples; el router puede disparar agentes que no necesitas.
4. **Modelo principal en sonnet** (`/model sonnet`) — los agentes ya traen su
   modelo optimizado (opus solo el architect).
5. **MCP solo los necesarios** — `claude mcp list` y quita los que no uses: sus
   esquemas viajan en cada sesion.

**Protecciones automaticas del plugin (v2.5.1+):**
- Los subagentes NO pueden delegar (solo el lead orquesta; hook lo bloquea)
- Los comandos `/dev-team:*` se ejecutan inline, nunca como subagentes (hook lo
  bloquea) — correr `/start` como subagente recargaba todo el contexto
- `task_start`/`task_end` se registran via hooks (cero tokens)

**Leyendo tu `/usage`:**
- "subagents under dev-team:backend" con % bajo = normal (son Explore, busqueda
  barata permitida); % alto = delegacion anidada → actualiza el plugin y reinicia
- "% at >150k context" alto = sesiones demasiado largas → habito 1
- La primera interaccion tras el reset del limite siempre pesa mas (escritura de
  cache fria) — es el peaje de arranque, no una fuga

## Preguntas frecuentes

**¿Tengo que saber que agente invoca cada cosa?**
No. Usa `/dev-team:start` y describe lo que necesitas. El equipo enruta solo.

**¿Funciona sin GitHub ni Azure DevOps?**
Si — elige "solo local" en el onboard. El backlog vive en `.coordination/backlog.md`.
Puedes conectar un tracker despues con `/dev-team:setup tracker`.

**¿Por que QA no arregla los bugs que encuentra?**
Por diseño: QA reproduce y reporta con evidencia; el dev responsable corrige. Asi
la evidencia es objetiva, el fix lo hace quien conoce el codigo, y QA no pierde
tiempo debuggeando.

**¿Que evidencia deja QA y donde queda?**
Screenshots de cada paso y clips cortos (<30s) para lo dinamico, en
`.coordination/evidence/`. Si es un bug, se adjunta al PBI/WI/Issue del tracker.

**¿Que pasa si el DBA entrega scripts mal formateados para un pase?**
El release-manager los rechaza con el detalle exacto (archivo, linea, regla) y el
DBA corrige. Nada se consolida en Scripts.zip hasta que el checklist pase completo.

**¿El DBA puede escribir en las BDs cuando compara dos bases?**
No. La comparacion es solo-lectura por regla dura. Los scripts de nivelacion se
GENERAN como archivos que tu decides cuando ejecutar.

**¿Siempre se crea un PR al terminar una tarea?**
No. Los devs preguntan primero — hay entregables que no llevan PR.

**¿Como veo lo que esta haciendo el equipo ahora mismo?**
`/dev-team:team-office` (oficina visual en vivo) o `/dev-team:status` (texto).
Para numeros: `/dev-team:team-metrics`.

**¿Necesito Obsidian para la wiki?**
No — la wiki es markdown puro y los agentes la usan igual. Obsidian solo agrega
el graph view y una navegacion comoda para humanos.

**¿Que pasa si no tengo Playwright/Docker/gh/Node instalado?**
El agente setup lo detecta y te ofrece instalarlo. Nada falla en silencio.

**¿Puedo usar solo una parte del equipo?**
Si. Cada comando funciona independiente: solo `/db-health` para BD, solo `/refine`
para HUs, solo `/pase` para un release, solo `/e2e` para pruebas.

**¿El equipo respeta mi proyecto tal como esta?**
Si. En onboard nunca se propone cambiar topologia, stack ni convenciones existentes
salvo que lo pidas.

**¿Como cambio de GitHub a Azure DevOps (o al reves)?**
Edita `tracker.provider` en `.coordination/config.json` y ejecuta
`/dev-team:setup tracker` para validar la autenticacion del nuevo proveedor.
