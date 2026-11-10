---
description: Punto de entrada unico del equipo. Detecta si hay proyecto configurado y te guia - crear proyecto nuevo, heredar uno existente, o continuar trabajando. Si no sabes que comando usar, usa este.
argument-hint: (opcional) que quieres hacer, en tus palabras
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Start: ¿Que hacemos hoy?

Pedido del usuario (puede venir vacio): $ARGUMENTS

Este comando existe para que NADIE tenga que memorizar los demas comandos.
Detecta el contexto y guia al usuario al flujo correcto.

## Como le hablas a la persona (siempre)
Quien escribe puede no ser tecnico. **Un mensaje, un proposito** (informar, preguntar o pedir
permiso; nunca todo junto). Abre con 1-2 frases en llano sobre que paso o que haras, sin
archivos, comandos, puertos ni siglas. **Las preguntas van aparte, al final, bajo "Necesito de
ti"**: maximo 3 (ideal 1), respondibles con una palabra, con opciones y tu recomendacion; usa la
herramienta de preguntas con opciones si existe. **No preguntes lo que puedes averiguar o
decidir**: los valores tecnicos los eliges tu y lo dices en una linea. **Haz en vez de
describir**: instalas y ejecutas, y cuentas el resultado en una linea. Un mensaje cabe en una
pantalla. Lo que reporten los agentes lo traduces a este formato antes de mostrarlo. **Esto es para el chat:** los
informes, los comentarios en el ticket con evidencia y los documentos conservan todo su detalle.

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

## Paso 1: Detectar contexto (resolucion CANONICA)

Resolver la coordinacion del proyecto en este orden, subiendo desde el directorio
actual (hasta ~8 niveles):
1. **Registro del usuario** `~/.claude/dev-team.config.json` → `proyectos` (ruta del repo →
   carpeta del proyecto) o, en proyectos viejos, el puntero `.coordination-root`: la
   coordinacion es `{carpeta}/.coordination` → proyecto activo → Paso 3. (El hook de sesion ya
   indica la ruta canonica absoluta; usala.)
2. **`.coordination/` CON `config.json`** → es la canonica → proyecto activo → Paso 3
3. **`.coordination/` SIN `config.json`** → es un DESVIO (huerfana): NO la uses
   como coordinacion. Pregunta al usuario donde esta la canonica (carpeta
   paraguas); con su OK registrala en `~/.claude/dev-team.config.json` → `proyectos`
   (nada dentro del repo), fusiona lo util del desvio en la canonica y
   eliminalo. Luego continua al Paso 3 con la canonica.
4. **Nada de lo anterior** → no hay proyecto configurado → Paso 2

NUNCA escribas handoffs/metricas/evidencia en una .coordination sin config.json.

## Paso 2: Sin proyecto — ofrecer 2 caminos

Preguntar al usuario (con AskUserQuestion si esta disponible):

> ¿Que quieres hacer?
> 1. **Crear un proyecto nuevo** desde una idea o documento de requerimientos
>    → ejecutar el flujo de `/dev-team:new-project`
> 2. **Heredar un proyecto existente** (repos en GitHub/Azure o carpeta local)
>    → ejecutar el flujo de `/dev-team:onboard`

En AMBOS casos, lo primero que hace el flujo elegido es invocar al agente `setup`
para validar/instalar prerequisitos. El usuario no necesita saberlo: simplemente
funciona.

## Paso 2.5: Adoptar el protocolo del equipo (SIEMPRE que haya proyecto)
Si NO tienes ya en contexto el bloque `<dev-team-protocolo-sesion-principal>`
(pasa cuando la sesion se abrio fuera de la carpeta del proyecto), cargalo ahora:
```bash
node "${CLAUDE_PLUGIN_ROOT}/hooks/run.mjs" session_context.py --proyecto "{ruta-del-proyecto-detectado}"
```
Adopta TODA su salida como reglas vigentes de esta sesion (plan primero, gates,
delegacion, etc.) y aplica lo que indique el bloque de mantenimiento si aparece.

## Paso 3: Proyecto activo — resumen + siguiente accion

1. Leer `.coordination/config.json`, `backlog.md`, `sprint-actual.md` y handoffs pendientes
2. Mostrar un resumen de 5 lineas maximo:
   ```
   Proyecto: {nombre} ({topologia}, tracker: {github|azure})
   Sprint: {n} tareas en curso, {n} bloqueadas
   Handoffs sin procesar: {n}
   Ultimo sync con tracker: {fecha}
   ```
3. Interpretar $ARGUMENTS si el usuario pidio algo especifico:
   - "quiero una nueva funcionalidad / HU / feature" → flujo de `/dev-team:refine` (PO)
   - "hay un bug" / "esto falla" / "me paso que..." → `/dev-team:bug {descripcion}`: QA lo
     REPRODUCE con evidencia y emite veredicto ANTES de registrarlo o triagearlo
   - "probar / validar / testear" → agente QA (`/dev-team:e2e` o `/dev-team:test-plan`)
   - "diseñar / pantalla nueva / rediseño / logo / identidad / animacion / 3D / video de
     producto / como se veria" → equipo de diseño (`/dev-team:design {pedido}`)
   - "documentar (tecnico: README, API, diagramas)" → tech-writer (`/dev-team:document`)
   - "documento de negocio / PDF o Word de una HU / especificacion / acta de aceptacion / informe de sprint" →
     PO (`/dev-team:doc {hu|especificacion|sprint|aceptacion} {ref}`)
   - "registrar / grabar / automatizar un flujo / proceso paso a paso / correr el flujo de {X}" →
     `/dev-team:flow {crear|grabar|ejecutar} {dominio}/{flujo}`
   - "probar en local / desplegar / ver que hay en el servidor" → `/dev-team:deploy {sub}` (o `/dev-team:deploy-check`)
   - "revisar seguridad / pentest / hackeo etico" → `/dev-team:security-audit` o `/dev-team:pentest {alcance}`
   - "urgente / se cayo produccion / hotfix" → `/dev-team:hotfix {incidente}` (rapido, con gates intactos)
   - "como venimos hoy / standup / que hizo cada uno" → `/dev-team:standup`
   - "retrospectiva / que mejorar del sprint" → `/dev-team:retro`
   - "que aprendimos / recuerda que / de ahora en adelante / no vuelvas a" →
     `/dev-team:memoria {buscar|aprender|consolidar}`
   - "los agentes se bloquean / piden permiso / modo automatico" → `/dev-team:setup permisos`
   - "no se / que sigue" → recomendar la accion mas util segun el estado
     (handoffs pendientes → /inbox; HUs sin asignar → /assign-task; nada pendiente → /sync pull)
4. Ejecutar el flujo elegido directamente — no pedir al usuario que escriba otro comando

## Regla
Este comando NUNCA falla con "no entendi": siempre ofrece las opciones disponibles
con una explicacion de una linea cada una.
