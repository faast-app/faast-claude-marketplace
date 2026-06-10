# Dev Team — Guia de Uso

Equipo completo de desarrollo con 11 agentes IA que cubre todo el ciclo de vida del
software: desde la Historia de Usuario hasta el deploy, con QA automatizado y
documentacion. Funciona con proyectos **nuevos o existentes**, en **mono-repo o
multi-repo**, con backlog en **GitHub o Azure DevOps**.

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
(git, Docker, gh/az, cliente de BD, Playwright) y **ofrece instalar lo que falte**.
Nunca te vas a topar con un error criptico por una herramienta faltante.

---

## El equipo: 11 agentes

| Agente | Rol | Modelo |
|--------|-----|--------|
| 🔧 **setup** | Valida e instala prerequisitos, configura conexiones BD y tracker | haiku |
| 📋 **product-owner** | Escribe HUs de negocio con criterios de aceptacion, gestiona el backlog en GitHub/Azure | sonnet |
| 🏛️ **architect** | Diseña la arquitectura: topologia (mono/multi), servicios, stack, BD, gateway | opus |
| 🎯 **lead** | Coordina al equipo, asigna tareas, exige gates de calidad, unico que mergea | sonnet |
| ⚙️ **backend** | Implementa servicios backend (.NET 8, Node.js, Python, Java) | sonnet |
| 🎨 **frontend** | Implementa SPA y microfrontends (React, Vue, Angular) | sonnet |
| 🗄️ **dba** | Diseña esquemas, optimiza queries, revisa migraciones | sonnet |
| 🧪 **qa** | Valida HUs contra sus criterios, automatiza E2E con Playwright | sonnet |
| 🚀 **infra** | Docker, CI/CD, gateways, deploy | sonnet |
| 🔒 **cybersec** | Audita seguridad; nunca commitea, reporta hallazgos | sonnet |
| 📚 **tech-writer** | README, OpenAPI, ADRs, diagramas, wiki | haiku |

> Los modelos estan asignados para optimizar costo: `opus` solo donde el razonamiento
> complejo lo amerita, `haiku` para tareas mecanicas.

### Reglas del equipo (siempre activas)
- **El PO escribe HUs de negocio** — el "como tecnico" nunca aparece en una HU
- **QA es gate de merge** — nada llega a main sin que QA apruebe los criterios de aceptacion
- **Cybersec es gate de merge** en features que tocan auth o datos sensibles
- **Solo el Lead mergea** a develop/main
- **Un agente = un branch = una tarea**
- **Cybersec nunca commitea** — reporta y otro agente implementa el fix

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
| `/dev-team:new-project {doc o idea}` | Proyecto nuevo: arquitectura → repos → backlog de HUs |
| `/dev-team:onboard {nombre}` | Hereda un proyecto existente (detecta repos, trae tickets) |
| `/dev-team:setup` | Valida/instala prerequisitos (tambien: `setup db`, `setup tracker`, `setup playwright`) |

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
| `/dev-team:test-plan {HU}` | QA genera el plan de pruebas desde los criterios de aceptacion |
| `/dev-team:e2e {HU\|run\|explorar url}` | QA valida con Playwright (interactivo) y automatiza la suite E2E |
| `/dev-team:review-pr {n}` | Revision de codigo de un PR |
| `/dev-team:security-audit` | Auditoria de seguridad |
| `/dev-team:git-check` | Verificacion git antes de commitear |

### Operacion
| Comando | Que hace |
|---------|----------|
| `/dev-team:db-health` | Health check de base de datos (esquema, indices, slow queries) |
| `/dev-team:deploy-check` | Verifica readiness para deploy |
| `/dev-team:document {tema}` | Tech Writer actualiza documentacion tecnica |

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
7. Listo: `/dev-team:assign-task` para empezar a trabajar

## Flujo B: Heredar un proyecto existente

```
/dev-team:onboard backoffice
```

1. **setup** valida entorno y pregunta: ¿GitHub, Azure DevOps o solo local?
2. Detecta los repos (locales y remotos), analiza stack y estructura de cada uno
3. Detecta la topologia (mono/multi) — **nunca propone migrarla**
4. Configura el acceso del DBA a la BD (motor, credenciales, prueba de conexion)
5. Trae los tickets reales del tracker y arma el backlog
6. Listo: el equipo conoce tu proyecto y puede trabajar

## Flujo C: Una feature de principio a fin

```
/dev-team:refine "los analistas necesitan filtrar cobranzas por fecha"
```

```
1. PO escribe la HU (negocio + criterios Gherkin) ──► la crea en GitHub/Azure
2. Lead asigna: backend + frontend implementan ──► QA prepara el plan de pruebas en paralelo
3. Devs terminan ──► handoff a QA
4. QA valida cada criterio con Playwright (evidencia) y automatiza la suite E2E
5. Cybersec audita (solo si toca auth/datos sensibles)
6. Lead verifica gates: CI verde + QA aprobo + seguridad OK ──► merge
7. /dev-team:sync push ──► PR mergeado, HU a Done en el tracker
8. tech-writer actualiza la documentacion
```

## Flujo D: Reportar y corregir un bug

```
/dev-team:start hay un bug en la paginacion de cobranzas
```

1. **Lead** hace triaje: ¿que componente falla? ¿severidad?
2. **QA** lo reproduce con Playwright y documenta los pasos exactos
3. Se registra el Bug en el tracker, el Lead lo asigna con branch `fix/...`
4. El dev corrige; **QA escribe el test de regresion** que cubre el bug
5. Lead mergea cuando el test pasa; el bug no vuelve

## Flujo E: Pruebas

```
/dev-team:test-plan HU-042       # plan de pruebas desde los criterios
/dev-team:e2e HU-042             # valida y automatiza esa HU
/dev-team:e2e run                # corre la regresion completa
/dev-team:e2e explorar http://localhost:3000   # prueba exploratoria libre
```

QA trabaja en dos modos:
- **Interactivo** (Playwright MCP): navega la app real, valida criterios, captura evidencia
- **Automatizado** (suite Playwright): tests en codigo que corren en CI en cada PR

Cada criterio de aceptacion de la HU se convierte en al menos un test (trazabilidad
HU → criterio → test).

## Flujo F: Base de datos

```
/dev-team:db-health          # configura conexion si falta, luego health check
/dev-team:db-health full     # esquema, indices, slow queries, tamaños
```

Si el DBA encuentra problemas, crea handoff al Lead → el Lead asigna la correccion.

---

## Configuracion del proyecto

Todo vive en `.coordination/config.json` (lo crean new-project/onboard — no lo
escribas a mano salvo que quieras cambiar algo):

```json
{
  "project": "backoffice",
  "topology": "multi",
  "tracker": {
    "provider": "github",
    "github": { "org": "faast-app", "project": "BackOffice" }
  },
  "urls": { "dev": "http://localhost:3000" }
}
```

| Campo | Valores | Efecto |
|-------|---------|--------|
| `topology` | `mono` / `multi` | Como trabajan los agentes (carpetas vs repos) y donde vive `.coordination/` |
| `tracker.provider` | `github` / `azure` | Donde el PO crea HUs y donde sincroniza `/sync` |

Archivos que NUNCA van a git: `.coordination/dba-access.json` (credenciales BD) y
`.coordination/setup-status.json`.

---

## Preguntas frecuentes

**¿Tengo que saber que agente invoca cada cosa?**
No. Usa `/dev-team:start` y describe lo que necesitas. El equipo enruta solo.

**¿Funciona sin GitHub ni Azure DevOps?**
Si — elige "solo local" en el onboard. El backlog vive en `.coordination/backlog.md`.
Puedes conectar un tracker despues con `/dev-team:setup tracker`.

**¿Que pasa si no tengo Playwright/Docker/gh instalado?**
El agente setup lo detecta y te ofrece instalarlo. Nada falla en silencio.

**¿Puedo usar solo una parte del equipo?**
Si. Cada comando funciona independiente: solo `/db-health` para BD, solo `/refine`
para HUs, solo `/e2e` para pruebas.

**¿El equipo respeta mi proyecto tal como esta?**
Si. En onboard nunca se propone cambiar topologia, stack ni convenciones existentes
salvo que lo pidas.

**¿Como cambio de GitHub a Azure DevOps (o al reves)?**
Edita `tracker.provider` en `.coordination/config.json` y ejecuta
`/dev-team:setup tracker` para validar la autenticacion del nuevo proveedor.
