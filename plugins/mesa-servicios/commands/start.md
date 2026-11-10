---
description: Punto de entrada unico de la Mesa de Servicios. Detecta si la mesa esta configurada y te guia - configurar por primera vez, recibir algo nuevo de un cliente, seguir una solicitud en curso, o ver el estado. Si no sabes que comando usar, usa este.
argument-hint: (opcional) que quieres hacer, en tus palabras
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Start: ¿que hacemos hoy en la Mesa?

Pedido (puede venir vacio): $ARGUMENTS

Este comando existe para que NADIE tenga que memorizar los demas. Detecta el contexto y lleva al
flujo correcto. Nunca responde "no entendi": siempre ofrece las opciones con una linea cada una.

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
Buscar `.mesa/config.json` subiendo desde el directorio actual (hasta 8 niveles):
- **No existe** → la Mesa no esta configurada → Paso 2.
- **Existe** → leerlo junto con `.mesa/backlog.md` y los `estado.json` de `.mesa/solicitudes/*/` → Paso 3.

## Paso 2 — Sin configurar
Invocar al agente `setup`: crea `.mesa/config.json` preguntando UNA vez lo minimo (tracker y
Project, clientes, productos, brain, repo de evidencia, ambientes), valida e instala con
confirmacion, y deja `setup-status.json`. Luego ofrecer `/mesa-servicios:brain init` si el brain
no existe. Terminar mostrando como recibir la primera solicitud.

## Paso 3 — Mesa activa: resumen + siguiente accion
Mostrar maximo 5 lineas:
```
Mesa: {n} solicitudes en curso · {n} esperando cliente · {n} pendientes de aprobacion comercial
Ultimas: {ID} ({estado}), {ID} ({estado})
Brain: {n} paginas · ultimo ingest {fecha}
```
Interpretar $ARGUMENTS:
- "me llego / recibi / el cliente mando / correo / reunion / audio / adjunto" → `/mesa-servicios:recibir`
- "preguntas / cerrar / que falta / respondio el cliente" → `/mesa-servicios:analizar {ID}`
- "reproducir / el cliente dice que falla / evidencia" → `/mesa-servicios:reproducir {ID}`
- "maqueta / como se veria / prototipo / pantalla" → `/mesa-servicios:prototipo {ID}`
- "script / revertir / corregir datos / consulta a la base" → `/mesa-servicios:sql …`
- "flujo / siempre hago esto / buscar operaciones / registrar como lo hago" → `/mesa-servicios:flujo {crear|grabar|ejecutar} …`
- "documento / propuesta / pdf / word" → `/mesa-servicios:documento {ID}`
- "ticket / subir al backlog / registrar" → `/mesa-servicios:ticket {ID}`
- "que sabemos de / el negocio / el cliente X" → `/mesa-servicios:brain query …`
- "como vamos / estado / pendientes" → `/mesa-servicios:estado`
- "no se / que sigue" → recomendar lo mas util (solicitudes esperando respuesta → analizar;
  documentadas sin ticket → ticket; cerradas sin brain → brain ingest)
Ejecutar el flujo elegido directamente, sin pedir que escriba otro comando.

## Paso 3.5 — Protocolo de la Mesa
Si no esta en contexto el bloque `<mesa-servicios-protocolo>` (sesion abierta fuera de la carpeta),
cargarlo: `node "${CLAUDE_PLUGIN_ROOT}/hooks/run.mjs" session_context.py --proyecto "{ruta}"` y adoptar
su salida (plan primero, la persona de mesa habla con el cliente, cero escritura del DBA, etc.).
