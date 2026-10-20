---
description: Valida e instala lo que el equipo del PO necesita - git, GitHub CLI con scopes project y read:project (o Azure CLI con Boards), Playwright MCP y su navegador, LibreOffice para PDF y Word, python3 - con una confirmacion, y configura el tracker preguntando una sola vez organizacion, repos, Projects, campos, mapeo de estados a etapas del ciclo de pase, ambientes, clientes, capacidad y repo de evidencia en .po-team/config.json. Ejecutalo al empezar o si algo falla. Uso - /po-team:setup [todo|tracker|playwright|documentos|ambientes]
argument-hint: '[todo | tracker | playwright | documentos | ambientes]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Setup: que nada falle por herramientas o configuracion

Alcance: $ARGUMENTS (por defecto `todo`)

Invocar al agente `setup` (modelo `haiku`, fijo) con el alcance. El flujo del agente:
1. Detecta el sistema operativo.
2. Checklist del alcance y tabla (herramienta · estado · accion):
   - **tracker**: `gh auth status` + scopes `project`/`read:project` + acceso a repos y Projects
     (`gh project list`, `gh project field-list`), o `az` con la extension de Boards.
   - **playwright**: MCP del plugin visible (`claude mcp list`), `npx playwright install chromium`,
     `.po-team/accesos.env` con los NOMBRES de variables de cuentas por ambiente.
   - **documentos**: `soffice` + prueba real de conversion con acentos.
   - **ambientes**: URLs y variables de Desa, QA, Demo por pais y Preprod por cliente; cuales
     reciben pases en lote.
3. Pregunta UNA sola vez "¿Instalo lo que falta?" con la lista exacta; instala; re-verifica.
4. Si no existe `.po-team/config.json`, lo crea desde
   `${CLAUDE_PLUGIN_ROOT}/templates/po-team/config.json` con UNA ronda de preguntas (equipo, PO,
   tracker, Projects y campos leidos del tracker real, mapeo de estados a etapas y estados solo
   de QA, ambientes, clientes, capacidad, repo de evidencia, prefijo de ambiente en bugs).
5. Guarda `.po-team/setup-status.json`, deja `.po-team/` en la carpeta del proyecto (nunca en un repo) y da el OK o lista lo pendiente con
   su impacto.

## Reglas
- Nunca instalar sin confirmacion; nunca contraseñas ni tokens en archivos versionados.
- Nada hardcodeado: todo valor sale de las respuestas o de lo que se lee del tracker.
- Idempotente: correrlo de nuevo solo re-valida y completa.
