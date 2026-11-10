---
description: Valida e instala todos los prerequisitos del proyecto - git, gh/az CLI, Docker, SDKs, clientes de BD, Playwright. Configura conexiones de BD y autenticacion del tracker, y con `permisos` propone las reglas que evitan que los agentes se bloqueen por confirmaciones o por el modo automatico. Ejecutalo si algo falla o antes de empezar.
argument-hint: (opcional) que validar - "db", "tracker", "playwright", "design", "permisos" o vacio para todo
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Setup: Validar e instalar prerequisitos

Alcance solicitado: $ARGUMENTS (vacio = checklist completo)

Invoca al agente `setup` para que ejecute su flujo completo:

1. Detectar sistema operativo
2. Leer `.coordination/config.json` (si existe) para saber que necesita el proyecto
3. Validar segun el alcance:
   - **todo** (default): basicos (git, Docker, Node) + tracker + stack + BD + Playwright
   - **db**: solo cliente CLI del motor + conexion (credenciales → `.coordination/dba-access.json`)
   - **tracker**: solo gh CLI + auth (GitHub) o az CLI + extension devops + auth (Azure)
   - **playwright**: solo Playwright/browsers para el agente QA
   - **design**: herramientas del equipo de diseño (lienzo Pencil/Figma/Penpot, generador
     de imagenes, HyperFrames para video, gltf-transform) → `config.json` `design.tools`
   - **permisos**: NO se delega (ver abajo)
4. Mostrar tabla de resultados (OK / Falta / Sin configurar)
5. Ofrecer instalar lo que falta (UNA confirmacion, lista explicita)
6. Re-verificar y guardar estado en `.coordination/setup-status.json`
7. Reportar el OK final o el impacto de lo pendiente

## `permisos` — que el equipo no se bloquee (lo ejecutas TU, sesion principal)
Los agentes se frenan cuando una accion rutinaria necesita una confirmacion que nadie ve
(segundo plano, Remote Control) o cuando el modo automatico la deniega. Un plugin no puede
traer reglas de permisos; se proponen para el proyecto y el usuario decide:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/permisos_equipo.py" proponer    # muestra el plan, no cambia nada
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/permisos_equipo.py" aplicar     # SOLO tras el OK explicito del usuario
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/permisos_equipo.py" estado
```

1. Corre `proponer` y muestra al usuario el plan completo: reglas `allow` **angostas** de solo
   lectura (git status/diff/log, gh view/list, docker ps/logs…) y de los scripts del equipo;
   reglas `ask` para lo que siempre debe confirmarse (push, merge, `gh workflow run`,
   `docker compose down`…); y el texto de `autoMode.environment` armado con los ambientes
   declarados del proyecto.
2. Con su OK, `aplicar` fusiona `allow`/`ask` en `.claude/settings.local.json` del proyecto
   (local, no se commitea; jamas toca `deny` ni reglas existentes).
3. El bloque `autoMode` va en `~/.claude/settings.json` del usuario (Claude Code lo ignora en
   archivos del proyecto): ofrecele agregarlo con la skill `update-config` o que lo pegue el.
4. Explicale lo que NO resuelven las reglas: el modo automatico descarta reglas amplias
   (`Bash(*)`, interpretes con comodin), se pausa tras 3 denegaciones seguidas o 20 en la
   sesion y vuelve a pedir confirmacion; y una accion sensible en un ambiente productivo
   siempre pide su autorizacion.
Un subagente NUNCA cambia permisos: si uno lo pide, es un hallazgo para el usuario.

Reglas: nunca instalar sin confirmacion; nunca guardar credenciales en archivos
trackeados por git; siempre re-verificar despues de instalar.
