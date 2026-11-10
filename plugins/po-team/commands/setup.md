---
description: Valida e instala lo que el equipo del PO necesita - git, GitHub CLI con scopes project y read:project (o Azure CLI con Boards), Playwright MCP y su navegador, LibreOffice para PDF y Word, python3 - con una confirmacion, y configura el tracker preguntando una sola vez organizacion, repos, Projects, campos, mapeo de estados a etapas del ciclo de pase, ambientes, clientes, capacidad y repo de evidencia en .po-team/config.json. Ejecutalo al empezar o si algo falla. Uso - /po-team:setup [todo|tracker|playwright|documentos|ambientes]
argument-hint: '[todo | tracker | playwright | documentos | ambientes]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica, SIEMPRE con su nombre completo `po-team:{agente}`
> (dev-team y mesa-servicios tambien tienen un agente `setup`: sin prefijo se puede invocar el
> de otro equipo). Al invocar: ruta ABSOLUTA de `.po-team/`, "Pedido del usuario (textual): ..."
> y, si el usuario aprobo un plan, "Autorizacion del usuario: {plan literal}".

# Setup: que nada falle por herramientas o configuracion

Alcance: $ARGUMENTS (por defecto `todo`)

Invocar al agente `po-team:setup` (modelo `haiku`, fijo) con el alcance. El flujo del agente:
1. Detecta el sistema operativo.
2. Checklist del alcance y tabla (herramienta · estado · accion):
   - **tracker**: `gh auth status` + scopes `project`/`read:project` + acceso a repos y Projects
     (`gh project list`, `gh project field-list`), o `az` con la extension de Boards.
   - **playwright**: MCP del plugin visible (`claude mcp list`), `npx playwright install chromium`,
     `.po-team/accesos.env` con los NOMBRES de variables de cuentas por ambiente.
   - **documentos**: `soffice` + prueba real de conversion con acentos.
   - **ambientes**: URLs, variables de cuentas y **clase** (`pruebas` | `productivo`, la declara el
     PO; nunca se deduce del nombre) de Desa, QA, Demo por pais y Preprod por cliente; cuales
     reciben pases en lote.
3. "¿Instalo lo que falta?" con la lista exacta, UNA sola vez. Como el setup corre como subagente
   y no puede esperar: devuelve la lista con `esperando_usuario`; ESTA sesion pregunta al usuario
   y lo re-invoca con "Autorizacion del usuario: instalar {lista}" (o con lo que el usuario
   excluya); instala, re-verifica y sigue.
4. Si no existe `.po-team/config.json`, lo crea desde
   `${CLAUDE_PLUGIN_ROOT}/templates/po-team/config.json` con UNA ronda de preguntas (equipo, PO,
   tracker, Projects y campos leidos del tracker real, mapeo de estados a etapas y estados solo
   de QA, ambientes, clientes, capacidad, repo de evidencia, prefijo de ambiente en bugs).
5. Guarda `.po-team/setup-status.json`, deja `.po-team/` en la carpeta del proyecto (nunca en un repo) y da el OK o lista lo pendiente con
   su impacto.

## Paso 0 — Entorno (solo si el equipo no cargo; funciona en cualquier terminal y sistema)
Si en el contexto de esta sesion **no aparece** el bloque de protocolo de este equipo, o aparece
"ENTORNO INCOMPLETO", los hooks del plugin no pudieron correr. Necesitan **Node.js** y
**Python 3** — no bash: sirven PowerShell, cmd, Windows Terminal, Git Bash, zsh o bash. Arreglalo
TU antes de seguir, sin pedirle al usuario que lo haga a mano:
1. Comprueba que hay: `node --version` y `python --version` (si falla: `python3 --version`,
   y en Windows tambien `py -3 --version`). En Windows, un `python` que abre la Microsoft Store
   o no imprime version **no** es Python: cuenta como ausente.
2. Dile al usuario en UNA linea que falta y que lo vas a instalar, e instala lo que falte:

   | Sistema | Python 3 | Node.js |
   |---|---|---|
   | Windows | `winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements` | `winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements` |
   | macOS | `brew install python@3.12` | `brew install node` |
   | Debian / Ubuntu | `sudo apt-get update && sudo apt-get install -y python3` | `sudo apt-get install -y nodejs npm` |
   | Fedora / RHEL | `sudo dnf install -y python3` | `sudo dnf install -y nodejs` |

   Sin `winget` (Windows antiguo) o sin `brew` (macOS): usa el instalador oficial de
   python.org / nodejs.org y guia al usuario en ese unico paso. Si la instalacion pide
   confirmacion de Claude Code o del sistema, es normal: el usuario la aprueba una vez.
3. Verifica de nuevo las versiones. En Windows el PATH nuevo solo lo ve una terminal nueva:
   pide al usuario **cerrar y volver a abrir** la terminal y la sesion. Al reabrir, el equipo
   carga completo (protocolo, pendientes, memoria).
4. Mientras tanto NO te detengas: sigue con el pedido en modo reducido y dilo. Para cargar el
   protocolo sin reiniciar: `node "${CLAUDE_PLUGIN_ROOT}/hooks/run.mjs" session_context.py`.
En Windows los procedimientos que digan `python3 archivo.py` se ejecutan como `python archivo.py`.

## Reglas
- Nunca instalar sin confirmacion; nunca contraseñas ni tokens en archivos versionados.
- Nada hardcodeado: todo valor sale de las respuestas o de lo que se lee del tracker.
- Idempotente: correrlo de nuevo solo re-valida y completa.
