---
description: Valida e instala todo lo que la Mesa necesita - GitHub/Azure autenticado con acceso al Project, transcripcion local (ffmpeg + Whisper), lectura de documentos (pandoc), PDF y Word (LibreOffice), Playwright MCP, clientes de base de datos en SOLO LECTURA, faast-brain y repo de evidencia, conectores de correo/Teams si existen - con una confirmacion. Crea y completa .mesa/config.json y los archivos de acceso gitignored. En modo nube verifica conectores. Ejecutalo al iniciar la Mesa o si algo falla. Uso - /mesa-servicios:setup [todo|tracker|fuentes|documentos|playwright|db|brain|nube]
argument-hint: '[todo | tracker | fuentes | documentos | playwright | db | brain | nube]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Setup: que nada falle por herramientas o credenciales

Alcance: $ARGUMENTS (por defecto `todo`)

Invocar al agente `setup` con el alcance. El flujo del agente:
1. Detecta sistema operativo y modo (local / nube).
2. Si no existe `.mesa/config.json`, lo crea desde `templates/mesa/config.json` preguntando UNA
   vez lo minimo: tracker (GitHub o Azure) y org/repo/Project/columna, clientes (codigo y
   nombre), productos, ruta del brain, repo de evidencia, ambientes con sus URLs.
3. Ejecuta el checklist del alcance y muestra la tabla (herramienta · estado · accion):
   - **tracker**: `gh auth status` + scope `project` + acceso a repo, Project y etiquetas (o `az`).
   - **fuentes**: `ffmpeg`, `whisper` (o `faster-whisper`; aviso del tamaño del modelo), `pandoc`;
     conectores de correo/Teams en `claude mcp list` (opcionales).
   - **documentos**: `soffice` + prueba real de conversion con acentos.
   - **playwright**: un solo MCP `playwright` activo, `npx playwright install chromium`,
     `.mesa/accesos.env` con cuentas de prueba por nombre de variable.
   - **db**: `mysql` / `sqlcmd`; por conexion, prueba `SELECT 1` y **verificacion de que la
     cuenta NO escribe**; `.mesa/db-access.json` con `solo_lectura: true`.
   - **brain**: repo en `brain.path` (si no, ofrecer `/mesa-servicios:brain init`); remoto opcional.
   - **nube**: conectores necesarios presentes; advertir limitaciones (transcripcion de archivos
     grandes, bases en red privada) y dejarlas en `setup-status.json`.
4. Pregunta UNA sola vez "¿Instalo lo que falta?" con la lista exacta; instala; re-verifica;
   avisa si hay que reiniciar.
5. Guarda `.mesa/setup-status.json` y asegura el `.gitignore` (`accesos.env`, `db-access.json`,
   `setup-status.json`, `evidencia/`, archivos de audio/video).
6. Da el OK ("Mesa lista") o lista lo pendiente con su impacto.

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
- Nunca instalar sin confirmacion; nunca contraseñas en archivos versionados.
- Cuentas de base de datos siempre de solo lectura; si no, se reporta como riesgo.
- Idempotente: correrlo de nuevo solo re-valida.
