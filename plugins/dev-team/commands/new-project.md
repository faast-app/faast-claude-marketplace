---
description: Crea un proyecto nuevo desde una idea o documento de requerimientos. Valida prerequisitos, diseña la arquitectura (mono o multi-repo), crea repos con scaffolding y genera el backlog de HUs en GitHub o Azure DevOps.
argument-hint: Ruta al documento de requerimientos (.docx, .pdf, .md) o descripcion en texto libre
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Crear nuevo proyecto

Recibiste un documento o descripcion de requerimientos: $ARGUMENTS

Ejecuta el siguiente flujo paso a paso:

## Paso 0: Prerequisitos (agente setup)
Invocar al agente `setup` para validar lo basico: git, Docker, Node y — apenas el
usuario elija tracker (Paso 4) — gh o az autenticado. Si falta algo, el setup lo
instala con confirmacion. NO continuar con herramientas criticas faltantes.

## Paso 1: Leer y analizar requerimientos
- Si $ARGUMENTS es una ruta a un archivo (.docx, .pdf, .md, .txt), leelo completo
- Si es texto libre, usalo directamente como requerimientos
- Extrae: requerimientos funcionales, no funcionales, actores, flujos, integraciones

## Paso 2: Invocar al Arquitecto
Usa el agente `architect` para analizar los requerimientos y generar la propuesta.
El Arquitecto debe producir `architecture.md` con:
- **Topologia recomendada: mono-repo o multi-repo** (con justificacion)
- Bounded contexts identificados
- Servicios propuestos (nombre, stack, patron, BD, justificacion)
- API Gateway (tecnologia y justificacion)
- Frontend (SPA vs microfrontends)
- Comunicacion entre servicios
- Diagrama Mermaid
- Repos/carpetas a crear (segun topologia)
- Plan de ejecucion por fases

## Paso 3: Presentar propuesta al usuario
Muestra la propuesta completa y pregunta:
- "Aprobado" → continuar al paso 4
- Ajustes ("prefiero mono-repo", "quita el servicio X") → el Arquitecto modifica y re-presenta

## Paso 4: Configurar proyecto y tracker
Preguntar al usuario (en UNA sola interaccion):
- Nombre del proyecto (ej: ecommerce)
- Directorio base (default: ~/projects/)
- Tracker: **GitHub** (Issues + Projects) o **Azure DevOps** (Boards) — y la org/organizacion
- ¿Crear repos remotos? (GitHub/Azure Repos, o solo local)

Validar con el agente `setup` que el CLI del tracker elegido esta autenticado.

## Paso 5: Crear estructura del proyecto

Escribir `.coordination/config.json` — la fuente de verdad para todos los agentes:
```json
{
  "project": "{nombre}",
  "topology": "mono|multi",
  "tracker": {
    "provider": "github|azure",
    "github": { "org": "{org}", "project": "{nombre-project}" },
    "azure": { "organization": "https://dev.azure.com/{org}", "project": "{nombre}" }
  },
  "urls": { "dev": "http://localhost:{puerto-frontend}" }
}
```

**Topologia MULTI** — carpeta paraguas:
```
{directorio}/{proyecto}/
├── .coordination/  (config.json, handoffs/+archive/, backlog.md, sprint-actual.md, architecture.md, test-plans/, wiki/, metrics/, evidence/)
├── docker-compose.dev.yml
├── .env.dev
├── {proyecto}-{servicio}/     ← git init por servicio (scaffolding segun stack desde templates/)
└── {proyecto}-e2e/            ← repo de la suite Playwright de QA
```

**Topologia MONO** — un solo repo:
```
{directorio}/{proyecto}/       ← git init (unico)
├── .coordination/  (igual que multi; dba-access.json y setup-status.json en .gitignore)
├── src/
│   ├── services/{servicio}/   ← scaffolding segun stack
│   ├── gateway/
│   └── frontend/
├── e2e/                       ← suite Playwright de QA
├── docs/
├── docker-compose.dev.yml
└── .github/workflows/         ← CI con paths-filter por carpeta
```

Por cada repo/carpeta: estructura segun stack (usar `templates/` del plugin),
Dockerfile, CI/CD, CLAUDE.md con contexto del servicio, .env.example, README basico,
commit inicial. Si hay remoto: `gh repo create` / `az repos create` + push.

## Paso 6: Backlog inicial (agente product-owner)
Invocar al agente `product-owner` para:
1. Convertir los requerimientos + fases del Arquitecto en HUs de negocio con
   criterios de aceptacion
2. Crear las HUs en el tracker elegido (issues/PBIs reales)
3. Generar `.coordination/backlog.md` espejo con los IDs reales

## Paso 7: Wiki y metricas
1. Ejecutar `/dev-team:wiki init` (tech-writer): crea `.coordination/wiki/` con el
   esquema del plugin e ingiere `architecture.md` y el backlog inicial
2. Crear `.coordination/metrics/` (los agentes registran ahi `activity.jsonl`)
3. Sugerir: abrir `.coordination/wiki/` como vault en Obsidian (graph view) y
   `/dev-team:team-office` para ver al equipo trabajando en vivo

## Paso 8: Resumen final
Mostrar:
- Topologia y repos/carpetas creados (locales y/o remotos)
- Tracker configurado y N HUs creadas
- Estado del entorno (del setup)
- Proximo paso: "Ejecuta /dev-team:assign-task para empezar a asignar trabajo,
  o /dev-team:start cuando no sepas que sigue"
