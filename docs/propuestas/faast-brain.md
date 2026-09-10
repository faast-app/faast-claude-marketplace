# Propuesta: FaaST Brain — memoria organizacional compartida del equipo dev-team

**Estado:** propuesta (pendiente de aprobación) · **Fecha:** 2026-09-10 · **Fase sugerida:** 5

## 1. Problema

Hoy la memoria del equipo vive **por proyecto** en `.coordination/wiki/` (patrón LLM Wiki):
cada proyecto recuerda lo suyo, pero nada cruza entre proyectos. Consecuencias reales:

- Una lección aprendida en Confirming 2.0 (ej. colisión de nombres en GHCR) no llega
  a quien arranca Portal Digital — salvo que alguien la copie a mano al plugin.
- Nadie sabe sin preguntar **qué versión de qué componente está en Demo PE hoy** — la
  información está repartida en 15 correos de pase.
- Un dev nuevo (o un agente) que entra a un repo no tiene un lugar único donde leer
  "cómo hacemos las cosas aquí": estándares, decisiones, quién es dueño de qué.
- Los estándares (formato de pases, scripts SQL, arquitectura Docker) viven
  **dentro de los prompts del plugin** — cambiar una regla exige publicar una versión.

## 2. Propuesta en una frase

Un repositorio `faast-app/faast-brain` (git + markdown, vault de Obsidian) que actúa
como **cerebro común**: lo alimentan automáticamente los agentes de dev-team desde
CADA proyecto, lo cura el tech-writer, lo aprueba el owner, y lo consultan agentes y
personas antes de decidir. Dos capas de memoria que se complementan:

| Capa | Dónde | Qué recuerda | Quién escribe |
|---|---|---|---|
| **Wiki del proyecto** (ya existe) | `.coordination/wiki/` de cada proyecto | Lo específico: HUs, bugs, servicios, decisiones locales | tech-writer del proyecto |
| **FaaST Brain** (nuevo) | repo `faast-brain` | Lo transversal: estándares, decisiones org, catálogo de componentes, estado de ambientes, historial de pases, incidentes y lecciones, runbooks, glosario | agentes (automático, a `inbox/`) + tech-writer (curación) + owner (aprobación) |

## 3. Estructura del repo

```
faast-brain/
├── CLAUDE.md                 # esquema y reglas (como el de la wiki de proyecto)
├── index.md                  # portada: mapa del cerebro
├── estandares/               # FUENTE DE VERDAD de las reglas del equipo
│   ├── pases-formato.md      #   (hoy hardcodeado en release-manager.md)
│   ├── scripts-sql.md        #   (hoy en dba.md)
│   ├── arquitectura-docker-monorepo.md   (el estándar v2.0 de Arquitectura Docker)
│   ├── ramas-y-promocion.md
│   └── seguridad-checklist.md
├── decisiones/               # ADRs de alcance organización (no de un proyecto)
├── componentes/              # CATÁLOGO: un archivo por componente desplegable
│   └── ms-backoffice.md      #   repo, owner, stack, BD, ambientes donde vive, versión por ambiente
├── ambientes/                # ESTADO ACTUAL por ambiente
│   ├── demo-cl.md · demo-pe.md · demo-co.md · puente.md · preprod-co.md
│   └── prod-{cliente}.md     #   tabla componente → versión → fecha → pase que la puso
├── releases/                 # HISTORIAL: un archivo por pase (auto, desde release-manager)
│   └── 2026-09-10-demo-co-sprint13-finamco.md
├── incidentes/               # postmortems y lecciones transversales (lo que hoy va a los agentes)
├── runbooks/                 # procedimientos operativos reutilizables
├── proyectos/                # ficha de cada proyecto + link a su wiki local
├── personas/                 # roles y responsabilidades por área (sin datos sensibles)
├── glosario.md               # términos del negocio y técnicos en lenguaje simple
├── inbox/                    # ENTRADAS AUTOMÁTICAS sin curar (los agentes escriben aquí)
└── .brain/ingested.log
```

Toda página lleva frontmatter `type / scope / updated / fuentes / proyecto-origen` y se
enlaza con `[[wikilinks]]` — misma disciplina que la wiki de proyecto.

## 4. Cómo se alimenta (automático, desde el plugin)

| Quién | Cuándo | Qué escribe en el brain |
|---|---|---|
| **release-manager** | al entregar un pase | `releases/{fecha}-{ambiente}-{tema}.md` + actualiza `ambientes/{ambiente}.md` (componente → versión) + `componentes/*.md` (versión por ambiente) |
| **tech-writer** | en `/dev-team:wiki ingest` | detecta lo que es TRANSVERSAL (lección, ADR org, runbook, estándar nuevo) y lo **promueve** a `inbox/` del brain con su fuente |
| **QA / PO** | bug con causa sistémica (no puntual) | `incidentes/` vía inbox |
| **architect** | al cerrar `/new-project` u `/onboard` | ficha en `proyectos/` + componentes nuevos en el catálogo |
| **cybersec** | hallazgo que aplica a más de un repo | `estandares/seguridad-checklist.md` vía inbox |
| **hook SessionStart** | al abrir sesión | `git pull --ff-only` del brain a `~/.claude/faast-brain/` (caché local, fail-silent) |

Regla: los agentes escriben SOLO en `inbox/` (append, nunca editan páginas canónicas).
El tech-writer cura `inbox/` → páginas canónicas en su ciclo (`/dev-team:brain curate`).
Los `estandares/` y `decisiones/` requieren PR aprobado por el owner (CODEOWNERS).

## 5. Cómo se consume

**Agentes** — se agrega un escalón al "contexto bajo demanda":
1. Handoff trae el contexto → trabajar
2. Wiki del proyecto (`.coordination/wiki/`)
3. **Brain** (`~/.claude/faast-brain/`) — para estándares, catálogo, estado de ambientes, lecciones
4. Preguntar al usuario

**Personas** — tres puertas:
- **Obsidian**: abrir `faast-brain/` como vault → graph view de toda la organización.
- **`/dev-team:brain query "¿qué versión de MS BACKOFFICE está en Demo PE?"`** — responde
  citando páginas; si no sabe, lo dice.
- **Sitio estático** (opcional, fase posterior): MkDocs/Obsidian Publish para que Mesa de
  Servicio o gerencia consulten sin herramientas.

**Onboarding**: `/dev-team:onboard` y `/new-project` leen primero `estandares/` y
`componentes/` — un proyecto nuevo nace ya alineado.

## 6. El cambio arquitectónico más valioso: estándares FUERA del plugin

Hoy el formato de pases, las reglas SQL y el estándar Docker viven en los `.md` de los
agentes (por eso el dba pesa 5.7k tokens). Con el brain:

- Los estándares viven en `faast-brain/estandares/` — **una sola fuente**, editable con
  un PR, sin publicar versión del plugin.
- Los agentes los leen **bajo demanda** solo cuando la tarea lo requiere (el
  release-manager lee `pases-formato.md` al armar un pase; el dba lee `scripts-sql.md`
  al preparar scripts) → prompts más livianos, arranque más rápido, menos tokens.
- El plugin conserva un **resumen mínimo embebido** como fallback (si no hay red o
  brain, sigue funcionando con las reglas actuales).

## 7. Gobernanza

| Aspecto | Regla |
|---|---|
| Fuente de verdad | El brain, para lo transversal; la wiki local, para lo del proyecto. Ante conflicto, gana la realidad y se corrige la página |
| Quién escribe canónico | Solo tech-writer (curación) · `estandares/` y `decisiones/` solo vía PR aprobado por owner |
| Secretos | Prohibidos (mismo check que la wiki + gitleaks en CI del brain) |
| Idioma | Español; glosario para términos técnicos |
| Retención | Nada se borra: `releases/` e `incidentes/` son historial permanente |
| Calidad | `/dev-team:brain lint`: links rotos, huérfanos, `ambientes/` sin actualizar tras un pase, inbox con >7 días sin curar |

## 8. Plan de implementación (Fase 5)

| Paso | Contenido | Esfuerzo |
|---|---|---|
| 5.1 | Crear `faast-brain` con esquema, estructura, CODEOWNERS y CI de lint/gitleaks. Sembrarlo con lo que YA existe: el estándar Docker (`Arquitectura Docker/.coordination/wiki/estandares/`), los 17 ADRs, las lecciones que hoy viven en los agentes, y el estado actual de ambientes reconstruido desde los correos de pase | 1 sesión |
| 5.2 | Plugin: hook de sync al abrir sesión, comando `/dev-team:brain` (init/sync/query/curate/lint), escalón "brain" en contexto bajo demanda, config `brain.repo` | ½ sesión |
| 5.3 | Alimentación automática: release-manager escribe releases + estado de ambientes; tech-writer promueve en cada ingest; architect registra proyectos/componentes | ½ sesión |
| 5.4 | Mover estándares del plugin al brain con fallback embebido (dieta de agentes) | 1 sesión |
| 5.5 | (Opcional) sitio estático para consulta sin herramientas | ½ sesión |

## 9. Riesgos y mitigaciones

- **Brain desactualizado** → lint semanal + `ambientes/` se actualiza en cada pase automáticamente.
- **Ruido en inbox** → curación obligatoria en el flujo diario del Lead (`brain curate` junto a `wiki ingest`).
- **Dependencia de red** → caché local + fallback embebido en los agentes.
- **Fuga de datos** → sin secretos, sin PII, repo privado de la org, CODEOWNERS.
