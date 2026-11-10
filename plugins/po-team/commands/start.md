---
description: Punto de entrada unico del equipo del Product Owner. Detecta si po-team esta configurado y te guia - configurar por primera vez, refinar lo que llego de la Mesa de Servicios, planificar el sprint, ver el tablero, validar tickets, generar un documento o un manual. Interpreta lo que pides en tus palabras y te lleva al flujo correcto. Si no sabes que comando usar, usa este.
argument-hint: (opcional) que quieres hacer, en tus palabras
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica, SIEMPRE con su nombre completo `po-team:{agente}`
> (dev-team y mesa-servicios tambien tienen un agente `setup`: sin prefijo se puede invocar el
> de otro equipo). Al invocar: ruta ABSOLUTA de `.po-team/`, "Pedido del usuario (textual): ..."
> y, si el usuario aprobo un plan, "Autorizacion del usuario: {plan literal}".

# Start: ¿que hacemos hoy con el backlog?

Pedido (puede venir vacio): $ARGUMENTS

Este comando existe para que NADIE tenga que memorizar los demas. Detecta el contexto y lleva al
flujo correcto. **Nunca responde "no entendi"**: si el pedido es ambiguo, ofrece las 3 opciones
mas probables con una linea cada una y, si no elige, recomienda la mas util.

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

## Paso 1 — Detectar contexto
Resolver la carpeta canonica con `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/coord_root.py" "$PWD"`
(registro `~/.claude/po-team.config.json`, puntero `.po-team-root` y subida de directorios,
prefiriendo una `.po-team/` fuera de cualquier repo). Si el hook de sesion ya imprimio la ruta
absoluta, usar esa:
- **No existe** → po-team no esta configurado → Paso 2.
- **Existe** → leerlo junto con el ultimo `.po-team/tablero/tablero-datos.json` (si existe) y el
  `.po-team/sprints/*.json` mas reciente → Paso 3.

## Paso 2 — Sin configurar
Explicar en 2 lineas que hace el equipo y invocar al agente `po-team:setup` (alcance `todo`): valida e
instala con una confirmacion y crea `.po-team/config.json` preguntando UNA vez organizacion,
repos, Projects, mapeo de estados a etapas, ambientes, clientes, capacidad y repo de evidencia.
Al terminar, mostrar como seguir: `/po-team:tablero` para ver el estado o `/po-team:refinar`
para lo que llego de la Mesa.

## Paso 2.5 — Protocolo del equipo
Si no esta en contexto el bloque `<po-team-protocolo>` (sesion abierta fuera de la carpeta),
cargarlo: `node "${CLAUDE_PLUGIN_ROOT}/hooks/run.mjs" session_context.py --proyecto "{ruta}"` y adoptar
su salida (plan primero, gates, delegacion, nada hardcodeado).

## Paso 3 — Configurado: resumen + siguiente accion
Mostrar maximo 5 lineas (del ultimo tablero; si tiene mas de 24 h, decirlo):
```
{equipo} · tablero al {fecha}
Sprint {N}: {pts} pts · VB cliente {x}% · observados {n} · bloqueados {n}
Proximo hito: {Demo|Preprod|VB} {fecha} {⚠ si esta en riesgo}
Pendiente: {n} tickets de la Mesa sin refinar · {n} sin estimar
```
Interpretar $ARGUMENTS:
- "llego de la mesa / nuevo requerimiento / HU / historia / bug / redactar / estimar / refinar" → `/po-team:refinar …`
- "sprint / planificar / capacidad / que entra / fechas de pase / replanificar" → `/po-team:sprint …`
- "tablero / dashboard / como vamos / avance / informe diario / semanal / publicar" → `/po-team:tablero …`
  (sin decir cual, el tablero pregunta: generico, Organizacion PO o validaciones)
- "crear / armar un backlog o tablero nuevo en GitHub / no tengo Project" → `/po-team:tablero crear-backlog`
- "validar / VB PO / probar rapido / revisar en demo / preprod / lote" → `/po-team:validar …`
- "me reportaron un error / falla / no funciona X / registrar un bug" (sin reproducir) →
  `/po-team:validar --reproducir "…"` (solo con REPRODUCIDO se registra el bug)
- "ya lo arreglaron / revalidar / volver a probar el #n" → `/po-team:validar --revalidar #n`
- "cerrar el sprint / review / retro / como nos fue" → `/po-team:sprint cierre {N}`
- "documento / pdf / word / acta / aceptacion / especificacion / informe de sprint" → `/po-team:documento …`
- "manual / instructivo / paso a paso para usuarios / para QA" → `/po-team:manual …`
- "estado / que hay pendiente / que sigue" (rapido, sin regenerar) → `/po-team:estado`
- "configurar / no funciona gh / falta soffice / navegador / ambiente nuevo" → `/po-team:setup …`
- Vacio o "no se / que sigue" → recomendar lo mas util en este orden: pendientes que esperan
  respuesta (los lista el hook de sesion) → fechas vencidas o en riesgo → observados sin devolver
  → arreglos sin revalidar → tickets de la Mesa sin refinar → sprint sin planificar → tickets en
  Demo sin VB PO → sprint terminado sin cierre → tablero de mas de 24 h.
Ejecutar el flujo elegido directamente, sin pedir que escriba otro comando.
