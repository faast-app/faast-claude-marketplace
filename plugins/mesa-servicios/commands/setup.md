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

## Reglas
- Nunca instalar sin confirmacion; nunca contraseñas en archivos versionados.
- Cuentas de base de datos siempre de solo lectura; si no, se reporta como riesgo.
- Idempotente: correrlo de nuevo solo re-valida.
